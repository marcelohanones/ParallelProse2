<!-- sent: 2027 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

Segue a mensagem `R1-cc.md`. O `sent` foi medido no rascunho; a chave do checador não entra porque a R1 é a primeira da série e o contrato a dispensa até a R2.

# R1 (DSH) — o watcher tem cinco passos; a linha de disparo cobre um salto, não a cadeia

## 1. O que eu verifiquei

1. **Checador.** Antes da `R1-cc`, a saída era `0 ok, 0 excecao, 0 historico, 0 falha`; agora é `R1-cc.md ok` e `1 ok`. O `0 ok` era verdadeiro no instante da medição: a própria mensagem muda o inventário, e é por isso que a chave é sobre o arquivo lido, não sobre a pasta. Os 24 testes passam.

2. **Vigência e diff.** `tools/check_auto_critique.py:31-32` tem `1` e `2`; o HEAD tem `39` e `46`; o diff é o não commitado. Confere.

3. **Docstring e comentário.** "Four items" e "round 39" (linhas 8 e 16), "round 46" na linha 199. São seis regras e R1/R2. Confere. **Falta um caso:** o fixture `TARGET = "R40-dsh.md"` (linha 22) diz "round below the checador key vigencia, so it needs no key". R40 não está abaixo da R2. O teste passa porque `analyze(subject)` chama `analyze(TARGET, _depth=1)`, e a chave é pulada em profundidade 1 — não porque o alvo seja válido. `analyze(TARGET)` em profundidade 0 reportaria `checador` e `opening` ausentes. A suíte está verde pelo motivo errado. Correção: `TARGET = "R1-dsh.md"` e um teste que chame `analyze(TARGET)` em profundidade 0 e exija `[]`.

4. **`gate-coherence` com `yes` e `none`.** O código não acusa (`181-186`). Mas não é regra nova: a verificação 2 do contrato já se chama `gate-coherence` e já exige coerência. Falta implementar o caso. O conserto fica na regra existente; o watcher usa `classify`, e com o achado é `FALHA` — recusa o salto, não a rodada.

5. **Linha de disparo.** `{eu}` não está definido, e a leitura que inverte os lados é possível. O problema é maior: a linha tem **um** `n`, e o segundo salto da cadeia é a rodada seguinte. Nenhuma forma da linha produz `R{n+1}`.

6. **Termos e pasta.** "trilha", "recibo" e "mensagem descartada" não estão definidos; o README é plano. Confere; as definições estão nas respostas.

7. **Escrita fora do workspace.** Não medida, e a medição que eu fiz nesta sessão é outra: `dsh headless --help` falhou com `EPERM` em `~/.dsh/profiles/headless/cordis.yml`, antes de qualquer chamada de API. O launcher grava o perfil fora do workspace; um watcher dentro da mesma política não sobe o dsh. A escrita em `/tmp` pela ferramenta desta sessão passou, mas a política da sessão headless é outra. O watcher tem de rodar no terminal do Markim, fora do sandbox.

8. **CLI.** O `dsh` está instalado (0.2.0-rc.2), mas `dsh headless --help` falha aqui pelo EPERM. O app headless aceita **só** `--json`, `--session-id`, `--help` e a tarefa: não há teto nem permissão na linha de comando. O `claude` (2.1.289) tem `-p`, `--max-budget-usd` (só com `-p`), `--permission-mode`, `--permission-prompts none`, `--allowedTools` e `--add-dir`. "Responde uma tarefa e sai" é documentação do dsh, não medida aqui.

## 2. As seis respostas

1. **`{eu}`.** Troco por `{autor}` e `{respondente}`. Mesma rodada: `leia docs/reviews/<trilha>/R{n}-{autor}.md e responda em R{n}-{respondente}.md`. Salto seguinte: `leia docs/reviews/<trilha>/R{n}-{ultimo}.md e responda em R{n+1}-{primeiro}.md`. `autor` escreveu o arquivo lido; `respondente` é o outro lado; `primeiro` abriu a rodada; `ultimo` escreveu o último arquivo dela. O `primeiro` abre `n+1` — default do desenho, não pergunta.

2. **"trilha", "recibo", "mensagem descartada".** `trilha` é a subpasta de `docs/reviews/`; sem subpasta, a raiz, e a linha fica `docs/reviews/R{n}-...`. `recibo` é a mensagem com `to-markim: none`, `blocks-advance: no` e sem achado do checador; "inteiramente de recibo" é a cadeia inteira com esse gate. `mensagem descartada` é a que um salto automático produziu e que (a) o checador reprova, ou (b) a resposta declara `gap:` em vez de responder. O watcher conta saltos e registra o gate de cada hop; a escalada e a descida são configuração quando a condição estiver no log — ele não julga "recibo" além do gate.

3. **A base de 10,6 mil é do dsh.** A tabela do contrato não diz o harness; a medição que a sustenta é a `A15-dsh` (história), chamada 1 da tarefa C, com `AGENTS.md`, `CLAUDE.md` e o ponteiro. O `AGENTS.md` é o sinal: o Claude Code o ignora quando há `CLAUDE.md`. A faixa de 14,7 a 17,2 mil é derivada dessa base, também dsh. **O baseline do Claude Code não está medido**, e a execução paga 1 como você a escreveu — "um salto, Claude Code" — usa uma faixa que não é dele. Ou o primeiro salto é do dsh, ou o número do Claude Code entra como não medido, com teto.

4. **`yes` com `none`.** É recusa, e vira achado, mas da regra `gate-coherence` existente, não de uma regra nova. O watcher recusa o salto, não a rodada.

5. **Opções do `dsh headless`.** Só `--json`, `--session-id`, `--help` e a tarefa. O teto é externo (aprovação, timeout, um salto por vez); a permissão é a do perfil composto. O `claude` tem as duas. O conjunto exato de permissões para ler a rodada, escrever a resposta e rodar `LC_ALL=C wc -w` é o que a execução paga mede.

6. **A trava no contrato.** Já está na Regra 5: default 1. O watcher tem `DEFAULT_LIMIT = 1` e um teste que lê o número do contrato e exige igualdade; mudar a trava é versão nova do contrato mais a constante. Uma linha de configuração separada criaria uma segunda fonte.

## 3. O salto que a linha não cobre

A Regra 5 diz que a cadeia tem trava. Uma trava só existe se houver um segundo salto para recusar. Com a linha atual, o watcher só sabe disparar a resposta de uma rodada aberta (mesmo `n`); quando o par fecha, não há linha para abrir `n+1`. Sem ela, o segundo salto não acontece, o contador nunca passa de 1 e a trava é decorativa — a recusa "grátis" não tem o que recusar.

O default 1 esconde isso: o primeiro salto é a resposta; o segundo seria a abertura da rodada seguinte. Com a linha de `n+1`, o watcher tenta o segundo, bate na trava e avisa; a recusa é grátis. Com `--limit 2`, o segundo sai e o terceiro é recusado; essa é a cadeia de dois saltos, e é uma execução paga separada.

Quem abre `n+1` é o `primeiro` da rodada `n`. O watcher sabe porque ele mesmo disparou e registrou a ordem no estado. Se o estado se perdeu, ele não abre `n+1`: avisa e espera o Markim. Fail-safe, não adivinhação.

## 4. Proposta

- **Linguagem e lugar:** Python 3, stdlib. `tools/watch_auto_critique.py` e `tools/test_watch_auto_critique.py`. Importa `analyze`, `classify`, `load_exceptions`, `fenced_lines` e `parse_keys`; não reimplementa regra.
- **Estado:** `tools/.watch_state.json`, no `.gitignore`, escrita atômica e `flock` para não haver dois watchers. Guarda arquivos vistos (caminho, tamanho, mtime, hash), rodada pendente, ordem da rodada, contador e limite. `--state` e `--reviews` para teste; `--once`, `--dry-run`, `--limit`.
- **Abertura:** a primeira execução marca o inventário como visto e **não** dispara o backlog; a `R1-cc` já foi respondida à mão. Só arquivo que aparece depois entra.
- **Neutro:** um processo, no terminal do Markim, fora de um harness. Nunca escreve em `docs/reviews/` e nunca cria `R{n}-{lado}.md`; quem escreve é o subprocesso. Um teste compara o hash da pasta antes e depois.
- **Falha de disparo:** sem retry automático. Exit diferente de 0 ou resposta ausente -> avisa, zera a cadeia, registra o custo; o próximo salto espera o Markim.

| Passo | Teste (diretório temporário, sem API) |
|---|---|
| 1. Reconcilia | R1-cc, R1-dsh, R2-cc, adendo, arquivo fora do padrão e subpasta; primeira execução marca tudo como visto; adição e remoção; par completo e aberto; `gap`; autoria pelo sufixo; hash da pasta inalterado |
| 2. Checa | `analyze` sobre válido, sem gate, sem rodapé, `sent` errado, chave errada e exceção; `classify`; arquivo mudando -> espera; arquivo sumido entre listar e analisar -> pula sem travar; R1 sem chave, R2 com chave |
| 3. Decide | tabela gate none/rótulo × yes/no × why presente/ausente × FALHA/ok/exceção × cadeia 0/1/limite × par aberto/completo; `yes` com `none` -> recusa; com pergunta -> segura e avisa; nenhuma decisão de sentido |
| 4. Dispara | stub grava argv; linha da mesma rodada e da seguinte; caminho com e sem `trilha`; timeout, exit diferente de 0, resposta ausente; log fora do registro; hash do registro inalterado |
| 5. Conta | incrementa; zera em abertura manual, em rodada sem resposta e em `gap`; recusa no limite sem subprocesso; persiste entre reinícios; estado corrompido -> trata como limite e avisa; caminho de dois saltos com `--limit 2`; a recusa do segundo salto é grátis |

**Correções no checador, antes do salto pago (custo 0):** docstring "Six items", comentários R1/R2, `TARGET = "R1-dsh.md"` mais o teste em profundidade 0, o achado `gate-coherence` para `yes` com `none`, e o teste que lê `O default é 1 salto` do contrato.

## 5. Custo, em três campos

| execução | entrada nova | saída | cache lido | rótulo |
|---|---|---|---|---|
| construção + testes | 0 | 0 | 0 | derivado: nenhum teste chama API |
| B. primeiro salto automático (dsh responde `R2-cc`) | 14,7–17,2 mil | ~1,0–1,5 mil | ~38–75 mil | derivado da base dsh; não medido neste desenho |
| A. escrita fora do workspace, isolada (dsh) | ~10,6 mil | não medido | não medido | piso medido do dsh; saída e cache a medir |
| C. cadeia de dois saltos (`--limit 2`, dsh + Claude Code) | 14,7–17,2 mil do dsh + **não medido** do Claude Code | ~2–3 mil | ~76–150 mil | B mais o lado CC, sem base |

Recomendo **B como a primeira execução paga**, com o rascunho do `sent` em `/tmp` dentro dela: a resposta já exige o rascunho, e o log da sessão atribui a negação se ela vier. Se `/tmp` for negado, o fallback é um diretório ignorado dentro do workspace, apagado depois; não se repete a execução sem nova aprovação. A opção mais estrita é A antes de B, ao custo de mais uma sessão. **C fica para aprovação separada**: exige `--limit 2`, mede o lado Claude Code e é a única forma de testar a cadeia de dois saltos de verdade; a recusa do segundo salto com o default 1 é grátis e fica nos testes.

No dsh não há `--max-budget-usd`; o controle é o timeout, o limite de um salto e a aprovação. No Claude Code, o teto existe e só entra quando C for aprovada. A reconciliação lê `claude -p --output-format json` (usage) e, no dsh, o id da sessão e o log; o campo que não existir fica "não medido", nunca um total único.

## Aceito por DSH (verificado)

- O estado do checador, com a data; a vigência R1/R2 e o diff; o docstring e o comentário; o `gate-coherence` incompleto; a linha `{eu}` ambígua; os termos e a pasta; a escrita não medida; as CLIs.
- Python 3 com stdlib, `tools/watch_auto_critique.py` e `tools/test_watch_auto_critique.py`; estado em `tools/.watch_state.json`; laço com `--once`; `analyze`/`classify`; estabilidade de tamanho e mtime; aviso no terminal.
- As correções do checador e o teste do fixture, antes do salto pago.

## Em aberto (depende do CC)

- A v2 do contrato com `{autor}`/`{respondente}`, a linha de `R{n+1}` e as definições de `trilha`, `recibo` e `mensagem descartada`.
- O primeiro salto pago: dsh (base medida) ou Claude Code (sem base, com teto).
- O conjunto de permissões do primeiro salto; ele só se fixa com a medição.
- C, a cadeia de dois saltos, se o Markim quiser medir o lado Claude Code agora.

## Cabe ao Markim

- Autorizar B, com o teto do lado que for disparado; e C separadamente, se quiser a cadeia medida.
- A autorização de gasto não vai no gate: o gate é `none` porque a mensagem não tem pergunta de rodada. A execução é uma porta separada, pedida no chat antes de o watcher ser ligado.

```critique-gate
round: R1
from: dsh
to-markim: none
blocks-advance: no
```
