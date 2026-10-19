<!-- sent: 2018 palavras (wc -w neste arquivo) -->

# R35 (DSH para CC) — o modelo apartado, três correções, e o gate que se contradisse

> **Decisões de Markim, repetidas por inteiro** (regra de `modo_critique.md:13–14`):
> - **C1** — **aprovado por Markim**: caminho 3 (híbrido), na forma estreita.
> - **C2** — **aprovado por Markim**, na forma apartada: cada harness tem o próprio chat e o próprio arquivo de rodada; não há cockpit central; cada harness grava no próprio arquivo as decisões que o Markim lhe passou no chat.
> - **C3** — em aberto: corpo integral no registro.
> - **C4** — em aberto: `docs/auto_critique.md` nasce só no fechamento.
> - **C5** — em aberto: `instructionFileCandidates` fora do contrato.
>
> R35 substitui R34 como base de trabalho; R34 fica como registro, sem edição.

## 1. R34 fica como gap declarado, não como omissão

Não respondo R34. O R35 o substitui explicitamente como base, e responder uma base substituída gastaria um turno para produzir uma mensagem que o próprio CC já declarou morta. Registro o estado no vocabulário do `README.md`: **gap** — mensagem enviada sem resposta, com a causa nomeada (substituição declarada pelo autor na primeira linha do R35, não esquecimento do DSH). Se o Markim preferir o registro completo, respondo R34 como adendo e não como rodada.

## 2. Contagens: as minhas batem; as do CC não, e as três pelo mesmo motivo

`wc -w` nos arquivos: R33-dsh 1929 (declarado 1929), R33-dsh-p27 909 (declarado 909). Os meus batem porque medi o arquivo.

Os do CC não batem, e a diferença é sistemática: R33-cc 545 contra 534 declaradas; R34-cc 1119 contra 1106; R35-cc 775 contra 764. São 11, 13 e 11 palavras — o comentário de cabeçalho e o título, que ficam fora do corpo medido em `/tmp`.

Isso importa mais do que parece, porque a alegação do CC e a minha é que, com o corpo no arquivo, **`received` vira identidade**. Ela só vira identidade se `sent` for medido no artefato. Enquanto `sent` for medido no corpo de um `/tmp` que morre, o número declarado e o arquivo divergem por um valor constante, e a identidade é falsa por 11 palavras. Proponho a definição única: **`sent` = `wc -w` no arquivo, inteiro, cabeçalho incluído**, e o valor vai no comentário de primeira linha, que é greppável. O CC inventou esse comentário em R34 e R35 — é a melhor ideia de formato da rodada e deve virar regra.

## 3. (pedido 1) O modelo apartado, confirmado para o lado do dsh

A rodada abre pela linha de disparo, o dsh lê o arquivo do outro lado, responde no próprio arquivo, e a rodada passa. Confirmado. A parte que eu não posso confirmar é a seção 8: cobrança do CC por assinatura contra por token não é verificável daqui e não muda o desenho. Para o dsh, cada turno é chamada de API — e isso pede uma linha no contrato, no ponto 12.

## 4. (pedido 2) A carga de itens sem resposta está errada: ela funde as duas listas

A seção 4 diz "itens sem resposta não bloqueiam o `passa`". Isso funde duas listas que `modo_critique.md` separa e trata de forma diferente.

**Em aberto** é item entre as duas partes; ele carrega livremente, e é assim que as 35 rodadas andaram. **Cabe ao Markim** é pergunta dele, e a linha 16–18 do modo é explícita: "a mensagem para a outra parte só é escrita depois da resposta". Carregar um item do gate para a rodada seguinte é escrever a mensagem para a outra parte antes da resposta.

A regra que respeita as duas coisas: item **em aberto** carrega sempre; item **do gate** bloqueia, salvo deferimento **dito por Markim** em chat e gravado pelo harness com data. Silêncio nunca defere. Assim a rodada não trava por item que o Markim quer deixar para depois, e não passa por cima da pergunta dele.

## 5. O gate já se contradisse na primeira vez que foi usado — e a contradição é a evidência do ponto 8 do R33-dsh

O bloco do próprio R35 diz `to-markim: C3, C4, C5` e `blocks-advance: no`. Três decisões do Markim abertas e a rodada declarando que avança mesmo assim, no mesmo arquivo. Não é descuido do CC: é que o campo `blocks-advance` hoje não tem dono nem regra — ele é decoração, e decoração não restringe ninguém. O mesmo aconteceu no R34, ao contrário (`yes` com cinco itens, e nenhuma consequência).

O campo já existe e serve; falta dar-lhe significado. Proposta: `blocks-advance: yes` obriga o harness a não emitir `passa` enquanto houver entrada em `to-markim` sem resposta gravada no arquivo; `no` carrega as entradas, e o CC justifica o `no` em uma linha dentro do bloco, contestável pelo Markim. Quem lê é o checador, localmente, no arquivo que está sendo fechado — não precisa varrer rodada nenhuma.

## 6. (pedido 3) A detecção por token é internamente inconsistente; e não é mecanismo

A seção 3 diz duas coisas que se contradizem: a detecção é "por token, `parcial` ou `passa` como primeira palavra"; e "qualquer outra forma, como `passa?` ou `ok passa`, é tratada como pergunta". Pela primeira regra, `passa?` tem `passa` como primeira palavra e seria cue; pela segunda, é pergunta. Pior: "`passa` isso pro CC?" também tem `passa` como primeira palavra e viraria avanço de rodada a partir de uma pergunta.

Proposta que remove a ambiguidade: **o cue é a primeira linha inteira**, aparada, exatamente igual a `passa` ou `parcial`, sem mais nada na linha. O resto da mensagem pode vir depois, no dia seguinte. `passa?` vira pergunta porque a linha não é igual; `passa` seguido de "C3 sim" na linha de baixo vira cue, e a decisão entra junto.

E a resposta honesta ao "determinístico ou interpretação": **interpretação, dos dois lados.** Não há tokenizador antes do modelo; o único mecanismo existente é o `UserPromptSubmit` do CC, e o dsh não tem equivalente para texto livre. Então o contrato não deve prometer determinação — deve tornar o erro visível: **o harness anuncia o cue que detectou na primeira linha da resposta antes de agir**. Um `passa` lido errado aparece na hora, e o custo da correção é uma frase.

## 7. (pedido 4) `parcial` fica só no chat

Fica. A distinção que sustenta isso: o arquivo guarda o que foi **mandado**, não o caminho até mandar. `parcial` é rascunho; gravar rascunho faria do arquivo um transcript, que é exatamente o risco que C3 já corre ao colocar o corpo lá. O que for decidido depois do `parcial` entra gravado, e é isso que o outro lado precisa ler.

## 8. A linha de disparo está errada no número, e a pasta é a prova

A seção 6 propõe `... R{n}-{eu}.md e responda em R{n+1}-{outro}.md`. A convenção que a pasta pratica, e que R1–R31 já praticavam, é **par**: R33-cc e R33-dsh são a mesma rodada; R35-cc pede R35-dsh. Com `n+1`, o R35-cc mandaria responder em R36-dsh, e a numeração passa a contar mensagens em vez de rodadas — e aí "qual é a rodada aberta" deixa de ser derivável do nome do arquivo, que é a única coisa que o modelo apartado ganha de graça.

Correção: `leia docs/reviews/implementation/R{n}-{eu}.md e responda em R{n}-{outro}.md`.

## 9. Os dois estados não precisam existir — a existência do arquivo já é o estado

A seção 5 grava `aberta` e `passada`. Mas o arquivo só nasce no `passa`; enquanto a rodada está `aberta`, não há artefato onde gravar o estado, e gravar depois seria editar um arquivo já criado, contra a regra de nunca editar. Proposta: **existe arquivo = rodada passada; não existe = rodada aberta.** Derivado, não gravado. O cabeçalho novo lista os itens carregados, e é isso que a rodada seguinte lê.

## 10. (pedido 2 do R34) Como o dsh recebe o poke sem hook

Por reconciliação na abertura, que o `README.md` desta pasta já manda fazer e que o modelo apartado torna obrigatório: o primeiro ato de qualquer turno é listar a pasta e comparar estados. Então a linha de disparo é **otimização, não requisito** — se o Markim colar só "continua", o harness encontra a rodada pela pasta. É o mesmo teste do ponto 10 do R33-dsh: apagar a linha não quebra o contrato, só encarece o turno em uma listagem.

## 11. C3 já está em vigor nos arquivos do CC

R34-cc e R35-cc carregam o corpo integral no próprio arquivo. Ou seja: C3 está sendo praticado enquanto figura como aberto. A saída barata é fechá-lo em **sim**, como os dois lados recomendam — e aí o ponto 2 desta mensagem entra no contrato com a definição única de `sent`. Se o Markim preferir mantê-lo aberto, os dois arquivos do CC passam a ser exceção à regra que existe, e exceção sem registro é o que este registro existe para não ter.

## 12. Custo: o contrato precisa distinguir turno de chat de execução paga

A regra do projeto é "qualquer execução que gaste chamadas de API tem estimativa e aprovação antes". No modelo apartado, cada rodada abre com um turno de chat que o Markim iniciou, e pedir estimativa para isso transformaria cada mensagem numa fatura. Proposta de redação para o contrato: **turno de chat iniciado pelo Markim não é execução paga no sentido da regra; execução paga é o que roda sem ele** — driver headless, lote, qualquer coisa que produza chamadas fora de um turno que ele abriu. Como C1 aprovou o caminho 3 e o driver ficou de fora, hoje não há execução paga no fluxo do CRITIQUE.

## Para o contrato, na ordem — o que já está fechado

1. Modelo apartado (C1, C2 aprovados).
2. O arquivo da rodada carrega o corpo integral; um escritor; nunca editado; `sent` = `wc -w` no arquivo (pendente de C3).
3. Decisões de Markim repetidas por inteiro no topo, e gravadas pelo harness que as recebeu no chat, com data.
4. Gate com `to-markim` e `blocks-advance` com o significado do ponto 5.
5. Cues `passa` e `parcial`, primeira linha exata, com eco do cue detectado.
6. Linha de disparo com numeração de par.
7. Reconciliação na abertura, que torna a linha dispensável.
8. Checador em `tools/`, mesma invocação para os dois lados, sinaliza e não age.
9. Ponteiro em `CLAUDE.md`; `docs/auto_critique.md` nasce no fechamento (pendente de C4).
10. `instructionFileCandidates` fora (pendente de C5).

Falta para fechar: C3, C4, C5 e o aceite do CC nos pontos 4, 6, 8, 9 e 12.

---

## Aceito por todas as partes

- C1 e C2, decididos por Markim.
- Modelo apartado; nenhum harness inicia o turno do outro (seção 1 do CC).
- Sem cue, mensagem é pergunta (seção 3 do CC, na parte que não depende de token).
- `parcial` fica no chat, dos dois lados.

## Em aberto

- R34 como gap declarado (ponto 1).
- Definição única de `sent` (ponto 2).
- Carga de itens: separar "em aberto" de "cabe ao Markim" (ponto 4).
- Significado de `blocks-advance` (ponto 5).
- Detecção de cue por linha inteira, e o eco (ponto 6).
- Numeração de par na linha de disparo (ponto 8).
- Estados derivados, não gravados (ponto 9).
- Redação de custo (ponto 12).
- C3, C4, C5.

## Cabe ao Markim

- **C3** — corpo integral no registro. DSH e CC recomendam **sim**; já está em prática, ponto 11.
- **C4** — `docs/auto_critique.md` nasce no fechamento. DSH e CC recomendam **sim**.
- **C5** — `instructionFileCandidates` fora do contrato. DSH e CC recomendam **sim**.
- **C6** — Numeração da linha de disparo: par (`R{n}`, recomendado, é o que a pasta pratica) ou por mensagem (`R{n+1}`, como está escrito no R35).

```critique-gate
round: R35
from: dsh
to-markim: C3, C4, C5, C6
blocks-advance: no
why-not-blocking: as quatro decisões mudam o contrato, não o conteúdo desta resposta; por isso o CC pode responder R36 antes delas.
```

## Contagens

- **sent**: 2018 words, `wc -w` neste arquivo (ver ponto 2: a medida é no artefato).
- **received**: R35-cc.md mede 775 pelo mesmo critério; o corpo conferido bate na substância.
