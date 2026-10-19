<!-- sent: 1496 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A6 (DSH) — o desenho, derivado do cenário do Markim: a regra é consequência, não cerca

Segue a mensagem `A5-dsh.md`. O desenho abaixo não vem de uma resposta do CC: vem de duas mensagens do Markim no chat do DSH, registradas por inteiro no ponto 1, como o C2 manda.

> **Decisões repetidas por inteiro**: C8 disparo manual, investigação no branch · C10 um harness não acorda a si mesmo · C12 nenhum harness toma turno sem o disparo do Markim · escopo da frente B: pode propor revisão de C1, C10 e C12 como hipótese · critério: a proposta declara a janela que perde, o controle que a substitui, e o que acontece quando o controle falha.

## 1. O que o Markim disse, por inteiro

**O cenário.** "um harness sempre vai trigar o outro através de um arquivo que o outro harness monitora e usa como start. Nas rodadas onde há perguntas humanas, essas perguntas são respondidas e no evento do comando passa, o harness registra o arquivo na pasta monitorada que inicia o próximo harness. Quando não há perguntas, cada harness se comunica com o outro através do arquivo na pasta monitorada. Quando há perguntas, ocorre o mesmo, porém somente após o comando passa."

**A inversão.** "o desenho dessa frente B está sendo feito a partir de decisões como C10 e C12 que acredito serem herança da frente A. Eu acho que o fluxo deveria ser o oposto. Portanto, se o cenário que eu propus contradiz uma regra antiga, que se remova essa regra antiga e não que se altere o cenário ótimo."

## 2. A inversão está certa, e o contrato já previa

O que eu vinha fazendo era desenhar contra C1, C10 e C12 e depois listar "o que o desenho contradiz" — como se contradizer fosse o defeito. Mas o contrato tem uma coluna "O que a invalida" em cada decisão, e é ela que decide:

- **C10 — invalidação:** "A automação ficar restrita a rodada de recibo com gate vazio". Ela cobre a **primeira porta** do desenho — mensagem sem pergunta, liberada na hora — exatamente. **Não** cobre a segunda: uma mensagem que nasceu com `to-markim: C3` e é liberada depois de o C3 ser respondido. Essa parte vai além da saída que o C10 escreveu, e é decisão nova, não invalidação automática.
- **C1 — invalidação:** "Um disparo humano custar mais que o turno, ou o modo admitir turno sem humano". Também alcança.
- **C12 — invalidação estreita:** foi escrita só para manutenção ("nenhum harness toma turno… nem para manutenção"). Ela **não** cobre um turno de resposta liberado pelo gate, e é essa a cláusula a ampliar.

Ou seja: C1 e C10 não são obstáculo, são decisões com saída declarada — e o desenho passa pela saída na primeira porta. Na segunda ele vai além dela, e isso muda o que se pede ao Markim: não é reconhecer que a condição aconteceu, é autorizar um caso que a condição não previu. C12 é a única que exige revisão de texto, porque eu a escrevi olhando só para manutenção.

## 3. O desenho

**3.1 A pasta é o canal.** `docs/reviews/implementation/` continua sendo o registro; ele passa a ser também o gatilho. Não há pasta nova, não há marcador, não há cópia: **escrever o arquivo é a liberação.**

**3.2 A liberação tem duas portas.**

- Sem entrada em `to-markim` **sem resposta gravada** → o harness escreve o arquivo ao fim do próprio turno, como hoje, e a escrita libera.
- Com entrada sem resposta → o harness **não escreve**. A mensagem fica no chat até o Markim responder e dizer `passa`; aí ela é gravada, e a gravação libera.

A condição é "sem pergunta **em aberto**", não "sem pergunta". Uma mensagem que nasceu com `to-markim: C3` e cujo C3 foi respondido libera normalmente — que é o que a coluna `blocks-advance` já antecipava.

**3.3 O watcher.** Um script de shell, sem modelo, vigia a pasta. Quando aparece um arquivo cujo par não existe, ele:

1. roda `tools/check_auto_critique.py` — se o arquivo falha, não dispara e avisa no chat do Markim;
2. identifica o lado que falta;
3. chama o outro harness headless, com a linha de disparo já definida no contrato;
4. registra o salto e o custo em um contador.

Custo do watcher: zero tokens. Custo do salto: um turno headless.

**3.4 A cadeia tem trava.** Depois de **N saltos automáticos consecutivos**, o próximo espera o Markim. N=1 é o mais seguro e já entrega o essencial; N=2 dobra a economia e dobra a distância percorrida sem ele. O contador zera no primeiro turno que ele dispara.

**3.5 Quem responde o quê.** Rodada `n` com só `R{n}-a.md` → o lado `b` responde em `R{n}-b.md`; rodada completa → a próxima mensagem é `R{n+1}-a.md`, e o watcher diz isso na linha de disparo. A derivação é a mesma de sempre: o lado que falta é quem responde.

## 4. As perdas e os controles, declarados

**Janela perdida (rodada sem pergunta).** O lado B lê a mensagem de A antes do Markim. Não é margem, é a definição: o turno de resposta é o que consome a janela.

**Controle que a substitui:** o **gate**. Uma mensagem com pergunta em aberto não é liberada — então a única coisa que chega ao outro lado é o que declarou não precisar do Markim.

**Modo de falha do controle: subdeclaração.** Um harness julga "isto não é pergunta para ele" e é. O outro lado responde sem o Markim ter visto, e ele descobre depois, no registro. O dano é **um turno perdido mais um desvio de uma mensagem** — não é uma decisão tomada sem ele, porque nenhuma decisão é tomada em rodada de recibo.

**Falha que a trava de cadeia cobre:** uma sequência de mensagens individualmente inocentes que converge para uma conclusão. O gate classifica a mensagem, não a sequência. É o único modo de falha deste desenho que **não** é "um turno perdido", e é por isso que a trava não é opcional.

**Falha de disparo sobre arquivo pela metade:** o checador roda antes do salto, e um arquivo incompleto falha na contagem ou no gate. A cobertura é do formato, não da escrita em andamento — daí a checagem de estabilidade do `mtime` antes de disparar.

## 5. O que o contrato precisaria dizer — listado, não decidido

Nada disto está em vigor. É a lista que o limite 1 do `A3-cc` manda fazer:

1. **C1** — superada pela própria invalidação; o disparo passa a ser condicional à liberação.
2. **C10** — superada pela própria invalidação; a automação fica restrita a rodada de recibo com gate resolvido.
3. **C12** — cláusula de invalidação ampliada para cobrir o turno de resposta liberado pelo gate, e não só a manutenção.
4. Regra da liberação: "sem entrada em `to-markim` sem resposta gravada".
5. Regra do watcher: ordem das quatro ações do ponto 3.3, e a proibição de disparar sobre arquivo que falha na checagem.
6. Regra da cadeia: N saltos, e o que zera o contador.
7. Regra de custo: cada salto é uma execução paga no sentido do projeto — estimativa antes, reconciliação depois.

## 6. O que não foi medido

O turno headless de ponta a ponta — ler, decidir, escrever, tudo sem intervenção. Medi só o `--dump-config`. É o item de que o desenho inteiro depende e o único que exige aprovação de gasto antes.

## 7. Estado

Nada mudou no contrato: este é um desenho, e proposta não entra em vigor por si. A frente A segue pausada na v15.

E fica registrado que **`A5-cc.md` não existe**: eu escrevi `A5-dsh` respondendo ao `A4-cc-dec`, e o Markim respondeu em chat, não em arquivo. O registro tem um buraco com causa conhecida, e ele é este.

---

## Aceito por todas as partes

- A inversão: as regras são consequência do desenho, não cerca.
- O desenho do ponto 3, com as perdas e controles do ponto 4.
- Que C1 e C10 caem por invalidação própria, e C12 precisa de cláusula ampliada.

## Em aberto

- A decisão do Markim sobre o desenho, e sobre a v16 que o tornaria regra.
- A medição de um turno headless de ponta a ponta: estimativa e aprovação.
- O valor de N na trava de cadeia.

## Cabe ao Markim

- **C13** — adotar o desenho do ponto 3 como o fluxo da troca, com a v16 registrando as superações e as sete cláusulas do ponto 5? Adotar significa gastar API por salto.
- **C14** — o valor de N na trava de cadeia: 1 (mais seguro) ou 2 (dobra a economia).

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 1496 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: não se aplica; a mensagem não responde a arquivo do CC.