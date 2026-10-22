# auto_critique

Mod de uso pessoal que roda um laço entre a sessão do Claude e o dsh, pela API local do dsh. Não é publicado: fica nesta máquina.

## Comandos

- `/auto_critique start N <prompt>`: inicia o laço com até N envios ao dsh. O texto depois do número é o prompt de partida. Sem texto, usa a semente fixa. Na primeira mensagem ao dsh, envia também o prompt, no formato `Pergunta: ... / Resposta: ...`.
- `/auto_critique stop`: interrompe o laço no ponto em que estiver.
- `/auto_critique status`: mostra se o laço está rodando, a fase e os envios feitos, como `envios=1/2`.
- `/auto_critique chat <id>`: define o chat do dsh que recebe o laço desta sessão, pelo id `session-…`. Fica no estado da sessão e vale até `/clear`, `/resume` ou `/branch`. Só funciona com o laço parado. Sem chat definido, `start` recusa.
- `/auto_critique chats [filtro]`: lista os chats do dsh com id e título, filtrando pelo título quando o filtro é dado. É só leitura.

Durante a execução, não digite nada na sessão.

## Arquivos

- `.claude-plugin/plugin.json`: nome, versão e descrição do plugin.
- `hooks/hooks.json`: aponta para `hooks/register.ts`.
- `hooks/register.ts`: os hooks do comando, o temporizador de 3 segundos e a regra de negar ferramentas enquanto o laço roda.
- `dsh_step.py`: ponte até a API do dsh. Usa `dsh_api.py`, na mesma pasta.
- `dsh_api.py`: autenticação, RPC, histórico e envio à API local do dsh.
- `gate.py`: as checagens C1 a C5 e a CLI usada pelo laço.
- `answer.txt`: última mensagem enviada ao dsh. É sobrescrito a cada envio.

## Dependências externas

- Token de lançamento do `dsh web` em `/Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/runtime/dsh_token.txt`, com permissão 600. Parâmetro inicial. Muda a cada reinício do `dsh web`.
- Id do chat do dsh: não é arquivo. Fica no estado da sessão (`$.state`), definido por `/auto_critique chat <id>`.
- Cookie de sessão em `/Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/runtime/jar.txt`, renovado a partir do token.
- Log em `/Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/runtime/laco_mod.log`.
- Última mensagem enviada ao dsh em `/Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/runtime/app_last_sent.txt`, usada para casar a resposta.

## Como carregar

Na sessão do app, o mod carrega pela recarga automática de mods. Em terminal, use:

```bash
claude --plugin-dir /Users/marcelohanones/Developer/personal/ParallelProse2/tools/auto_critique/mod
```

Para carregar em todas as sessões, `CLAUDE_CODE_PLUGIN_DIRS` aponta para essa mesma pasta na configuração do usuário. A variável é lida ao abrir a sessão, então é preciso reiniciar o Claude Code depois de configurá-la.

Depois de editar `register.ts`, a sessão recarrega o mod ao fim do turno da edição. Em terminal, `/reload-plugins` também recarrega. A recarga zera o estado do laço.

## Limitações

- A negação de ferramentas enquanto o laço roda ainda não foi testada com uma tentativa real.
- O laço depende de um temporizador de 3 segundos.
- Ao reiniciar o `dsh web`, é preciso gravar o token novo em `dsh_token.txt`. Se a porta 3080 estiver ocupada pelo processo anterior, o token novo não é aceito.
