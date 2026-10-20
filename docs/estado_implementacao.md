## Pendências para o cenário

Para a regra "o arquivo na pasta é o start do outro harness" valer, falta isto. Os itens marcados como feitos estão implementados no `4444a10`; os demais não.

1. **Um monitor contínuo.** Hoje o watcher roda uma passada e sai. Precisa de um processo que observe `docs/reviews/` e detecte o arquivo novo sem ninguém executá-lo. Sem isso, a pasta não é start de nada.
2. **Nenhuma colagem manual.** A transição manda o Markim colar a linha de disparo. Ela deve virar recurso de emergência, fora do fluxo normal. **Decidido na R5:** não é regra nova — é consequência do item 11, e a colagem fica como emergência, como o contrato já diz.
3. **Ordem de arquivos novos.** O par que chega junto colapsa num gatilho só — o último —, e o alvo é `R{n+1}-{quem abriu}`; a ordem vem da citação "Segue a mensagem", não do nome nem do `mtime`. Processar em ordem não serve: `dispatch_line` só está correta quando o gatilho é o último arquivo da rodada, e o par processado em ordem dispara duas vezes, uma delas para o lado errado. **Feito no `4444a10`.**
4. **Um start, uma vez.** O watcher marca o arquivo e grava o estado antes do disparo, então a queda não repete o start. O `disparando` com id vai na mesma gravação, e no reinício um `disparando` sem resultado vira "salto interrompido, olhar humano", sem novo disparo. **Feito no `4444a10`.**
5. **Falha de salto com política.** A falha é terminal — o arquivo está em `seen` e a passada seguinte não repete o disparo — e o destino é durável: `tools/.watcher-hops/index.jsonl`, uma linha por salto com rodada, alvo, motivo, caminho do log, passos e previsão. O aviso nomeia a rodada e o alvo. **Feito no `4444a10`.**
6. **O `passa` vira arquivo.** Hoje o `passa` é digitado no chat. Para a automação valer, ele precisa ser um sinal que o harness detecte sozinho. **Decidido na R5:** sai. O cenário diz que o harness registra o arquivo no evento do `passa`, e o harness presente é o que o Markim fala; o T9 passa a dizer que o arquivo seguinte é escrito por ele.
7. **Permissões para rodar sozinho.** O dsh roda com `workspace-write` e aprovação `ask`, e o cc com o comando aprovado. Falta verificar num salto que começa sem nenhum humano por perto. **Decidido na R5:** sai como pendência. Os três saltos headless não mostram bloqueio de permissão, e o item 11 ganha o teste de fumaça — um salto sem humano, `workspace-write`, escrita só em `docs/reviews/`.
8. **Prontidão antes da marca.** Rascunho com o marcador espera: não entra em `seen`, não vira FALHA, e depois do prazo do P-d vira aviso. O defeito que isto corrige: um arquivo observado a meio do procedimento — cabeçalho em `0000`, contagem, `sed` — era marcado, recusado por `FALHA` e depois lido como reescrita, e a rodada morria em silêncio. **Feito no `4444a10`.**

Os itens 1, 3, 4, 5 e 8 são código do watcher, cobertos pelos itens 11, 6, 9, 8 e 5 do plano. O 2, o 6 e o 7 saíram por derivação, com a decisão escrita acima.

## Política de falha e de espera (P-a a P-e)

Vive no contrato desde a **v23**, na seção `## A política de falha`. Fechada pelos dois harnesses na R2-dsh — proposta pelo cc em `R1-cc.md:40-43`, corrigida pelo dsh em `R1-dsh.md:62-67` —, ela esteve aqui até a v23, e não se repete aqui: duas cópias da mesma regra foi o defeito do `PROCEDURE_NOTE`, e não se conserta criando outra.

A `R1-cc` guarda `1154` no lugar do marcador: o `sed` global do passo 4 o trocou em quatro trechos, e o arquivo não se edita. O P-d lê-se com o marcador, que é `0000`.

## Estado da implementação

Esta seção descreve o que existe agora. O registro de rodadas não é citado aqui: ele é transporte, pode estar vazio, e o que precisa durar mora neste documento ou no contrato.

**Arquivos**
- `tools/watcher_auto_critique.py` — o watcher. Uma passada por execução: reconcilia, checa, decide, dispara, conta. Comandos: sem argumento (passada), `--dry-run`, `--status`, `--reset` (zera o contador de relato), `--set-cc-cmd "..."`.
- `tools/check_auto_critique.py` — o checador. Seis regras: `gate-last`, `gate-coherence`, `sent`, `single-footer`, `checador`, `opening`.
- `tools/test_check_auto_critique.py` e `tools/test_watcher_auto_critique.py` — 62 testes, todos OK em `python3 -m unittest discover -s tools`.
- `tools/.watcher-state.json` — estado do watcher: arquivos vistos e contador. Ignorado pelo git.
- `tools/.watcher-hops/` — um log por salto, com a saída do processo. Ignorado pelo git.
- `docs/reviews/` — o registro. Um arquivo por lado por rodada, mais adendos. É transporte: o conteúdo é ignorado pelo git e pode ser apagado ao fim da sessão.

**Disparo**
- dsh: `dsh --profile headless --json "<linha de disparo>"`, com o trecho do procedimento anexado. Roda fora do sandbox — o perfil é gravado em `~/.dsh` antes de qualquer chamada de API.
- cc: `cc_argv` gravado no estado, com `{line}` e `{target}` substituídos. Configurado com `--permission-prompts none` e uma lista de `--allowedTools`. Sem `--max-budget-usd`.

**Cadeia e gate**
- **Não há limite.** O contador de saltos relata, e não impede disparo. `--reset` zera a contagem; não é exigência para disparar.
- Gate com `blocks-advance: yes` segura o arquivo, e o watcher não dispara. O `passa` libera o arquivo seguinte.
- Gate com `yes` e rótulo exige `why-blocking`: sem essa linha, o checador aponta.

**Medições**
- Três saltos do dsh: 404 s e 64 `tool_call`; 250 s e 35; 286 s e 33. `tool_call` não é passo de modelo: o passo é o `step_start`.
- Um deles: 62.232 tokens de entrada nova, 51.309 de saída, 1,70 milhão de cache lido — é o R15, e confere ao token.
- Sete saltos com `--json`, medidos dos `step_end` em `tools/.watcher-hops/`: 18, 45, 76, 52, 27, 65 e 27 passos, mediana 45; `tool_call` de 27 a 88. Três saltos não têm JSON nenhum (R2, R3 e R4), e os do cc também não: o lado cc não tem base, e agora está medido.
- Preset do dsh: `workspace-write` é o padrão. Não verificado: o efeito de `DSH_PERMISSION_MODE` sobre o modo efetivo.
- Permissão do cc: `Edit(docs/reviews/{target})` casou no último salto. Não verificado: `Grep`, `Glob` e as regras com padrão.

**Autorização de saltos e plano**
- **D1, respondida pelo Markim em 2026-10-20:** sem teto. O contador de saltos relata, e não impede disparo. Confirma a Regra 5 do contrato; a linha anterior, que autorizava cinco saltos com dois usados, fica retirada.
- **D4, respondida pelo Markim em 2026-10-20:** a série em curso é aposentada **depois** que a v23 entrar. A ordem é esta: a v23 no contrato, fechar a série, apagar o registro, `--new-series`, e só então o monitor. Falta um passo nessa lista, e ele vem depois do reset: com o registro vazio, ninguém tem o que citar, então o Markim pede a um lado, à mão, que escreva `R1-{lado}.md`. Esse arquivo abre a série e tem de passar o checador como qualquer outro — `sent` e gate; a chave do checador e a linha da abertura só são exigidas da R2 em diante. Com o monitor ligado não há linha de disparo a colar: o abridor é turno único, e o watcher dispara o outro lado com `rodada aberta`. A linha só serve ao caminho manual. Enquanto a ordem não se cumprir, a passada de verdade não roda — ela toma a linha de base no meio da série.
- **D2, respondida em 2026-10-20:** a concordância do Markim com o plano vem depois da revisão do dsh, e não antes. **D3 foi retirada** pelo dsh: era um bloqueio sem default, e o plano executa zero chamadas de API.
- **O plano dos doze itens** está aceito pelos dois harnesses, com as correções dos itens 5, 6 e 9 e os refinamentos dos itens 1 e 3. O Markim deu o `passa` em 2026-10-20.
- **O item 1 está feito:** contrato na v23, com a reconciliação como passo 6 do watcher, a previsão sem base, o comando do passo 4 preso às duas chaves do `sent` e a política de falha dentro dele.

**Pendente, com quem**
- **Markim:** a lista de capacidades liberadas para o salto do dsh — o que ele pode ler, escrever e executar. A recomendação medida é manter `workspace-write` para escrita e auditar leitura e shell no watcher sem bloquear.
- **Código do watcher:** o monitor está escrito (item 11 do plano) e **não rodou contra um salto real**. O estado real ainda é o da série anterior, e `--new-series` não foi rodado: a adoção exige aposentar a série em curso, porque o registro nunca está vazio enquanto a troca vive.
- **Git:** o `README.md` da raiz é um arquivo vazio versionado.

**Comandos úteis**
- `python3 tools/check_auto_critique.py` — confere o registro inteiro.
- `python3 -m unittest discover -s tools` — suíte completa. Rode com a saída guardada, `> /tmp/suite.log 2>&1`, e só depois olhe o resumo: filtrar até `OK`/`FAILED` foi o que apagou o nome do teste que falhou em 2026-10-20, e é por isso que aquela falha segue sem explicação.
- `python3 tools/watcher_auto_critique.py --status` — contador e últimos avisos.
- `python3 tools/watcher_auto_critique.py --dry-run` — mostra o que dispararia, sem gravar nada.
- Uma passada que dispara um salto demora de 4 a 8 minutos: rode em segundo plano.
