# Auto critique: laço automático entre Claude e dsh

O laço leva a resposta do Claude ao dsh e a resposta do dsh de volta ao Claude, sem ação manual. O Claude responde na sessão do app Claude desktop, pelo mod. O dsh é acionado pela API local do dsh. Cada mensagem que cruza a fronteira passa pelo gate (`gate.py`) antes de seguir.

Este documento descreve o estado atual e serve para retomar o trabalho em uma nova sessão.

## Estado atual (para retomar)

- **Transporte:** fechado nos dois sentidos. O teste `start 2` fez 2 chamadas ao Claude e 2 ao dsh, como previsto, e parou pelo limite de envios.
- **Gate:** C1 a C5 ligados nos dois sentidos. C6, C7 e C8 foram suspensas, porque as regras ainda são suposição. Ver a seção "Gate".
- **Contrato:** o texto está no `CLAUDE.md`, na seção "Contrato entre harnesses (CRITIQUE)". O mod também o envia junto de cada mensagem.
- **Confirmado:** a resposta final do dsh aparece na sessão do app, logo abaixo da linha de fim, pela `$.ui.log`.
- **Não commitado:** há alterações no working tree. Antes de commitar, confira o `git status`.

## Como ligar e desligar

Comandos, digitados na sessão do app:

- `/auto_critique chat <id>`: define o chat do dsh desta sessão, pelo id `session-…`. Fica no estado da sessão e vale até `/clear`, `/resume` ou `/branch`. Só funciona com o laço parado. Sem chat definido, `start` recusa e não envia nada.
- `/auto_critique start N <seu prompt>`: inicia o laço com até N envios ao dsh. O texto depois do número é o prompt de partida, enviado ao Claude como a semente.
- `/auto_critique stop`: interrompe o laço no ponto em que estiver.
- `/auto_critique status`: mostra se o laço está rodando, a fase, os envios feitos e o chat em uso.
- `/auto_critique chats [filtro]`: lista os chats do dsh com id e título, filtrando pelo título. É só leitura: não envia mensagem e não chama o Claude.

Durante a execução, não digite nada na sessão. O laço para sozinho ao atingir N envios, e a linha de fim aparece na sessão.

## Como o laço anda

1. `/auto_critique start N <prompt>` envia a semente ao Claude. A semente leva o contrato e os dados da rodada: brief, sha256 atual e alvo, lidos do estado pelo `gate.py contexto`.
2. Quando o Claude termina o turno, o hook `turn.complete` pega a resposta e a manda ao gate (`claude-para-dsh`).
   - Aceita: a resposta vai ao dsh pelo `dsh_step.py send`, com o contrato e os dados da rodada.
   - Recusa ou estaciona: o motivo volta ao Claude como nova mensagem. Não conta como envio.
3. O temporizador de 3 segundos consulta o dsh (`dsh_step.py read`) até a resposta aparecer. A resposta é a última mensagem de texto do dsh antes do `turn/end` do turno.
4. Se o envio atingiu N, a resposta do dsh aparece na sessão, e o laço para com a linha de limite.
5. Caso contrário, a resposta passa pelo gate (`dsh-para-claude`).
   - Aceita: vira um prompt da sessão, com o contrato e os dados da rodada.
   - Recusa: o motivo volta ao dsh como nova mensagem. Não conta como envio.

Regras que o mod impõe:

- Durante o laço, o Claude não pode usar ferramentas. O hook `tool.call` nega qualquer ferramenta nessa fase.
- Só o turno pedido pelo próprio laço segue ao dsh.
- O laço para em qualquer um destes casos, sempre com uma linha de motivo na sessão e no log:
  - limite de envios atingido;
  - parada manual;
  - 3 recusas seguidas do Claude, ou 3 do dsh, pelo gate;
  - 3 minutos sem resposta do dsh (60 ticks de 3 segundos);
  - C3 sem nó aberto (`encerra`);
  - erro no temporizador ou no envio.

A espera pelo Claude não tem timeout.

## Gate

O `gate.py` roda como processo, chamado pelo `register.ts`. Ele lê o `estado.json` e o histórico, roda as checagens e registra o veredito.

| Check | O que confere | Se falhar |
|---|---|---|
| C1 | Bloco `<<<MSG ... MSG>>>`, campos na ordem da seção 3, linha `---`, `tipo` válido | recusa |
| C2 | Brief do envelope é o do estado, e o sha256 bate com o arquivo | recusa |
| C3 | `alvo` é o primeiro nó aberto. Sem nó aberto, encerra a rodada | estaciona, ou encerra |
| C4 | Um único pedido (no máximo um `?`) | recusa |
| C5 | Crítica cita critério existente no nó; pergunta não cita critério (`-`) | estaciona ou recusa |

**Suspensas:** C6 (material existe), C7 (declaração de estado) e C8 (orçamento e convergência). As regras delas são suposição, e voltam ao desenho depois de testes reais.

**Fail-closed:** sem `estado.json`, ou em qualquer erro de leitura, o gate recusa.

**Registros:**

- `docs/critique/rodadas.jsonl`: uma linha por mensagem checada, com o veredito.
- `docs/critique/estacionados.jsonl`: itens estacionados. Ainda não existe, porque nada foi estacionado.
- O registro mistura execuções antigas com as atuais. Antes de um teste limpo, mova o arquivo para `docs/critique/arquivo-teste/`, com carimbo de data.

**Estado da rodada:** `tools/auto_critique/estado.json`. Versionado no git. Hoje é um placeholder: brief `docs/ingest.md`, um nó `N0` aberto, e a chave `_aviso` que marca o conteúdo como placeholder. A regra de escrita exclusiva do Markim foi revogada. O campo `materiais` existe, mas o gate não o usa.

## Onde ficam os arquivos

- `tools/auto_critique/mod/`: o mod. É a fonte de verdade.
  - `.claude-plugin/plugin.json`: manifesto. Aponta para `types/index.d.ts`.
  - `types/index.d.ts`: contrato do estado (`auto_critique.chat`).
  - `hooks/register.ts`: os hooks do comando e o laço.
  - `dsh_step.py`: a ponte até a API do dsh.
  - `gate.py`: as checagens, a CLI `check` e a `contexto`.
  - `test_gate.py`: a suíte do gate.
  - `answer.txt`, `resposta_claude.txt`, `resposta_dsh.txt`: arquivos temporários do laço, ignorados pelo `.gitignore` do mod.
- `~/.claude/settings.json`: a variável `CLAUDE_CODE_PLUGIN_DIRS` aponta para `tools/auto_critique/mod`. Ela é lida ao abrir a sessão, então depois de mudar é preciso reiniciar o Claude Code.
- `mod/dsh_api.py`: a API local do dsh (autenticação, RPC, histórico e envio).
- `docs/proposta_gate_critique.md`: a proposta, com as decisões D1 a D5.
- `tools/auto_critique/runtime/`: arquivos de execução, não versionados e ignorados pelo git. A pasta é criada pelos scripts quando falta.
  - `dsh_token.txt`: token de lançamento do `dsh web`, permissão 600.
  - `jar.txt`: cookie de sessão obtido com o token.
  - `app_last_sent.txt`: a última mensagem enviada ao dsh, para a leitura casar a resposta.
  - `laco_mod.log`: o log do laço.

## Como testar

Antes de testar, confirme três coisas:

1. O Claude Code foi reiniciado depois de qualquer mudança no `register.ts`. O gate (`gate.py`) não precisa de reinício, porque roda como processo a cada chamada.
2. O `dsh web` está de pé, e o token em `dsh_token.txt` é o atual.
3. O chat desta sessão está definido com `/auto_critique chat`.

Previsão de chamadas, já observadas:

| Teste | Previsto | Observado |
|---|---|---|
| `start 1` | 1 Claude e 1 dsh | 1 Claude e 1 dsh |
| `start 2` | 2 Claude e 2 dsh | 2 Claude e 2 dsh |

Antes de cada teste com API, declare o número de chamadas. Depois, reconcilie com o log.

Para conferir sem gastar API:

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_gate` na pasta do mod. Resultado esperado: 30 testes OK.
- `claude plugin validate <pasta do mod>`. Resultado esperado: passa, com dois avisos já conhecidos (nome do plugin não é kebab-case, e falta o autor).
- `python3 -I gate.py contexto` na pasta do mod. Resultado esperado: `ok: true`, com o brief, o sha256 e o alvo.

## Credenciais

- O token de lançamento do `dsh web` muda a cada reinício. Para usar o laço, grave o token novo em `dsh_token.txt` e renove o cookie, o que o mod faz a partir dele. Grave o arquivo com `printf`, sem passar o token pelo chat:

```bash
printf '%s' 'COLE_O_TOKEN_AQUI' > /Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/runtime/dsh_token.txt && chmod 600 /Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/runtime/dsh_token.txt
```

- Um reinício do `dsh web` invalidou o cookie anterior, mesmo que a documentação do dsh diga que o segredo do cookie persiste. Depois de reiniciar, o token precisa ser gravado de novo.
- Ao reiniciar, a porta 3080 pode continuar ocupada pelo processo anterior. Nesse caso, o token novo não é aceito, e é preciso encerrar o processo antigo antes de subir o novo.
- O cookie, segundo a documentação do dsh, dura 30 dias. Não verifiquei se sobrevive a um reinício do `dsh web`.
- O servidor do dsh escuta só em `127.0.0.1:3080`, e a API exige sessão de navegador.
- Se o token aparecer no chat, trate como exposto e troque ao reiniciar.

## Medições que sustentam a escolha

Os tempos são do trecho que você definiu: da resposta disponível num harness até o envio no outro.

| Caminho | Trecho | Mediana | Faixa | Amostra |
|---|---|---|---|---|
| Interface do dsh (Chrome, clipboard) | entrada no dsh | 26 s | 2,5 a 37 s | 19 |
| Interface do Claude desktop | entrada no Claude | 53 s | 7 a 77 s | 18 |
| API do dsh | entrada no dsh | 0,03 a 0,04 s | — | 6 |
| API do dsh | leitura da resposta | 0,2 a 0,4 s | — | 6 |

- A API eliminou clipboard, foco, busca de campo, Cmd+V, botão Copy e Return. A resposta completa sai pelo `session/page`.
- Os tempos de processamento do dsh e do Claude não entram nessa métrica.

## Pontos em aberto

- **Conteúdo do gate:** C6, C7 e C8 suspensas. As regras voltam depois de testes reais.
- **Conteúdo do contrato:** o envelope depende de o Claude copiar o sha256 e o alvo. Os dados chegam pelo prefixo, mas o argumento e a escolha do critério são juízo, e não são checados.
- **Respostas do dsh:** o dsh tem repetido o texto do Claude quase palavra por palavra. Isso é conteúdo, e fica para a etapa de camadas.
- **Verificação de afirmações:** durante o laço, as ferramentas são negadas. Isso impede o Claude de conferir o que afirma, e o modo CRITIQUE pede essa verificação. Precisa de decisão de desenho.
- **Premissa P4 da proposta:** diz que o Markim escreve a árvore. Ainda não foi removida, porque a regra foi revogada só no `estado.json`.
- **Camada 1 no dsh:** o dsh deve ler o `CLAUDE.md` pelo workspace da sessão. Não confirmei o workspace do chat de teste.
- **Registro misturado:** `rodadas.jsonl` tem linhas de execuções antigas. Arquive antes de um teste limpo.
- **Espera pelo Claude:** não tem timeout. Se o turno do Claude travar, o laço fica parado até o `stop`.
- **Cookie após reinício:** não verificado.
- **Respostas longas:** não testadas, nem mais de duas rodadas.

## Próximos passos

1. Arquivar o `docs/critique/rodadas.jsonl` antes de um teste limpo.
2. Decidir sobre a premissa P4 e sobre a verificação de afirmações com ferramentas negadas.
3. Depois de implementado o transporte, refinar o conteúdo de cada camada e voltar às regras suspensas, com testes reais.
