# Contrato da troca automatizada — ParallelProse2

**Versão 23 — 2026-10-20.** Escrito por DSH. A v23 traz a política de falha para dentro do contrato, onde ela passa a ser regra: P-a a P-e descreviam o watcher e viviam fora dele. Ela também tira da tabela medida a linha de "chamadas de um salto: 40", que não se refaz pelos artefatos deste repositório, e põe no lugar as duas medidas que saem do log de hop. E corrige a data da versão, que dizia 2026-10-19 desde a v21, quando a v21 e a v22 são de 2026-10-20. O motivo é a `D4`: a série em curso só é aposentada depois que o contrato que o monitor obedece está completo. A v22 ancora a regex do passo 4 no começo da linha e dá nome próprio ao contador, `{sent}`: a v21 trocava também a prosa que citasse a chave. O motivo é o item 2 do plano, que o T15 deixou vermelho de propósito até aqui. A v21 acrescenta a reconciliação à lista do watcher, dá à previsão de chamadas a forma sem base, e prende o comando do passo 4 às duas chaves do `sent` — o `sed` global corrompeu a `R1-cc` em quatro trechos. O motivo é o item 1 do plano da `R3-cc`. A v20 põe preço no bloqueio: o gate ganha `why-blocking`, exigido quando `blocks-advance: yes` carrega rótulo, e o checador confere. Bloquear deixa de ser gratuito. A v19 reduz a seção de autoria à regra que ela precisa: toda edição sobe a versão. A v18 trocou a estimativa de custo pela previsão de chamadas: o que se declara antes do disparo é quantas chamadas o salto faz, e a reconciliação compara com as feitas. A v17 tira o efeito do limite da cadeia: a Regra 5 passa a dizer que o salto não pede autorização, o contador vira registro e não porteiro, e a transição deixa de citar a trava. O código do watcher ainda recusa o segundo salto — ele está atrás do texto, e um teste marca a diferença.

## O cenário

O texto abaixo é do Markim, transcrito sem correção nenhuma — nem de ortografia, nem de acento. Ele é o objetivo deste documento.

```text
o que eu imagino sobre essa automacao é que um herness sempre vai trigar o outro
atraves de um arquivo que o outro harness monitora e usa como start. Nas rodadas
onde há perguntas humanas, essas perguntas sao respondidas e no evento do comando
passa, o harness registra o arquivo na pasta monitorada que inicia o proximo
harness. Quando nao ha perguntas, cada harness se cominica com o outro atraves do
arquivo na pasta monitorada. quando há perguntas, ocorre o mesmo, porem somete
apos o comando "passa".
```

## A regra de derivação

**Toda regra deste documento existe para implementar o cenário acima.** Ela nomeia, junto de si, a parte do cenário que serve; se não servir a nenhuma, não entra; se deixar de servir, sai. Uma regra sem essa ligação é uma regra a ser removida, e não uma regra a ser obedecida.

O cenário tem três partes:

- **A** — o arquivo na pasta monitorada é o start do outro harness.
- **B** — sem pergunta, o arquivo vai direto.
- **C** — com pergunta, o arquivo que inicia o próximo harness só vai depois do `passa`; o arquivo com a pergunta não inicia nada.

## As regras

### Regra 1 — a pasta é o canal, e escrever o arquivo é a liberação

**Serve a:** A.
**Premissa:** o registro é o único lugar que os dois lados conseguem ver, e a escrita é o instante em que uma mensagem passa a existir.
**Invalidaria:** a troca deixar de passar pelo registro — um processo chamando o outro diretamente, sem arquivo.

### Regra 2 — sem pergunta em aberto, o arquivo vai ao fim do turno

**Serve a:** B.
**Premissa:** o bloco de gate declara as perguntas de forma que um script leia; e um harness honesto não escreve mensagem com pergunta que ele mesmo não declarou.
**Invalidaria:** a subdeclaração virar norma — mensagens carregando pergunta que o gate não registra.

### Regra 3 — com pergunta em aberto, a resposta espera o `passa`

**Serve a:** C.
**Premissa:** o arquivo com pergunta é gravado ao fim do turno com `blocks-advance: yes` e não dispara; o `passa` libera o arquivo seguinte, que é a resposta e entra com `blocks-advance: no`. O arquivo com a pergunta não é editado; o registro da resposta é o arquivo novo.
**Invalidaria:** a resposta passar a ser uma edição do arquivo com a pergunta, ou o `passa` liberar o próprio arquivo com `yes`.

### Regra 4 — o watcher dispara o outro lado, e recusa o salto, nunca a rodada

**Serve a:** A.
**Premissa:** o checador dá um veredito por arquivo, sem decisão de sentido — ele diz se o arquivo está bem formado, não se ele está certo.
**Invalidaria:** a recusa do watcher passar a decidir o sentido da rodada; uma checagem que decide não é checagem.

### Regra 5 — o salto não pede autorização

**Serve a:** A.
**Premissa:** o cenário diz que o arquivo na pasta é o start do outro harness; um start que espera permissão não é start.
**Invalidaria:** a cadeia automática produzir mensagem que ninguém leu e que ninguém consegue atribuir — aí o limite volta, e volta escrito.

O watcher dispara assim que o arquivo liberado aparece. **Não há trava e não há reset**: o contador de saltos é registro, não porteiro, e serve para relatar quantos saltos houve entre dois disparos seus.

O que segura a cadeia não é um número, é o gate: arquivo com pergunta em aberto não é disparado (Regra 3), e arquivo que falha o checador não é disparado (Regra 4). Uma cadeia termina quando o outro lado pergunta.

### Regra 6 — cada salto declara quantas chamadas faz

**Serve a:** A e B.
**Premissa:** o salto sobe uma sessão nova e faz uma chamada por passo do laço de ferramentas; o número de passos é o que se pode prever, e o que se confere no log sem ambiguidade.
**Invalidaria:** o salto passar a fazer uma chamada só, ou o laço de ferramentas deixar de existir — aí não há número a prever.

Antes do disparo, o watcher declara quantas chamadas o salto deve fazer. Depois, a reconciliação lê o log de sessão e compara com as que foram feitas. Um salto que faz o dobro das previstas está fora do previsto, mesmo que as chamadas tenham saído baratas.

**A previsão tem duas formas.** O número, quando há base medida; **"sem base, primeira medição"**, quando não há — e aí a reconciliação cria a base, em vez de comparar com uma inventada.

**Os dois lados fazem chamadas; só um cobra por token.** Hoje o dsh cobra, e o cc roda na assinatura do plano Pro, informada pelo Markim em 2026-10-19 — mas a previsão de chamadas vale para os dois, porque é ela que diz o tamanho do salto. O custo em tokens fica registrado como consequência, e não é o que se estima.

## O watcher

Ele é a única peça que faz o cenário acontecer, e o que ele faz é isto, nesta ordem:

1. **Reconcilia** na abertura: lista a pasta, compara com o último estado, e sabe quem escreveu o quê.
2. **Checa** o arquivo liberado por arquivo — `analyze()` sobre o caminho, não a varredura da pasta — porque a decisão dele é sobre um arquivo.
3. **Decide**: gate sem pergunta em aberto, dispara o outro lado; gate com pergunta, não dispara, e avisa no chat do Markim.
4. **Dispara** o outro harness com a linha de disparo.
5. **Conta** o salto na cadeia.
6. **Reconcilia o salto**: lê os eventos do `--json` no stdout do salto — o log de sessão que o hop guarda —, conta as chamadas e grava a contagem por rodada.

Ele **nunca escreve no registro** e **nunca responde por um harness**. Se ele parar, a troca volta a ser manual — é para isso que serve a transição.

**O que o salto diz não some.** Um `returncode: 0` não esconde o stderr do lado cc: quando ele traz a frase `is not matched by file permission checks`, o watcher a noticia. E o zeramento manual do contador também deixa notícia — sem isso, o estado mostra `count: 0` com a última notícia de um salto, e o rastro some.

**Como ele chama o dsh:** `dsh --profile headless`. A forma `dsh headless` também vale — as duas são gramática do mesmo comando, e `--profile` é a canônica só por dizer o que faz, não porque a outra erre.

**Como ele chama o Claude Code:** o comando aprovado, com dois marcadores — `{line}` é a linha de disparo e `{target}` é o arquivo que a sessão vai gravar:

```text
claude -p {line} --permission-prompts none --allowedTools Read "Edit(docs/reviews/{target})" "Bash(LC_ALL=C wc -w *)" "Bash(python3 tools/check_auto_critique.py)" "Bash(python3 -m unittest discover -s tools)" "Bash(python3 tools/test_*.py)" Grep Glob
```

`Edit` e não `Write`: o Claude Code casa as regras de permissão de arquivo só na forma `Edit(path)`, e elas cobrem todas as ferramentas de edição. O alvo não existe quando a sessão começa — quem grava é ela —, então a regra é escrita para criar. O primeiro disparo do lado cc com `Edit` já ocorreu — o hop de 2026-10-19 que gravou a `R9-cc.md` —, com `returncode: 0`, stderr vazio e o arquivo criado. O critério é a ausência da frase `is not matched by file permission checks` no stderr do hop, nunca o arquivo existir: o disparo anterior, com `Write`, gravou com a frase presente. Na `R10-cc`, uma gravação em caminho do repo fora do alvo foi recusada, e a recusa se identificou como o classificador do auto mode — não como a regra `Edit(path)`. **Premissa:** a recusa foi observada uma vez, com `--permission-prompts none` e os `settings` do Markim. **Invalidaria:** um hop com `settings` limpo em que a mesma gravação passe. Segue não medido: a atribuição por camada — regra do comando aprovado, `settings` herdado, classificador —; medi-la exige um hop com `settings` limpo.

**O comando aprovado é piso, não teto.** Com `--permission-prompts none`, o que decide é o classificador do auto mode mais as regras herdadas, não a lista do comando como allowlist fechada. A sessão do hop herda o `~/.claude/settings.json`: **71 regras** em `permissions.allow` (contadas na `R10-cc`), sem `deny`, sem `ask`, sem `defaultMode`, mais `additionalDirectories` com `/private/tmp`. Na `R10-cc`, `ls`, `sed -n`, `grep`, `git status` e `python3 -c` rodaram sem casar com a lista do comando, e `ps`/`pgrep` rodaram sem casar com regra nenhuma. Consequência: stderr vazio é compatível com a regra usada, a regra não exercida e a chamada liberada por outra camada; o stderr do hop não separa as camadas, e o uso de `Grep`, `Glob` e das regras com padrão segue não medido por esse caminho. **Premissa:** o hop sobe com o `HOME` do Markim e herda `permissions.allow` e `additionalDirectories`. **Invalidaria:** o watcher passar a disparar com `settings` próprio.

**O salto se anuncia.** O watcher exporta `WATCHER_HOP=R{n}-{responder}` no ambiente do subprocesso, antes de disparar; a sessão o lê na abertura. É a marca do salto, e não depende de `ps` — que não casa com a lista do comando e é liberado pelo classificador. **Premissa:** o watcher é o processo pai e monta o ambiente do salto. **Invalidaria:** o disparo deixar de ser subprocesso — fila, outro host, ou gatilho assíncrono.

**O disparo do dsh roda fora do sandbox.** O perfil do dsh é gravado em `~/.dsh` antes de qualquer chamada de API, e um sandbox de escrita bloqueia ali com `EPERM` — o erro não é da forma do comando, é do lugar onde ele roda. Medido em 2026-10-19: sob sandbox de escrita, `dsh headless --help` para em `~/.dsh/profiles/headless/cordis.yml` com `EPERM` e sai com código 1. A passada e o disparo do lado cc não tocam `~/.dsh` e não têm essa exigência.

## A política de falha

**Serve a:** A. **Premissa:** um salto que falha não pode ser repetido — um lado escreve uma vez por número —, e uma falha que não se atribui não se manda refazer. O destino é `tools/.watcher-hops/index.jsonl`, uma linha por salto, com rodada, alvo, motivo, caminho do log, passos e a previsão declarada.

- **P-a — saída diferente de zero, ou timeout de 1800 s:** o salto é registrado como `falha-de-salto`; o aviso nomeia a rodada e o alvo, e não há nova tentativa.
- **P-b — saída zero e nenhum `R{n}-{respondente}.md` no registro ao fim:** `sem-resposta`. O salto rodou, então ele conta na cadeia; e não há nova tentativa.
- **P-c — resposta que falha o checador:** recusa e aviso, e o arquivo recusado continua em `seen`, com a notícia nomeando o arquivo.
- **P-d — o marcador do `sent` presente por mais de quinze minutos:** aviso, nem FALHA nem silêncio.
- **P-e — o monitor e a colagem manual são gatilhos da mesma cadeia:** enquanto o monitor roda, o `--status` o anuncia como ativo, e a colagem não é o caminho normal.

**Invalidaria:** a repetição passar a ser segura — observar um salto de saída diferente de zero que ainda assim deixa a resposta completa. Aí a decisão de repetir volta, e volta escrita.

## A cadeia

- Um **salto** é um disparo do watcher.
- O contador **zera** quando o Markim dispara à mão, e quando a rodada termina sem arquivo a responder.
- Não há trava: o contador não impede disparo nenhum. Ele relata quantos saltos houve, e é o que se lê para saber se a cadeia andou longe demais.

## O que foi medido

| medida | valor | como |
|---|---|---|
| linha de base de instruções, por sessão | ~10,6 mil tokens de entrada nova | medido em três execuções headless; na execução da R2-dsh, a primeira chamada tem 10.713 |
| primeira chamada com o bloco de regras, prompt total | 14,7 a 17,2 mil (medido: 15.833) | derivado da base de 12.318; a medição da R2-dsh cai dentro da faixa |
| rodar o checador com a saída descartada | ~26 tokens | diferença na mesma posição de chamada |
| trazer a saída do checador ao contexto | ~2.700 tokens | diferença na mesma posição de chamada |
| passos de modelo por salto | 18, 45, 76, 52, 27, 65 e 27; mediana 45 | contados de `step_start` em `tools/.watcher-hops/hop-*-R{8,9,10,11,13,14,15}-dsh.json`, 2026-10-20 |
| `tool_call` por salto | 27, 53, 88, 64, 35, 75 e 33 | contados de `type: tool_call` nos mesmos sete arquivos; `tool_call` não é passo de modelo |
| salto medido — entrada nova | 55.434 | medido: soma de `inputTokens` das 40 chamadas |
| salto medido — saída | 69.776 | medido: soma de `outputTokens` |
| salto medido — cache lido | 3.285.888 | medido: soma de `cacheReadTokens` |
| salto medido — cache escrito | 0 | medido: soma de `cacheWriteTokens` |
| prompt total do salto medido | 3.341.322 | derivado: entrada nova + cache lido, 40 chamadas |

**Os campos são os do log de sessão do dsh:** entrada nova é `inputTokens` (o que não veio do cache); cache lido é `cacheReadTokens`; cache escrito é `cacheWriteTokens`; saída é `outputTokens`. O prompt de uma chamada é entrada nova + cache lido; o custo do salto é a soma das chamadas.

**O que a faixa de 14,7 a 17,2 mil inclui:** a primeira chamada do salto, não o salto. Ela soma a base de 12.318, o bloco de regras de 2.153 e a rodada lida, de 230 a 2.724; a medição da R2-dsh dá 15.833 de prompt total. Ela **não** inclui ler o contrato inteiro (mais 5.932) nem o prompt do watcher (cerca de 400). Um salto que faça qualquer das duas coisas custa mais, e a estimativa tem de dizer qual dos casos está estimando. O salto inteiro é a soma das chamadas: 45 na mediana dos sete, e o número cresce com as ferramentas.

**A medição separa o que a tabela antiga misturava.** A linha de base de 10,6 mil é a entrada nova da primeira chamada; a composição de 14,7 a 17,2 mil é o prompt total dessa chamada. A medição da R2-dsh dá 10.713 de entrada nova, 5.120 de cache lido e 15.833 de prompt na primeira chamada; no salto, 55.434, 3.285.888 e 3.341.322. Quem estima diz se está estimando a primeira chamada ou o salto, e quantas chamadas o salto deve fazer.

**O lado cc não entra nesta tabela.** Ele roda na assinatura do plano Pro, informada pelo Markim, e não cobra por token: não há base dele a medir. Os números acima são do dsh.

Estas são as medidas que sustentam as regras acima. As de token são do primeiro salto pago, a sessão `session-c220c8f8-a8d5-4af6-b1ba-df966fa29456`, que gravou a `R2-dsh.md` em **2026-10-19**; a conta é a soma de `inputTokens`, `outputTokens`, `cacheReadTokens` e `cacheWriteTokens` por chamada, e o log de sessão é o artefato; aquele salto fez 40 chamadas. Aquele log de hop está no repositório e não tem JSON — ele rodou antes do `--json` —, então as linhas de token não se refazem relendo o arquivo: refaz-se o salto. As de passos e de `tool_call` sim: saem de `tools/.watcher-hops/`, e são sete saltos. As demais foram feitas em sessões headless reais na mesma data, com reconciliação de tokens por chamada. Quem quiser refazê-las repete o experimento.

## A transição

**Enquanto o watcher não disparar aquele salto, o disparo é manual:** o Markim põe no chat do outro lado a linha de disparo, e nada acontece sozinho.

O watcher não dispara quando não está rodando, ou quando aquele lado não tem comando configurado. Esta cláusula não é um segundo modo, e não deve ser reformulada em um: ela descreve o watcher que não dispara, não uma escolha entre dois caminhos.

## A mecânica

### O arquivo da rodada

- Um arquivo por lado por rodada, mesmo número: `R{n}-cc.md` e `R{n}-dsh.md`, em `docs/reviews/`.
- Criado pelo autor, nunca editado. O gate não é exceção: ele é escrito com o estado da mensagem e não muda depois. Correção é mensagem nova, ou adendo `R{n}-{lado}-{assunto}.md`, com o assunto em minúsculas ASCII e hífens — `R2-dsh-log-de-execucao.md`. O adendo corrige: não abre nem fecha rodada, e não conta para o par.
- **O registro é transporte, não arquivo.** A rodada existe enquanto a troca está aberta. O que precisa durar vai para este contrato, ou para o ledger da etapa — nunca fica só na rodada. Rodada é descartável; decisão não é.
- O corpo é a mensagem inteira, não o resumo.
- Estado derivado da existência: o par completo fecha a rodada; o lado que falta é quem responde. Um gap declarado fecha a vez sem arquivo.
- Um lado escreve no máximo uma vez por número; quando escreve de novo, o número sobe. Adendo com sufixo não conta.

### O cabeçalho e a contagem

Primeira linha, sempre:

```html
<!-- sent: N palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
```

O cabeçalho conta inteiro, marcadores incluídos. O comando de contagem é obrigatório e é este:

```bash
LC_ALL=C wc -w <arquivo>
```

Sem o locale fixado o número muda com o ambiente. A diferença tem causa conhecida: a palavra `às` é um token no locale C e dois num locale UTF-8.

Depois da linha de contagem vêm as chaves, até a primeira linha que não seja chave:

- `gap: R{n}` — rodada que este lado não vai responder;
- `premissa-caida: <decisão> — <uma linha>` — premissa que uma resposta do Markim derrubou;
- `checador: <arquivo lido> — <n> achado(s)` — o que o checador reportou sobre o arquivo que esta mensagem responde.

A chave do checador é sobre o arquivo lido, nunca sobre o inventário da pasta: o inventário inclui a mensagem que está sendo escrita e muda no instante em que ela é gravada.

**As chaves começam na linha seguinte à contagem, sem linha em branco antes delas.** O leitor procura as chaves no primeiro bloco do arquivo, e um bloco em branco antes da primeira chave as esconde dele.

**A abertura** vem depois das chaves e antes do primeiro título: `Segue a mensagem <arquivo>` para uma mensagem respondida, `Segue as mensagens <arquivo> e <arquivo>` para mais de uma. O arquivo citado na chave do checador é um dos nomeados nela.

### O gate

O bloco é uma cerca cujo info é `critique-gate`; é o info que o identifica, e uma cerca com outro info conta como gate ausente.

```critique-gate
round: R{n}
from: cc | dsh
to-markim: <rótulos> | none
blocks-advance: yes | no
why-blocking: <uma linha, quando "yes" e houver rótulo>
why-not-blocking: <uma linha, quando "no" e houver rótulo>
```

- `yes` impede que este arquivo dispare o próximo salto; o avanço vem do arquivo seguinte, e o `passa` é o cue que libera esse arquivo.
- **O gate é escrito uma vez, com o estado da mensagem: `yes` se ela carrega pergunta em aberto, `no` se não.** Ele nunca muda. O `why-not-blocking` diz por que um rótulo em `to-markim` não bloqueia; ele é exigido no arquivo com `no` que ainda cita o rótulo, porque a resposta já foi gravada. O formato não tem campo de "respondido": quem registra a resposta é o arquivo seguinte, que cita o rótulo no corpo e entra com `no`.
- `to-markim: none` não precisa de `why-not-blocking`.
- `yes` exige ao menos um rótulo em `to-markim`; `yes` com `none` é incoerente.
- **Bloquear exige justificativa.** `yes` com rótulo exige `why-blocking`: uma linha dizendo por que aquela escolha não tem default claro e por que a observação não a corrige. Sem essa linha o gate é incoerente, e o checador aponta. O bloqueio passa a custar trabalho — e uma pergunta que não consegue pagar esse preço não bloqueia a cadeia.
- O gate é o último bloco de conteúdo. Depois dele só pode vir o rodapé `## Contagens`, e nada depois do rodapé.
- Quem lê o gate é script, não modelo.

### Os cues

- O cue é a **primeira linha inteira**, aparada, exatamente `passa` ou `parcial`.
- `parcial` mostra no chat o que se entendeu; não grava, não muda estado.
- `passa` grava a mensagem seguinte no arquivo — a resposta —, e é a liberação (Regra 3). A mensagem com a pergunta já está no registro, com `yes`, e não é regravada.
- Mensagem sem cue é pergunta: responde e não muda estado.
- O harness **anuncia o cue detectado** na primeira linha da resposta, antes de agir.
- Detectar cue é interpretação, não mecanismo. O contrato promete que o erro aparece, não que ele não acontece.

### O checador

É `tools/check_auto_critique.py`, com testes em `tools/test_check_auto_critique.py`. Verificado quando os testes passam, não quando alguém lê o código.

Ele sinaliza e nunca edita. O leitor o roda na abertura; o watcher o roda antes de disparar; e os dois usam a mesma análise sobre o mesmo arquivo, então divergem no máximo por tempo.

### O procedimento da rodada

Um salto segue sete passos, nesta ordem, do lado dsh e do lado cc. Cada passo nomeia o que o executa; o que não está nesta lista não é passo do salto. O watcher anexa este procedimento à linha de disparo dos dois lados, então ele chega a cada salto.

1. **Leitura em lote.** Lê, numa única mensagem, o contrato, o arquivo que a linha de disparo nomeia e a rodada anterior do mesmo par. Executa: três leituras de arquivo em paralelo — `read` do contrato, do arquivo disparado e da rodada anterior —, e não três mensagens.
2. **Escrita.** Escreve a resposta uma vez, com o cabeçalho em `0000`. Executa: uma escrita de arquivo (`write`) em `docs/reviews/R{n}-{lado}.md`.
3. **Contagem.** Conta as palavras uma vez. Executa: `LC_ALL=C wc -w docs/reviews/R{n}-{lado}.md`.
4. **Cabeçalho.** Troca o número nas duas linhas que o carregam — a do `sent` no cabeçalho e a do rodapé —, sem tocar no corpo: a regex é ancorada no começo da linha, e o contador chama `{sent}` para não confundir com o `{n}` da rodada. Executa: `sed -i '' -E 's/^(<!-- sent:|- \*\*sent\*\*:)[[:space:]]*0000/\1 {sent}/' docs/reviews/R{n}-{lado}.md`.
5. **Checador.** Roda o checador no fim, uma vez, sobre o registro inteiro. Executa: `python3 tools/check_auto_critique.py`.
6. **Suíte.** Roda os testes quando a rodada mexe em código, ou no contrato que os testes leem. Executa: `python3 -m unittest discover -s tools`.
7. **Ambiente.** Não investiga o ambiente — processos, variáveis de ambiente, `~/.dsh`, sessões, logs de hop — a menos que a rodada peça. Executa: nenhum comando; é a proibição que vale para os seis passos acima.

**Passo é chamada ao modelo, não ferramenta.** A meta é de no máximo doze passos por salto; o que a reduz é o lote — três leituras num passo, e contagem, ajuste e checador num passo. Quem escreve a rodada declara o plano de passos no início da resposta e o número dado no fim, na mesma mensagem.

## Verificação

1. o bloco de gate existe, parseia; depois dele só o rodapé `## Contagens` pode aparecer como seção, e nada pode vir depois do rodapé — regra `gate-last`;
2. `to-markim` e `blocks-advance` são coerentes entre si nas duas direções: `no` com rótulo exige `why-not-blocking`, e `yes` com rótulo exige `why-blocking` — regra `gate-coherence`;
3. `sent` no cabeçalho confere com `LC_ALL=C wc -w` — regra `sent`;
4. há no máximo um título `## Contagens` no arquivo — regra `single-footer`;
5. a chave `checador:` existe, cita um arquivo existente e não ambíguo, e o número declarado confere com a análise desse arquivo — regra `checador`;
6. o arquivo citado na chave está entre os nomeados na linha de abertura — regra `opening`.

**Vigência**: as regras de forma valem da **rodada R1** em diante, porque o registro começa vazio e não há histórico a preservar. Toda rodada escrita aqui é conferida.

**Obrigatória da rodada R2 em diante**: a chave do checador. A primeira mensagem de uma série não responde arquivo nenhum, e por isso não tem o que citar.

O bloco abaixo é onde divergências conhecidas ficam, uma por linha, com a razão. **Está vazio, e vazio é o estado correto** enquanto nenhuma existir:

```text
critique-exceptions
critique-exceptions-end
```

### A linha de disparo

Dois casos, duas formas:

```text
rodada aberta:  leia docs/reviews/R{n}-{autor}.md e responda em R{n}-{respondente}.md
par completo:   leia docs/reviews/R{n}-{ultimo}.md e responda em R{n+1}-{primeiro}.md
```

`autor` escreveu o arquivo lido; `respondente` é o outro lado; `primeiro` abriu a rodada `n`; `ultimo` escreveu o último arquivo dela — e é o `primeiro` quem abre a `n+1`.

O registro é uma série só, em `docs/reviews/`, sem subpasta. Quando o watcher não dispara, é o Markim quem usa a linha. A reconciliação na abertura — listar a pasta e comparar estados — é obrigatória de qualquer jeito.

## Versionamento

- **Toda edição sobe a versão** e diz, em uma linha, o que mudou e por quê.

## O escopo

Este documento governa a troca entre os dois harnesses, desde 2026-10-19. Nenhum outro documento é citado por ele, e ele não cita nenhum.

**Referências a decisões de rodadas anteriores são história.** Rodadas escritas antes desta data citam contratos que não governam mais a troca; essas citações registram o que valia então, e não o que vale agora. A vigência é deste documento.

**Nenhuma regra deste contrato vem de arquivo apagado, de commit ou de rodada antiga.** Regra só existe aqui. Um número pode vir de qualquer lugar, e a única obrigação é dizer de onde veio e se é medido ou derivado. Encontrar o texto antigo não o transforma em regra, porque este contrato já declarou que não é.

---


## Contagens

- **sent**: 4636 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
