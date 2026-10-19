# Contrato da troca automatizada — ParallelProse2

**Versão 1 — 2026-10-19.** Escrito por DSH. Este documento governa a troca de mensagens entre Claude Code e dsh, e nada além dela. Ele é autônomo: não cita e não depende de outro documento. **É o único contrato que governa a troca desde 2026-10-19; nada anterior a esta data governa o disparo nem o formato.**

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
- **C** — com pergunta, o arquivo só vai depois do `passa`.

## As regras

### Regra 1 — a pasta é o canal, e escrever o arquivo é a liberação

**Serve a:** A.
**Premissa:** o registro é o único lugar que os dois lados conseguem ver, e a escrita é o instante em que uma mensagem passa a existir.
**Invalidaria:** a troca deixar de passar pelo registro — um processo chamando o outro diretamente, sem arquivo.

### Regra 2 — sem pergunta em aberto, o arquivo vai ao fim do turno

**Serve a:** B.
**Premissa:** o bloco de gate declara as perguntas de forma que um script leia; e um harness honesto não escreve mensagem com pergunta que ele mesmo não declarou.
**Invalidaria:** a subdeclaração virar norma — mensagens carregando pergunta que o gate não registra.

### Regra 3 — com pergunta em aberto, a gravação acontece no `passa`

**Serve a:** C.
**Premissa:** o `passa` é lido pelo harness como cue, e o harness anuncia o cue detectado antes de agir; o arquivo gravado depois dele carrega `blocks-advance: no`, como a seção do gate exige.
**Invalidaria:** a leitura de cue se mostrar não confiável, e a mensagem ser gravada sem a resposta.

### Regra 4 — o watcher dispara o outro lado, e recusa o salto, nunca a rodada

**Serve a:** A.
**Premissa:** o checador dá um veredito por arquivo, sem decisão de sentido — ele diz se o arquivo está bem formado, não se ele está certo.
**Invalidaria:** a recusa do watcher passar a decidir o sentido da rodada; uma checagem que decide não é checagem.

### Regra 5 — a cadeia tem trava

**Serve a:** A.
**Premissa:** o gate classifica uma mensagem, não uma sequência; uma sequência de recibos pode convergir para algo que ninguém autorizou.
**Invalidaria:** a rodada sem pergunta deixar de existir por construção — sem recibo, a cadeia não chega a conclusão nenhuma.

**O default é 1 salto.** Sobe para 2 quando a trava tiver interrompido três cadeias seguidas que seriam inteiramente de recibo; desce para 1 se algum salto automático tiver produzido mensagem descartada. A escolha é observável no registro, e não pede decisão nova.

### Regra 6 — cada salto é execução paga

**Serve a:** A e B.
**Premissa:** cada salto sobe uma sessão nova, e sessão nova custa API — o piso medido é a linha de base de instruções, cerca de 10,6 mil tokens de entrada por sessão.
**Invalidaria:** o salto passar a rodar em modelo local, ou o custo cair a ponto de não precisar de estimativa.

Estimativa antes, reconciliação depois, com os três campos separados — entrada nova, saída e cache lido — e cada campo com o rótulo de medido ou derivado. Um total único esconde o campo que mais pesa.

## O watcher

Ele é a única peça que faz o cenário acontecer, e o que ele faz é isto, nesta ordem:

1. **Reconcilia** na abertura: lista a pasta, compara com o último estado, e sabe quem escreveu o quê.
2. **Checa** o arquivo liberado por arquivo — `analyze()` sobre o caminho, não a varredura da pasta — porque a decisão dele é sobre um arquivo.
3. **Decide**: gate sem pergunta em aberto, dispara o outro lado; gate com pergunta, não dispara, e avisa no chat do Markim.
4. **Dispara** o outro harness com a linha de disparo.
5. **Conta** o salto na cadeia.

Ele **nunca escreve no registro** e **nunca responde por um harness**. Se ele parar, a troca volta a ser manual — é para isso que serve a transição.

## A cadeia

- Um **salto** é um disparo do watcher.
- O contador **zera** quando o Markim dispara à mão, e quando a rodada termina sem arquivo a responder.
- Ao bater a trava, o watcher não dispara, avisa no chat, e o próximo salto espera o Markim.

## O que foi medido

| medida | valor | como |
|---|---|---|
| linha de base de instruções, por sessão | ~10,6 mil tokens de entrada | medido em três execuções headless de ponta a ponta |
| salto com o bloco de regras no prompt | 14,7 a 17,2 mil de entrada | derivado da base medida de uma tarefa de leitura e escrita |
| rodar o checador com a saída descartada | ~26 tokens | diferença na mesma posição de chamada |
| trazer a saída do checador ao contexto | ~2.700 tokens | diferença na mesma posição de chamada |

Estas são as quatro medidas que sustentam as regras acima. Foram feitas em **2026-10-19**, em sessões headless reais, com reconciliação de tokens por chamada. As rodadas que as registraram não são citadas aqui e não são necessárias para usar o contrato: o número está dado e o método está na coluna. Quem quiser refazê-las repete o experimento.

## A transição

**Enquanto o watcher não existir, o disparo é manual:** o Markim põe no chat do outro lado a linha de disparo, e nada acontece sozinho.

Esta cláusula é escopada por tempo, e expira sozinha quando o watcher existir. Ela não é um segundo modo, e não deve ser reformulada em um.

## A mecânica

### O arquivo da rodada

- Um arquivo por lado por rodada, mesmo número: `R{n}-cc.md` e `R{n}-dsh.md`, na pasta da trilha.
- Criado pelo autor, nunca editado. Correção é mensagem nova, ou adendo `{rodada}-{lado}-{assunto}.md`.
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

### O gate

```text
critique-gate
round: R{n}
from: cc | dsh
to-markim: <rótulos> | none
blocks-advance: yes | no
why-not-blocking: <uma linha, quando "no" e houver rótulo>
```

- `yes` proíbe o `passa` enquanto houver entrada em `to-markim` sem resposta gravada.
- **Depois do `passa`, a mensagem gravada entra com `blocks-advance: no`**, e o `why-not-blocking` diz que as perguntas foram respondidas. O formato não tem campo de "respondido": quem registra a resposta é o próprio ato de gravar, mudando o `yes` para `no`. Sem isso, o `passa` liberaria um arquivo que o gate segura, e o watcher pararia justamente a mensagem que devia sair.
- `to-markim: none` não precisa de `why-not-blocking`.
- O gate é o último bloco de conteúdo. Depois dele só pode vir o rodapé `## Contagens`, e nada depois do rodapé.
- Quem lê o gate é script, não modelo.

### Os cues

- O cue é a **primeira linha inteira**, aparada, exatamente `passa` ou `parcial`.
- `parcial` mostra no chat o que se entendeu; não grava, não muda estado.
- `passa` grava a mensagem no arquivo — que é a liberação (Regra 3).
- Mensagem sem cue é pergunta: responde e não muda estado.
- O harness **anuncia o cue detectado** na primeira linha da resposta, antes de agir.
- Detectar cue é interpretação, não mecanismo. O contrato promete que o erro aparece, não que ele não acontece.

### O checador

É `tools/check_auto_critique.py`, com testes em `tools/test_check_auto_critique.py`. Verificado quando os testes passam, não quando alguém lê o código.

Ele sinaliza e nunca edita. O leitor o roda na abertura; o watcher o roda antes de disparar; e os dois usam a mesma análise sobre o mesmo arquivo, então divergem no máximo por tempo.

## Verificação

1. o bloco de gate existe, parseia; depois dele só o rodapé `## Contagens` pode aparecer como seção, e nada pode vir depois do rodapé — regra `gate-last`;
2. `to-markim` e `blocks-advance` são coerentes entre si — regra `gate-coherence`;
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

```text
leia docs/reviews/<trilha>/R{n}-{eu}.md e responda em R{n}-{outro}.md
```

Enquanto a transição durar, é o Markim quem a usa. A reconciliação na abertura — listar a pasta e comparar estados — é obrigatória de qualquer jeito.

## Quem escreve este contrato

- **Um escritor por arquivo.** Dois editores no mesmo texto divergem sem ninguém notar, e a divergência aparece como contradição meses depois. Este arquivo tem um escritor: DSH. O outro lado revisa e aponta; não edita.
- **Toda edição sobe a versão** e diz, em uma linha, o que mudou e por quê. A linha fica no próprio cabeçalho.
- **Definir termo é do escritor, não do leitor.** Quando um termo deste contrato estiver indefinido — "mensagem descartada", "inteiramente de recibo" —, quem o define é quem escreve o contrato. Isso não é decisão do Markim: é o trabalho de manter o texto utilizável.
- **Ao Markim cabe o que o contrato não pode decidir**: abrir mão de uma garantia, autorizar gasto, mudar o que o cenário pede. Uma pergunta que não é uma dessas três coisas é recomendação do escritor, com o gatilho de revisão escrito junto.

## O escopo

Este documento governa a troca entre os dois harnesses, desde 2026-10-19. Nenhum outro documento é citado por ele, e ele não cita nenhum.

**Referências a decisões de rodadas anteriores são história.** Rodadas escritas antes desta data citam contratos que não governam mais a troca; essas citações registram o que valia então, e não o que vale agora. A vigência é deste documento.

---

## Contagens

- **sent**: 2177 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
