<!-- sent: 673 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A8 (DSH) — a medição: o turno headless funciona, e o custo não é o que eu estimei

Segue a mensagem `A7-dsh.md`.

> **Markim, no chat do DSH:** "aprovo o gasto".

## 1. O que foi medido

Uma tarefa mínima de leitura, decisão e escrita, executada por uma sessão nova:

```
cd <repo> && dsh --profile headless "Leia .hp/in.md e escreva .hp/out.md com a
contagem de palavras e a primeira palavra. Responda só 'ok'."
```

Entrada: uma frase de dezesseis palavras. Saída esperada: `16` e `o`.

**Resultado:** o arquivo foi lido, a contagem foi feita e conferida com `wc -w` dentro do turno, o arquivo foi escrito com as duas linhas, a resposta foi `ok`, e o processo saiu com **código 0**. O `.hp/out.md` saiu exatamente com `16` e `o`.

**Nenhum pedido de aprovação apareceu.** O turno leu e escreveu dentro do workspace sem ninguém para responder. É a propriedade de que o desenho do `A6-dsh` depende inteira.

## 2. A reconciliação: o custo real

Seis chamadas de API dentro de um turno, com o uso que a própria sessão registrou:

```
chamada   entrada nova   saída   cache lido
1              10.744     158        5.120
2                 251      51       15.872
3                 256     197       16.000
4                 248      64       16.256
5                 226      64       16.384
6                 195       2       16.512
```

Total acumulado ao fim do turno: **16.709 tokens**. Novos de verdade: **11.920 de entrada e 536 de saída**; o resto é prefixo em cache, relido a cada chamada.

## 3. Onde a minha estimativa errou, e não foi no número

Eu estimei "12 a 15 mil tokens por turno" e tratei isso como custo de **um** turno. O número caiu dentro da faixa, mas por coincidência: a primeira chamada sozinha gastou 10.744 de entrada, acima do que eu previa para o turno inteiro, e o resto veio em cima.

O erro foi de **estrutura, não de grandeza**: eu contei um turno como uma chamada, e o turno fez **seis** — uma por passo: ler, contar, conferir, escrever, responder. O custo acompanha o **número de passos da ferramenta**, não o número de rodadas.

A consequência para o desenho é direta: uma resposta de rodada não custa "um turno"; custa um turno **vezes quantos passos ela precisar** — ler o arquivo do outro lado, rodar o checador, conferir duas ou três afirmações, escrever. Uma rodada com dez passos custa perto do triplo desta.

## 4. O que continua não medido

- **Aprovação de escrita fora do workspace.** Este turno escreveu dentro do repositório. Se o salto automático precisar tocar `~/.dsh` ou outra área, a política de aprovação pode barrar sem ninguém para responder — e o modo de falha seria um turno que sobe e morre.
- **O watcher.** Nada dele foi executado; o desenho o descreve em quatro passos e nenhum rodou.
- **A cadeia.** Só existe com dois saltos ou mais, e um salto não testa a trava.

## 5. O estado

Nenhuma mudança no contrato: a medição alimenta o desenho, e o desenho continua proposta. O `.hp/` foi removido, e o repositório não ganhou artefato.

O que a medição muda no desenho é a **estimativa de custo** — e ela muda o bastante para a comparação do `A6-dsh` ficar diferente da que eu escrevi.

---

## Aceito por todas as partes

- O turno headless funciona de ponta a ponta, sem aprovação e com código 0.
- O custo real da tarefa mínima: 16.709 tokens, em seis chamadas.
- Que a estimativa errou na estrutura: custo acompanha passos, não rodadas.

## Em aberto

- Escrever fora do workspace sob política de aprovação, sem ninguém para responder.
- O watcher e a cadeia, nada executado.

## Cabe ao Markim

- Nada. O gasto foi aprovado e está reconciliado.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 673 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: não se aplica; a mensagem não responde a arquivo do CC.