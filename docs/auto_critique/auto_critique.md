# Auto critique: laço automático entre Claude e dsh

O laço leva a resposta final do Claude ao dsh e a resposta do dsh de volta ao Claude, sem ação manual. O Claude responde na própria sessão do app Claude desktop. O dsh é acionado pela API local.

## Como ligar e desligar

Comandos, digitados na sessão do app:

- `/auto_critique start N <seu prompt>`: inicia o laço com até N envios ao dsh. O texto depois do número é o prompt de partida, enviado ao Claude como o primeiro turno. Na primeira mensagem ao dsh, o mod envia também esse prompt, no formato `Pergunta: ... / Resposta: ...`.
- `/auto_critique stop`: interrompe o laço no ponto em que estiver.
- `/auto_critique status`: mostra se o laço está rodando, a fase e os envios feitos, como `envios=1/2`.
- `/auto_critique chat <id>`: define o chat do dsh que recebe o laço, pelo id `session-…`. Só funciona com o laço parado, e a escolha fica salva em `dsh_chat_id.txt`.
- `/auto_critique chats [nome do chat]`: para descobrir o id de um chat pelo nome. lista os chats do dsh com id e título, filtrando pelo nome quando o filtro é dado. É só leitura: não envia mensagem ao dsh e não chama o Claude.

Durante a execução, não digite nada na sessão. Qualquer turno que o laço não tenha pedido não segue ao dsh, mas pode interferir no contexto.

O laço para sozinho ao atingir N envios. Entre um laço e outro, a sessão continua normal: dá para ler os resultados e fazer perguntas ao modelo no mesmo contexto, e o próximo `/auto_critique start` retoma nessa conversa.

## Como o laço anda

1. `/auto_critique start N <prompt>` envia o prompt ao Claude, pelo temporizador de 3 segundos.
2. Quando o Claude termina o turno, o hook `turn.complete` pega a resposta final e a envia ao dsh pela API (`session/prompt`).
3. O temporizador consulta o dsh (`session/page`) até a resposta aparecer.
4. A resposta do dsh vira um novo prompt da sessão, com a instrução de responder só com o texto.
5. Ao atingir N envios, o laço para.

Regras que o mod impõe:
- Durante o laço, o Claude não pode usar ferramentas. O hook `tool.call` nega qualquer ferramenta nessa fase. Esse bloqueio ainda não foi testado com uma tentativa real.
- Só o turno pedido pelo próprio laço segue ao dsh.

## Onde ficam os arquivos

- `~/.claude/dev-mods/e3ee81ff-02f6-4c53-b65e-9258f2e36a58/auto_critique/`: o mod.
  - `.claude-plugin/plugin.json` e `hooks/hooks.json`: manifesto e registro.
  - `hooks/register.ts`: os hooks do comando `/auto_critique`.
  - `dsh_step.py`: a ponte até a API do dsh.
- `tools/auto_critique/api_loop.py`: a API do dsh, usada pela ponte. Tem a função de envio e a de leitura da resposta.
- `/private/tmp/critique_cli_work/`: arquivos de execução, não versionados.
  - `dsh_token.txt`: o token de lançamento do `dsh web`, permissão 600. Parâmetro inicial do mod.
  - `dsh_chat_id.txt`: o id do chat do dsh que recebe o laço. Parâmetro inicial, alterado por `/auto_critique chat <id>`.
  - `jar.txt`: o cookie de sessão obtido com o token.
  - `app_last_sent.txt`: a última mensagem enviada ao dsh, para a leitura casar a resposta.
  - `laco_mod.log`: o log do laço.

## Credenciais

- O token de lançamento do `dsh web` muda a cada reinício. Para usar o laço, é preciso gravar o token novo em `dsh_token.txt` e renovar o cookie, o que o mod faz a partir dele. Grave o arquivo com `printf`, sem passar o token pelo chat:

```bash
printf '%s' 'COLE_O_TOKEN_AQUI' > /private/tmp/critique_cli_work/dsh_token.txt && chmod 600 /private/tmp/critique_cli_work/dsh_token.txt
```
- Um reinício do `dsh web` invalidou o cookie anterior, mesmo que a documentação do dsh diga que o segredo do cookie persiste. Depois de reiniciar, o token precisa ser gravado de novo.
- Ao reiniciar, a porta 3080 pode continuar ocupada pelo processo anterior. Nesse caso, o token novo não é aceito, e é preciso encerrar o processo antigo antes de subir o novo.
- O cookie, segundo a documentação do dsh, dura 30 dias. Não verifiquei se sobrevive a um reinício do `dsh web`.
- Ao terminar um teste, apague `dsh_token.txt` e `jar.txt` e reinicie o `dsh web`.
- O servidor do dsh escuta só em `127.0.0.1:3080`, e a API exige sessão de navegador.

## Medições que sustentam a escolha

Os tempos são do trecho que você definiu: da resposta disponível num harness até o envio no outro.

| Caminho | Trecho | Mediana | Faixa | Amostra |
|---|---|---|---|---|
| Interface do dsh (Chrome, clipboard) | entrada no dsh | 26 s | 2,5 a 37 s | 19 |
| Interface do Claude desktop | entrada no Claude | 53 s | 7 a 77 s | 18 |
| API do dsh | entrada no dsh | 0,03 a 0,04 s | — | 6 |
| API do dsh | leitura da resposta | 0,2 a 0,4 s | — | 6 |

- A API eliminou clipboard, foco, busca de campo, Cmd+V, botão Copy e Return. A resposta completa sai pelo `session/page`.
- Na interface do Claude desktop, as esperas se concentravam em duas etapas: cerca de 10 s entre a ativação e a busca do campo, e cerca de 34 s entre a busca e o envio.
- Os tempos de processamento do dsh e do Claude não entram nessa métrica.

## Pontos em aberto

- A negação de ferramentas durante o laço não foi testada com uma tentativa real.
- A entrega do laço depende de um temporizador de 3 segundos, e esse intervalo entra no trecho medido.
- A pergunta de ativação do app não funcionou nesta sessão, e a causa não foi identificada.
- Não testamos respostas muito longas, mais de duas rodadas por laço, nem a continuidade do cookie após reiniciar o `dsh web`.
