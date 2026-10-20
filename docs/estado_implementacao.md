## Pendências para o cenário

Para a regra "o arquivo na pasta é o start do outro harness" valer, falta isto. Nada abaixo está implementado.

1. **Um monitor contínuo.** Hoje o watcher roda uma passada e sai. Precisa de um processo que observe `docs/reviews/` e detecte o arquivo novo sem ninguém executá-lo. Sem isso, a pasta não é start de nada.
2. **Nenhuma colagem manual.** A transição manda o Markim colar a linha de disparo. Ela deve virar recurso de emergência, fora do fluxo normal.
3. **Ordem de arquivos novos.** Se chegam dois arquivos não vistos, o watcher recusa os dois. Processar em ordem não serve: `dispatch_line` só está correta quando o gatilho é o último arquivo da rodada, e o par processado em ordem dispara duas vezes, uma delas para o lado errado. O par colapsa num gatilho só — o último —, e o alvo é `R{n+1}-{quem abriu}`; a ordem vem da citação "Segue a mensagem", não do nome nem do `mtime`.
4. **Um start, uma vez.** O watcher marca o arquivo e grava o estado antes do disparo, então a queda não repete o start: ela o perde em silêncio. Falta o `disparando` com id, e no reinício um `disparando` sem resultado vira "salto interrompido, olhar humano", sem novo disparo.
5. **Falha de salto com política.** A falha já é terminal: o arquivo está em `seen` e a passada seguinte não repete o disparo. Falta o destino durável — um registro por rodada, com rodada, alvo, motivo e caminho do log —, e o aviso precisa nomear a rodada e o alvo, que hoje ele não nomeia.
6. **O `passa` vira arquivo.** Hoje o `passa` é digitado no chat. Para a automação valer, ele precisa ser um sinal que o harness detecte sozinho.
7. **Permissões para rodar sozinho.** O dsh roda com `workspace-write` e aprovação `ask`, e o cc com o comando aprovado. Falta verificar num salto que começa sem nenhum humano por perto.
8. **Prontidão antes da marca.** O watcher marca o arquivo em `seen` antes de checar, então um arquivo observado a meio do procedimento — cabeçalho em `0000`, contagem, `sed` — é marcado, recusado por `FALHA` e depois lido como reescrita: a rodada morre em silêncio. Prontidão (`sent` igual a `LC_ALL=C wc -w`, sha estável, checador limpo) decide antes de qualquer marca.

Os itens 1, 3, 4, 5 e 8 são código do watcher. O 2 e o 6 mexem em regra. O 7 é teste.

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
- Três saltos do dsh: 404 s e 64 chamadas; 250 s e 35; 286 s e 33.
- Um deles: 62.232 tokens de entrada nova, 51.309 de saída, 1,70 milhão de cache lido.
- Preset do dsh: `workspace-write` é o padrão. Não verificado: o efeito de `DSH_PERMISSION_MODE` sobre o modo efetivo.
- Permissão do cc: `Edit(docs/reviews/{target})` casou no último salto. Não verificado: `Grep`, `Glob` e as regras com padrão.

**Autorização de saltos**
- **D1, respondida pelo Markim em 2026-10-20:** sem teto. O contador de saltos relata, e não impede disparo. Confirma a Regra 5 do contrato; a linha anterior, que autorizava cinco saltos com dois usados, fica retirada.

**Pendente, com quem**
- **Markim:** a lista de capacidades liberadas para o salto do dsh — o que ele pode ler, escrever e executar. A recomendação medida é manter `workspace-write` para escrita e auditar leitura e shell no watcher sem bloquear.
- **Código do watcher:** os itens 1, 3, 4 e 5 das pendências.
- **Regra:** os itens 2 e 6.
- **Git:** o `README.md` da raiz é um arquivo vazio versionado.

**Comandos úteis**
- `python3 tools/check_auto_critique.py` — confere o registro inteiro.
- `python3 -m unittest discover -s tools` — suíte completa.
- `python3 tools/watcher_auto_critique.py --status` — contador e últimos avisos.
- `python3 tools/watcher_auto_critique.py --dry-run` — mostra o que dispararia, sem gravar nada.
- Uma passada que dispara um salto demora de 4 a 8 minutos: rode em segundo plano.
