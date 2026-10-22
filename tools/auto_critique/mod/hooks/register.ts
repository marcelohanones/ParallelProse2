import type { Register } from 'claude-code'

// Laço nesta sessão: o Claude responde por esta conversa e o dsh é acionado pela API via dsh_step.py.
// Ciclo: semente -> turno do Claude -> resposta vai ao dsh -> dsh responde -> prompt volta ao Claude -> ...
const MOD_DIR = '/Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/mod'
const HELPER = `${MOD_DIR}/dsh_step.py`
const ANSWER_FILE = `${MOD_DIR}/answer.txt`
const SEED = 'Responda com uma frase curta sobre o laço entre Claude e dsh. Responda só com o texto, sem status.'
const TICK_MS = 3000
// Tempo máximo esperando a resposta do dsh: 60 ticks de 3 s, ou 3 minutos, como na versão anterior da ponte.
const MAX_ESPERA_TICKS = 60
// Gate mecânico (gate.py): confere o envelope antes de cada mensagem sair. Recusas seguidas param o laço (proposta, seção 6.6).
const GATE = `${MOD_DIR}/gate.py`
const RESPOSTA_CLAUDE = `${MOD_DIR}/resposta_claude.txt`
const RESPOSTA_DSH = `${MOD_DIR}/resposta_dsh.txt`
const MAX_RECUSAS = 3

// Contrato do modo CRITIQUE (CLAUDE.md, seção "Contrato entre harnesses"). Vai junto de cada mensagem nos dois sentidos.
const CONTRATO = [
  'Modo CRITIQUE. Cada mensagem entre harnesses começa com o envelope definido em `docs/proposta_gate_critique.md`, seção 3.',
  'Trabalhe só no nó indicado em `alvo`. Melhoria só entra na rodada se citar um `criterio` existente.',
  'Não altere o brief nem o arquivo de estado da rodada.',
  'Entregue a resposta entre `<<<MSG` e `MSG>>>`, sem texto fora dos marcadores.',
].join('\n') + '\n\n'

// Estado do laço. Só valores simples aqui; $ aparece sempre no corpo de cada hook.
let running = false
let phase: 'idle' | 'seed_pending' | 'await_claude' | 'await_dsh' | 'devolver_claude' = 'idle'
let sent = 0
let maxRounds = 0
let seedText = SEED
let chatId = ''
let esperaTicks = 0
let recusas = 0
let recusasDsh = 0
let pendente = ''
let timer: { cancel(): void } | undefined

// Para o laço e devolve a linha de fim, para ser mostrada na sessão e registrada no log.
function parar(motivo: string): string {
  running = false
  phase = 'idle'
  timer?.cancel()
  timer = undefined
  return `laço parado: ${motivo}`
}

// Prefixo de cada mensagem aos harnesses: contrato mais os dados da rodada (brief, sha256 e alvo),
// lidos do estado a cada turno. Sem o sha256, o Claude não tem como acertar o envelope: não tem ferramentas no laço.
// Se o estado não puder ser lido, o prefixo diz isso, e o gate recusa a mensagem.
async function contratoDaRodada($: any): Promise<string> {
  const out = JSON.parse((await $.process.run(['python3', '-I', GATE, 'contexto'])).stdout)
  if (!out.ok) return CONTRATO + `Dados desta rodada indisponíveis: ${out.error}\n\n`
  return CONTRATO + `Dados desta rodada:\nbrief: ${out.brief} sha256:${out.sha256}\nalvo: ${out.alvo}\n\n`
}

export const register: Register = (on, options) => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'auto_critique',
      description: 'Laço com o dsh pela API',
      argumentHint: 'chat <id> | start N <prompt> | chats [filtro] | stop | status',
    })
    return next(e)
  })

  // Enquanto o laço roda, o turno do Claude é só texto: nenhuma ferramenta.
  on('tool.call', async ($, e, next) => {
    if (running) return { deny: 'laço ativo: a resposta deve ser só texto, sem ferramentas' }
    return next(e)
  })

  on('command.run', { command: 'auto_critique' }, async ($, e, next) => {
    const parts = e.args.trim().split(/\s+/)
    const [cmd, n] = parts

    // Chat do dsh: fica no estado da sessão e vale até /clear, /resume ou /branch.
    if (cmd === 'chat') {
      if (running) return { text: 'pare o laço antes de trocar o chat' }
      const id = n ?? ''
      if (!id.startsWith('session-')) return { text: "erro: o id do chat começa com 'session-'" }
      await $.state.set({ plugin: 'auto_critique', key: 'chat' }, id)
      return { text: `chat definido para esta sessão: ${id}` }
    }

    if (cmd === 'chats') {
      const out = await $.process.run(['python3', '-I', HELPER, 'chats', n ?? ''])
      return { text: out.stdout || out.stderr }
    }

    if (cmd === 'start') {
      if (running) return { text: 'o laço já está rodando' }
      const { value: chat = '' } = await $.state.get({ plugin: 'auto_critique', key: 'chat' })
      if (!chat) return { text: 'defina o chat desta sessão com /auto_critique chat <id>' }
      chatId = chat
      maxRounds = Number(n ?? 1) || 1
      // O texto depois do número é o prompt de partida; sem texto, usa a semente fixa.
      const rest = parts.slice(2).join(' ')
      seedText = rest || SEED
      running = true
      sent = 0
      esperaTicks = 0
      recusas = 0
      recusasDsh = 0
      phase = 'seed_pending'
      // O temporizador envia a semente e, depois, cada resposta do dsh.
      timer = $.clock.every(TICK_MS, async () => {
        if (!running) return
        try {
          if (phase === 'devolver_claude') {
            // Devolução do gate: o motivo volta ao Claude como prompt, sem contar como rodada.
            phase = 'await_claude'
            $.prompt.submit({ text: pendente }).catch(async (err: unknown) => {
              const msg = parar(`erro ao devolver ao Claude: ${String(err)}`)
              $.ui.log(msg)
              await $.process.run(['python3', '-I', HELPER, 'log', msg])
            })
            return
          }
          if (phase === 'seed_pending') {
            phase = 'await_claude'
            await $.process.run(['python3', '-I', HELPER, 'log', 'semente enviada ao Claude'])
            $.prompt.submit({ text: (await contratoDaRodada($)) + seedText }).catch(async (err: unknown) => {
              const msg = parar(`erro ao submeter a semente: ${String(err)}`)
              $.ui.log(msg)
              await $.process.run(['python3', '-I', HELPER, 'log', msg])
            })
            return
          }
          if (phase !== 'await_dsh') return
          esperaTicks += 1
          const out = JSON.parse((await $.process.run(['python3', '-I', HELPER, 'read', chatId])).stdout)
          if (!out.reply) {
            if (esperaTicks >= MAX_ESPERA_TICKS) {
              const msg = parar(`o dsh não respondeu em ${(MAX_ESPERA_TICKS * TICK_MS) / 1000} s`)
              $.ui.log(msg)
              await $.process.run(['python3', '-I', HELPER, 'log', msg])
            }
            return
          }
          await $.process.run(['python3', '-I', HELPER, 'log', `dsh respondeu (${out.reply.length} caracteres), envios=${sent}/${maxRounds}`])
          if (sent >= maxRounds) {
            // Última resposta do dsh: não volta ao Claude, então aparece na sessão como linha de transcrição.
            $.ui.log(`resposta do dsh:\n${out.reply}`)
            const msg = parar(`limite de envios atingido (${sent}/${maxRounds})`)
            $.ui.log(msg)
            await $.process.run(['python3', '-I', HELPER, 'log', msg])
            return
          }
          // Gate, dsh -> Claude: a resposta do dsh precisa do envelope antes de voltar ao Claude.
          await $.fs.write(RESPOSTA_DSH, out.reply)
          const gate = JSON.parse((await $.process.run(['python3', '-I', GATE, 'check', RESPOSTA_DSH, '--direcao', 'dsh-para-claude'])).stdout)
          if (gate.resultado === 'encerra') {
            const msg = parar(`gate encerrou a rodada (${gate.check}): ${gate.motivo}`)
            $.ui.log(msg)
            await $.process.run(['python3', '-I', HELPER, 'log', msg])
            return
          }
          if (gate.resultado !== 'aceita') {
            recusasDsh += 1
            await $.process.run(['python3', '-I', HELPER, 'log', `gate (dsh): ${gate.resultado} (${gate.check}): ${gate.motivo}`])
            if (recusasDsh >= MAX_RECUSAS) {
              const msg = parar(`${MAX_RECUSAS} recusas seguidas do dsh pelo gate (${gate.check}): ${gate.motivo}`)
              $.ui.log(msg)
              await $.process.run(['python3', '-I', HELPER, 'log', msg])
              return
            }
            // Devolução ao dsh: vai como nova mensagem ao chat, não conta como envio nem como rodada.
            await $.fs.write(ANSWER_FILE, (await contratoDaRodada($)) + `O gate devolveu a sua resposta anterior (${gate.check}): ${gate.motivo}. Refaça a resposta com o envelope completo.`)
            const devolucao = JSON.parse((await $.process.run(['python3', '-I', HELPER, 'send', ANSWER_FILE, chatId])).stdout)
            if (!devolucao.ok) {
              const msg = parar(`falha na devolução ao dsh: ${devolucao.error}`)
              $.ui.log(msg)
              await $.process.run(['python3', '-I', HELPER, 'log', msg])
              return
            }
            esperaTicks = 0
            return
          }
          recusasDsh = 0
          phase = 'await_claude'
          $.prompt.submit({ text: (await contratoDaRodada($)) + out.reply }).catch(async (err: unknown) => {
            const msg = parar(`erro ao submeter resposta do dsh: ${String(err)}`)
            $.ui.log(msg)
            await $.process.run(['python3', '-I', HELPER, 'log', msg])
          })
        } catch (err) {
          const msg = parar(`erro no temporizador: ${String(err)}`)
          $.ui.log(msg)
          await $.process.run(['python3', '-I', HELPER, 'log', msg])
        }
      })
      return { text: `laço iniciado: até ${maxRounds} envios ao dsh (chat ${chatId})` }
    }

    if (cmd === 'stop') {
      const msg = parar('parada manual')
      $.ui.log(msg)
      await $.process.run(['python3', '-I', HELPER, 'log', msg])
      return { text: 'laço parado' }
    }

    const { value: chat = '' } = await $.state.get({ plugin: 'auto_critique', key: 'chat' })
    return { text: `rodando=${running} fase=${phase} envios=${sent}/${maxRounds} chat=${chat || '(não definido)'}` }
  })

  // Só o turno que o próprio laço pediu segue ao dsh.
  on('turn.complete', async ($, e, next) => {
    try {
    if (running && phase === 'await_claude') {
      if (!e.answer) {
        const msg = parar('resposta vazia do Claude')
        $.ui.log(msg)
        await $.process.run(['python3', '-I', HELPER, 'log', msg])
      } else {
        // Gate, Claude -> dsh: a resposta precisa do envelope antes de seguir.
        await $.fs.write(RESPOSTA_CLAUDE, e.answer)
        const gate = JSON.parse((await $.process.run(['python3', '-I', GATE, 'check', RESPOSTA_CLAUDE])).stdout)
        if (gate.resultado === 'encerra') {
          const msg = parar(`gate encerrou a rodada (${gate.check}): ${gate.motivo}`)
          $.ui.log(msg)
          await $.process.run(['python3', '-I', HELPER, 'log', msg])
          return next(e)
        }
        if (gate.resultado !== 'aceita') {
          recusas += 1
          await $.process.run(['python3', '-I', HELPER, 'log', `gate: ${gate.resultado} (${gate.check}): ${gate.motivo}`])
          if (recusas >= MAX_RECUSAS) {
            const msg = parar(`${MAX_RECUSAS} recusas seguidas pelo gate (${gate.check}): ${gate.motivo}`)
            $.ui.log(msg)
            await $.process.run(['python3', '-I', HELPER, 'log', msg])
          } else {
            pendente = (await contratoDaRodada($)) + `O gate devolveu a resposta anterior (${gate.check}): ${gate.motivo}. Refaça a resposta com o envelope completo.`
            phase = 'devolver_claude'
          }
          return next(e)
        }
        recusas = 0
        // Primeiro envio: o dsh recebe também o prompt de partida, para ter o contexto da conversa.
        // O contrato vai junto ao dsh, para o lado dsh receber as mesmas regras (veículo A).
        const corpo = sent === 0 ? `Pergunta: ${seedText}\n\nResposta: ${e.answer}` : e.answer
        const payload = (await contratoDaRodada($)) + corpo
        await $.fs.write(ANSWER_FILE, payload)
        const out = JSON.parse((await $.process.run(['python3', '-I', HELPER, 'send', ANSWER_FILE, chatId])).stdout)
        if (!out.ok) {
          const msg = parar(`falha no envio: ${out.error}`)
          $.ui.log(msg)
          await $.process.run(['python3', '-I', HELPER, 'log', msg])
        } else {
          sent += 1
          esperaTicks = 0
          phase = 'await_dsh'
        }
      }
    }
    } catch (err) {
      // Erro no caminho da resposta do Claude: o laço para com o motivo, em vez de ficar travado.
      const msg = parar(`erro na resposta do Claude: ${String(err)}`)
      $.ui.log(msg)
      try {
        await $.process.run(['python3', '-I', HELPER, 'log', msg])
      } catch {
        // sem log, a linha já foi mostrada na sessão
      }
    }
    return next(e)
  })
}
