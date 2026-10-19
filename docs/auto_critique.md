# Contrato entre harnesses — modo CRITIQUE

**Versão 18 — 2026-10-19.** Escrita por DSH sob C9. Substitui a v17: **C12 foi retirada da tabela por decisão de Markim**, e a razão está no histórico. A revisão desta versão é em `A20-cc.md`.

## O que este documento é

A troca de mensagens do modo CRITIQUE entre Claude Code (CC) e dsh, e nada além disso: não governa a memória (`docs/harness_memory_design.md`), nem o conteúdo técnico das rodadas. Ele existe porque o `modo_critique.md` dizia que não há canal direto entre os harnesses e, desde C1, há um — o arquivo da rodada, com o Markim como disparo.

## Decisões e premissas

| # | Decisão | O que a tornou necessária | O que a invalida |
|---|---|---|---|
| C1 | Caminho 3, híbrido: arquivo transporta, Markim dispara | Nenhum harness inicia o turno do outro, e a cópia manual fazia o Markim de transporte | Um disparo humano custar mais que o turno, ou o modo admitir turno sem humano |
| C2 | Modelo apartado: cada harness grava o que ouviu no próprio chat | Um arquivo de decisões com escritor único exigiria uma segunda fonte para o mesmo fato | Duas repetições consecutivas divergirem sem a checagem de topo pegar |
| C3 | Corpo integral no arquivo; `sent` medido no artefato | `sent` apontava para um scratch que morre, então não sobrevivia a recontagem | O arquivo ficar grande demais para carregar por rodada |
| C4 | `docs/auto_critique.md` nasce no fechamento, com um escritor | Documento de um escritor só, versionado, em vez de editado por rodada | — |
| C5 | `instructionFileCandidates` fora do contrato | Promover arquivo a candidato transforma mensagem em instrução permanente e cria injeção de um lado só | — |
| C6 | Numeração de par: `R{n}-{eu}` responde em `R{n}-{outro}` | O `R28` colidiu entre trilhas com o mesmo número | Duas trilhas precisarem do mesmo número |
| C7 | Tudo sem resposta carrega para a rodada seguinte | A imutabilidade de C3 elimina o retrabalho que a regra de ordem protegia | Uma rodada avançar sobre premissa derrubada sem o sinal do cabeçalho |
| C8 | Disparo manual; a investigação de automação vive no branch | Separar investigação de contrato | — |
| C9 | DSH escreve a versão 1 | A lista-base é do DSH e o CC já a aceitou | — |
| C10 | Um harness não acorda a si mesmo | O disparo é o único ato que o modo atribui ao Markim | A automação ficar restrita a rodada de recibo com gate vazio |
| C11 | O leitor roda o checador na abertura, antes de responder | O pre-commit sinaliza no commit, e os dois harnesses leem a árvore de trabalho, não o git — **P29 de `docs/harness_memory_design.md`**, citado aqui porque a regra vive lá e um leitor só deste contrato não a encontraria; o sinal chegaria depois da leitura, ou nunca, porque as rodadas ficam fora do git até o commit | O passo de abertura deixar de executar, ou a checagem virar bloqueio |

## O arquivo da rodada

- Um arquivo por lado por rodada, mesmo número: `R{n}-cc.md` e `R{n}-dsh.md`, na pasta da trilha (`implementation/`, `ingestion/`, `contract/`, `automation/`).
- **Um lado escreve no máximo uma vez por número**, na forma `R{n}-{lado}.md`. Quando um lado escreve de novo, o número sobe — é assim que `R38-dsh`, `R38-cc`, `R39-dsh`, `R39-cc`, `R40-dsh` saíram sem buraco. Adendo com sufixo (`R35-dsh-dec.md`) não conta como segunda escrita. É **regra de processo**, verificável pela leitura do histórico e não pelo checador: dois arquivos não podem ocupar o mesmo nome no mesmo instante, e uma sobrescrita só aparece no git.
- Criado pelo autor. Nunca editado. Correção é mensagem nova, ou adendo `{rodada}-{lado}-{assunto}.md` criado pelo mesmo escritor.
- O corpo é a mensagem inteira, não o resumo. O resumo é o cabeçalho.
- **Estado é derivado, nunca gravado, e por lado**: a rodada está completa quando existem os dois arquivos; enquanto faltar um, **o lado que falta é quem responde**. O par completo fecha a rodada.
- **Gap declarado**: um lado que não vai responder grava `gap: R{n}` no cabeçalho da sua mensagem seguinte, e a rodada deixa de apontar a vez. Sem a linha, o arquivo faltante continua sendo a vez. O `R34` é o caso real — `R34-cc.md` existe, `R34-dsh.md` não, e a declaração está no ponto 1 do **`R35-dsh.md`**. A v2 citava `R36-dsh.md`: correção de fato, aceita do `R39-cc`.
- A primeira linha **do corpo, depois do cabeçalho de contagem**, diz a primeira linha da mensagem que esta responde, ou "segue a mensagem X".

## O cabeçalho e a contagem

Primeira linha, sempre:

```html
<!-- sent: N palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
```

`sent` é medido no artefato, nunca no scratch. `received` é o mesmo número para o outro lado: identidade por construção. Medir com um marcador no lugar do número evita circularidade.

**O comando de contagem é obrigatório e é este:**

```bash
LC_ALL=C wc -w <arquivo>
```

Sem o locale fixado, o número muda com o ambiente: no `R34-cc.md`, `LC_ALL=C` dá **1117** e um locale UTF-8 dá **1119**. **O valor canônico é o do comando acima** — a definição é o comando, não a contagem de ninguém.

**A causa dos dois é medida, não é mistério:** a diferença vem de uma palavra, `às`. O locale UTF-8 desta plataforma conta `às` como dois tokens (`à` e `s`) e o C como um. O `R34-cc.md` tem duas ocorrências, e as duas linhas que divergem são exatamente as duas que as contêm. Um fixture com `às` é por isso um teste de regressão melhor que qualquer oráculo: falha de forma reproduzível se o locale se perder.

**O oráculo desempata e não tem neutralidade.** A separação de tokens do Python concordou com o C no corpus medido, e foi útil para decidir qual dos dois comandos era o canônico — mas ela diverge do C num caso plausível: com um espaço não separável (U+00A0), o C conta 1 e o Python conta 2. Ele não é, e nunca foi, uma especificação.

**O cabeçalho conta inteiro, marcadores `<!--` e `-->` incluídos.** No `R34-cc.md` os marcadores valem 2 palavras: 1117 no arquivo inteiro, 1115 sem eles (`sed 's/<!--//g; s/-->//g' | LC_ALL=C wc -w`).

**Vigência do template**: a redação com `LC_ALL=C` vale das mensagens escritas sob a v5 em diante. As **dezessete** anteriores — catorze rodadas e três adendos — ficam com a redação antiga, que não se edita, e a única divergência conhecida é a do `R37-dsh.md`: 1536 declarado onde o comando canônico dá 1535.

**O cabeçalho** é o bloco de metadados no topo: a linha de contagem e, logo depois dela, as linhas `chave: valor` permitidas, até a primeira linha que não seja de nenhum dos dois tipos. As chaves de hoje, e nenhuma outra:

- `gap: R{n}` — rodada que este lado não vai responder;
- `premissa-caida: <decisão> — <uma linha>` — premissa que uma resposta do Markim derrubou;
- `checador: <arquivo lido> — <n> achado(s)` — o que o checador reportou **sobre o arquivo que esta mensagem responde**. **Obrigatória da rodada R46 em diante**, pela vigência, e verificada pelo checador por dois lados: reanalisa o arquivo citado e compara o número, e confere que esse arquivo está entre os nomeados na linha de abertura.

A chave do checador é sobre o arquivo lido, nunca sobre o inventário da pasta. O inventário inclui a mensagem que está sendo escrita e muda no instante em que ela é gravada — seria um número falso por construção, que é o defeito que a contagem já corrigiu três vezes nesta trilha. Sobre o arquivo lido, o número é estável: aquele arquivo não muda mais.

**A brecha que a v10 deixou escrita, e o que a fechou.** A v10 comparava o número, não a escolha do arquivo: uma mensagem citando o arquivo errado com a contagem certa passava. A v11 fecha isso lendo a linha de abertura — que o contrato já exigia — e exigindo que o alvo da chave esteja entre os arquivos ali nomeados. É pertinência, não igualdade: uma mensagem pode responder a uma pergunta e ao adendo dela ao mesmo tempo, e o `R45-dsh.md` responde a dois arquivos. O `R46-cc.md` falha nessa regra e é exceção nomeada — cita o `R45-cc.md` e abre dizendo `R46-dsh.md`.

A reconciliação lê essas linhas sem interpretar prosa; é por isso que elas existem como chave em vez de frase.

## O gate

```text
critique-gate
round: R{n}
from: cc | dsh
to-markim: <C-labels> | none
blocks-advance: yes | no
why-not-blocking: <uma linha, obrigatória quando "no">
```

- `yes` proíbe o `passa` enquanto houver entrada em `to-markim` sem resposta gravada.
- `no` carrega as entradas e exige a justificativa, que o Markim contesta.
- `to-markim: none` não precisa de `why-not-blocking`.
- **O que entra em `to-markim`** é só o que a regra do modo permite perguntar: escolha **sem default claro** e **não reversível pela observação**. Escolha com default claro é recomendação, não pergunta; escolha que a observação corrige é default, com o gatilho de revisão escrito junto. Perguntar antes da evidência transforma a decisão em limite.
- Quem lê o gate é script, não modelo. Ler o próprio bloco e concluir que está tudo bem não é checagem, é opinião.
- **O gate é o último bloco de conteúdo do arquivo.** Depois dele só pode vir o rodapé `## Contagens`; nenhuma outra seção. É essa posição que faz um arquivo truncado ser detectável.
- **Seção** é um título ATX (`## `) no início da linha, fora de bloco de código. Um `## ` literal dentro da prosa vira título e cria seção fantasma: aconteceu no `R39-cc.md`, linha 23, por um backtick não fechado que atravessou a quebra de linha.
- **Seção não é rodapé.** Seção é qualquer título ATX; rodapé é o título cujo texto é exatamente `Contagens`. Um título extra **antes** do gate é feio e não viola nada; **depois** do gate viola a regra de posição. É essa distinção que dispensa exceção para o `R39-cc.md` — o título fantasma da linha 23 é seção, não rodapé — e é por isso que o checador percorre todos os títulos depois do gate em vez de parar no primeiro.
- **Um único `## Contagens`, e ele é o rodapé.** Arquivo com dois viola a regra, mesmo que um deles seja fantasma.
- **Vigência**: as regras de forma valem da **rodada R39** em diante, que é a primeira escrita sob a v2. As rodadas anteriores ficam como estão e o checador as reporta como histórico, não como falha. O `R37-cc.md` é **histórico conhecido** — gate na linha 49, rodapé na 57, `## Linha de disparo` na 62. Não é exceção: o bloco de exceções está vazio, e exceção é outro estado.

## Cues

- O cue é a **primeira linha inteira**, aparada, exatamente `passa` ou `parcial`. Nada mais nessa linha; o resto da mensagem pode vir depois.
- `parcial`: o harness mostra no chat o que entendeu. Não grava, não muda estado.
- `passa`: grava a mensagem no arquivo e imprime a linha de disparo.
- Mensagem sem cue é pergunta: o harness responde e não muda estado.
- O harness **anuncia o cue detectado** na primeira linha da sua resposta, antes de agir.
- Isso é interpretação, não mecanismo. O contrato não promete exatidão; promete que o erro aparece.

## Carga de itens (C7)

Item sem resposta carrega para a rodada seguinte, com a mesma referência, e a rodada seguinte o repete no topo. Quando uma resposta do Markim contraria premissa assumida numa mensagem anterior, o harness que percebe **diz isso no chat e grava `premissa-caida:` no cabeçalho da mensagem nova** — nunca no arquivo antigo, que é imutável. Detectar a contradição é interpretação: o sinal não bloqueia o avanço, e quem decide é o Markim.

## Disparo

O Markim dispara. A linha, quando usada:

```text
leia docs/reviews/<trilha>/R{n}-{eu}.md e responda em R{n}-{outro}.md
```

É otimização. Obrigatória é a **reconciliação na abertura**: o primeiro ato de qualquer turno é listar a pasta e comparar estados. Qualquer poke serve, inclusive "continua".

**Antes de responder, o leitor roda o checador** (C11): `python3 tools/check_auto_critique.py` varre a pasta inteira em cerca de 0,2 s e não gasta API — a pasta, não um arquivo só, porque o que interessa é o estado do registro. Havendo achado, ele vai no corpo da resposta; não havendo, nada é dito. A resposta sai de qualquer jeito — a checagem sinaliza, não bloqueia (P7). O pre-commit do git fica como rede opcional e não substitui esta chamada: as rodadas ficam fora do git até o commit, e o sinal chegaria depois da leitura.

## O que este contrato substitui

**A regra de ordem do modo fica substituída.** O título dela é, literalmente, "As perguntas do Markim vêm antes da resposta à outra parte", e o corpo dela termina com "a mensagem para a outra parte só é escrita depois da resposta". As duas citações são exatas e separadas: emendá-las numa frase só com aspas em volta foi um defeito da v16, corrigido aqui. A regra está no `docs/modo_critique.md` e é citada **pelo texto, não pela linha** — uma linha muda quando o documento muda, e o P13 do `docs/harness_memory_design.md` proíbe citar por número de linha. A premissa que a sustentava está declarada no próprio modo: "Isso evita reescrever a mensagem a cada resposta". Com C3 a mensagem nunca é reescrita, e C7 assume a carga. O resto do modo continua valendo.

## Fora do contrato

- `instructionFileCandidates` como canal (C5).
- Qualquer turno que o Markim não dispare, inclusive um harness acordando a si mesmo (C10), e o driver headless (C1).
- O agendador `dsh-schedule`: existe, foi medido, e está fora por **C10** — um harness não acorda a si mesmo. A investigação vive em `docs/reviews/automation/`, no branch `investigacao/automacao-rodadas`.
- **A trilha `automation/`**: usa `A{n}-{lado}.md`, é registro de investigação e **não é checada** — não tem bloco de gate e não segue as regras de forma desta seção. O checador não a lê, e isso é deliberado: uma trilha de investigação que passasse pelo checador seria tratada como rodada do modo, e as regras de vigência e exceção não valem para ela. Se a investigação virar prática, ela entra no contrato com as regras desta seção, e não antes.

## Verificação

O checador é `tools/check_auto_critique.py`, com testes em `tools/test_check_auto_critique.py`, todos passando. **Ele é dado como verificado quando os testes passam**, não quando alguém lê o código. O que ele checa, e só isso:

1. o bloco de gate existe, parseia; depois dele só o rodapé `## Contagens` pode aparecer como seção, e nada pode vir depois do rodapé — regra `gate-last`;
2. `to-markim` e `blocks-advance` são coerentes entre si — regra `gate-coherence`;
3. `sent` no cabeçalho confere com `LC_ALL=C wc -w` — regra `sent`;
4. há no máximo um título `## Contagens` no arquivo — regra `single-footer`;
5. a chave `checador:` existe, cita um arquivo existente e não ambíguo, e o número declarado confere com a análise desse arquivo — regra `checador`;
6. o arquivo citado na chave está entre os nomeados na linha de abertura — regra `opening`.

Cada item nomeia a regra que o implementa, e um teste confere que a lista do contrato e a do código são a mesma. Antes disso a correspondência era conferida à mão, e conferência à mão não é conferência.

Falha só conta da rodada R39 em diante; antes disso o checador reporta como histórico. As divergências conhecidas ficam no bloco abaixo, e o checador as lê dele — uma exceção não listada é falha, e uma listada é reportada como exceção.

```text
critique-exceptions
R46-cc.md | opening | cita R45-cc.md; a mensagem responde R46-dsh.md
critique-exceptions-end
```

O bloco sai vazio por ora, e isso é resultado, não omissão. As duas divergências conhecidas — `R37-cc.md` e `R37-dsh.md` — são anteriores à vigência, então o checador já as reporta como histórico; listá-las aqui as faria passar por exceção, que é outro estado. O `R39-cc.md` chegou a ser listado e saiu: o título da linha 23 começa com a palavra mas continua em texto, e a regra do título único, ancorada na linha inteira, não dispara nele — o checador encontra um único rodapé, na 77, que é o verdadeiro.

Ele **sinaliza**, nunca edita nem apaga — P7 do `docs/harness_memory_design.md`. Os dois lados o invocam do mesmo jeito, no passo de abertura (C11); o hook do CC, se existir, é entrega antecipada, e apagá-lo não quebra este contrato.

## Histórico de versões

- **v18 — 2026-10-19.** **C12 retirada da tabela por decisão de Markim**, no chat do DSH, depois de dez rodadas de investigação na trilha `automation/`. A razão registrada: a frase do C12 era mais larga que a premissa dela e que a própria condição de reabertura — as duas falavam só de manutenção, enquanto a sentença proibia todo turno sem disparo. O desenho daquela trilha é de **turno de resposta**, que nunca foi o assunto arguido. Retirar a frase não libera a automação: **C10 continua dizendo que um harness não acorda a si mesmo**, e é ele que governa o caso — com a saída mais estreita, que o desenho do A6 atende na primeira porta. A referência ao agendador em "Fora do contrato" passa a citar C10.
- **v17 — 2026-10-19.** A v16 trocou a citação por número de linha pela citação pelo texto — e emendou duas frases do modo numa só, entre aspas, suprimindo o meio. As duas passam a ser citadas separadamente e na forma exata, e o `Isso` do modo recupera a maiúscula. Registro porque o defeito nasceu **na correção** de outro defeito de citação, e é a segunda vez nesta trilha que um conserto introduz a classe que ele combatia.
- **v16 — 2026-10-19.** A regra das três listas do `docs/modo_critique.md` mudou: a terceira lista, "o que cabe ao Markim", deixa de ser obrigatória — ela existe quando há algo, e a ausência é resposta correta. Junto entrou a regra que faltava: nem toda escolha é decisão, e perguntar antes da evidência transforma a decisão em limite. O contrato acompanha em dois pontos: passa a citar a regra de ordem **pelo texto**, porque citava por número de linha e a edição do modo moveria a citação (P13 do `harness_memory_design`); e diz o que pode entrar em `to-markim`.
- **v15 — 2026-10-19.** A trilha `automation/` entra em "Fora do contrato", com a razão de o checador não a ler: ela é investigação, não rodada do modo. Sem essa linha, a cegueira do checador para `A*.md` parece um defeito e convida a uma correção que quebraria a separação entre investigação e prática. A referência ao `dsh-schedule` passa a citar C12, que é a decisão que de fato o mantém fora.
- **v14 — 2026-10-19.** Decisão de Markim em `R55-cc-dec.md`, tomada depois das duas recomendações coincidirem: C12 entra na tabela como decidido — não, por ora — com a condição de reabertura no campo que invalida. Junto entra a correção de escopo do CC em `R55-cc.md`: o que fica parado entre disparos é a pasta de rodadas, não o repositório, e a condição de reabertura precisa dessa precisão para não admitir qualquer mudança como motivo.
- **v13 — 2026-10-19.** Revisão do CC em `R50-cc.md`, com três correções medidas por ele: (a) a diferença 1119/1117 tem causa única — a palavra `às`, que o locale UTF-8 desta plataforma divide em dois tokens; duas ocorrências, duas linhas, dois tokens, e um fixture com `às` passa a ser o teste de regressão; (b) o oráculo do Python não é neutro, e diverge do C com espaço não separável (U+00A0: 1 contra 2) — ele desempata e não especifica; (c) sai o número de casos de teste escrito em prosa, que já estava velho, e a regra de numeração declara-se regra de processo, não de checador.
- **v12 — 2026-10-19.** Revisão do CC em `R49-cc.md`: os seis itens da verificação passam a nomear a regra que os implementa, entre crases, e o checador expõe a lista `RULES`. Dois testes novos fecham a correspondência — um compara o contrato com a lista, o outro confere que cada regra declarada aparece no código. Era a última conferência feita à mão.
- **v11 — 2026-10-19.** Revisão do CC em `R47-cc.md`: a chave `checador:` passa a ser conferida contra a linha de abertura (regra 6), que o contrato já exigia — o que faltava era o checador lê-la. É pertinência e não igualdade, porque uma mensagem pode responder a mais de um arquivo. Três testes novos, dezenove no total. O bloco de exceções deixa de ser vazio: o `R46-cc.md` entra, por citar `R45-cc.md` numa mensagem que responde ao `R46-dsh.md`.
- **v10 — 2026-10-19.** Revisão do CC em `R46-cc.md`, aceita: a chave `checador:` deixa de ser opcional e passa a ser obrigatória da rodada R46 em diante, com o motivo dele — opcional esvazia o sinal, porque a ausência deixa de significar alguma coisa. O checador ganha a regra 5, que reanalisa o arquivo citado e compara o número, com três testes novos e dezesseis no total. O limite da regra fica escrito: ela verifica o número, não a escolha do arquivo.
- **v9 — 2026-10-19.** Revisão do CC em `R45-cc.md`, duas delas contradições internas da própria v8: (a) a regra do rodapé único ainda nomeava o `R39-cc.md` como exceção, contra a cláusula de seção-que-não-é-rodapé e contra o bloco vazio — a frase sai; (b) o `R37-cc.md` passa a ser **histórico conhecido**, não exceção, que é o estado que o checador de fato aplica; (c) o C11 cita **P29 de `docs/harness_memory_design.md`** pelo nome, porque a regra vive lá; (d) a chave `checador:` entra na lista fechada, com a precisão de que ela é sobre o arquivo lido e não sobre o inventário — inventário inclui o arquivo que está sendo escrito e seria falso por construção.
- **v8 — 2026-10-19.** Revisão do CC em `R44-cc.md` e decisão de Markim em `R44-cc-dec.md`: C11 entra na tabela e na reconciliação — o leitor roda o checador sobre o arquivo que vai ler, antes de responder. Cai a recomendação de pre-commit como caminho principal, e por medição: as rodadas ficam fora do git, e o sinal do commit chegaria depois da leitura. O teste da cláusula de seção antes do gate entra, e são doze.
- **v7 — 2026-10-19.** Revisão do CC em `R43-cc.md`: (a) o contrato passa a distinguir seção de rodapé, que é o que faltava para o título fantasma do `R39-cc.md` não precisar de exceção — ele é seção, não rodapé; (b) o item 1 da verificação ganha a segunda metade, "e nada pode vir depois do rodapé", que o checador da v6 não checava por parar no primeiro título; (c) o checador ganha os dois consertos da revisão — percorre todos os títulos depois do gate e checa a contagem mesmo sem gate — e passa a ter testes, onze casos, que são o que o verifica.
- **v6 — 2026-10-19.** Revisão do CC em `R42-cc.md`, verificada e aceita: (a) são **dezessete** cabeçalhos com a redação antiga, não dezesseis — catorze rodadas e três adendos; o dezesseis anterior vinha de uma contagem feita só numa pasta e que não via os dois cabeçalhos escritos como "sobre o corpo"; (b) a vigência deixa de dizer "primeira rodada sob a v2" e nomeia a **R39**; (c) o bloco `critique-exceptions` entra para o checador ler em vez de carregar a lista, e sai **vazio**: as duas divergências restantes são pré-vigência e o checador já as trata como histórico, e a terceira que eu havia listado — o `R39-cc` — não é violação da regra ancorada; (d) a verificação ganha o item 4, título único de contagem, que antes só existia como prosa na seção do gate.
- **v5 — 2026-10-19.** Revisão do CC em `R41-cc.md`, aceita. O contrato fixava o comando na seção de contagem e continuava dizendo `wc -w` sem locale em dois outros lugares — o template do cabeçalho, linha 39, e a verificação, item 3. O checador lê o contrato, então seguir a verificação reabriria a divergência que a v4 fechou. Alinhados os dois, mais a vigência do template (16 cabeçalhos antigos ficam com a redação velha; a divergência do `R37-dsh.md` fica nomeada) e a formulação do oráculo como desempate, não definição.
- **v4 — 2026-10-19.** Revisão do CC em `R40-cc.md`, verificada e aceita: (a) a contagem passa a exigir `LC_ALL=C wc -w`, e o canônico do `R34-cc.md` é **1117** — o 1119 da v3 está retirado, e ele vinha do locale UTF-8, não do arquivo; (b) o oráculo independente (`python3` `split`) concorda com o locale C em todos os arquivos medidos; (c) o `R39-cc.md` entra como exceção nomeada da regra de título único. Registro junto que a correção do `R36-dsh` sobre essa contagem está retirada, e que o `R37-dsh.md` declara 1536 onde o comando canônico dá 1535.
- **v3 — 2026-10-19.** Revisão do CC em `R39-cc.md`, verificada ponto a ponto antes de aceita: (a) o gap do `R34` está no `R35-dsh.md`, não no `R36-dsh.md` — a v2 citava errado; (b) o cabeçalho passa a ter chaves `gap:` e `premissa-caida:`, e a definição de cabeçalho, porque prosa exige interpretação e o contrato pediu mecanismo; (c) a contagem do cabeçalho inclui os marcadores `<!--` e `-->`, o que resolve 1119 contra 1117; (d) vigência da posição do gate a partir da v2, com o `R37-cc.md` nomeado como exceção; (e) seção definida como título ATX fora de bloco de código, e um único `## Contagens`; (f) a regra de numeração, que fecha o buraco registrado no `R39-cc-dec.md`.
- **v2 — 2026-10-19.** Quatro pontos da revisão do CC em `R38-cc.md`, verificados antes de aceitos — as posições do gate e do rodapé conferem em `R35-dsh.md`, `R36-cc.md`, `R37-cc.md` e `R38-dsh.md`: (a) o gate passa a ser o último bloco de conteúdo, com o rodapé de contagens depois; a v1 exigia "última coisa do arquivo", o que nenhuma rodada cumpria; (b) estado por lado, com o lado faltante sendo a vez, mais o gap declarado; (c) o sinal de premissa derrubada passa a ser chat mais uma linha no cabeçalho novo; (d) "primeira linha do corpo, depois do cabeçalho".
- **v1 — 2026-10-19.** Primeira versão, escrita sob C9 e revisada em `R38-cc.md`.

## Revisão

Um escritor: DSH nesta versão. Mudança sobe a versão e é feita pelo mesmo escritor; rodada nenhuma edita o contrato. A revisão é do CC, com pontos numerados; a desta versão é em `A20-cc.md`.
