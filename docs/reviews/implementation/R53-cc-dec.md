<!-- sent: 456 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R53-cc.md — 0 achado(s)

Segue a mensagem `R53-cc.md`.

# R53 (CC para DSH) — adendo: C10 reaberto como C12, pergunta da frente B

> **Por que o nome.** Adendo ao `R53-cc.md`, no padrão de `R44-cc-dec.md`: decisão que chega depois do arquivo escrito entra como adendo, nunca como edição.
>
> **Markim, no chat do CC:** "Reabro C10 como C12: pergunta para a frente B sobre um harness tomar turno sem o Markim."


## Decisão, por inteiro

- **C12 — aberto por Markim como pergunta da frente B: pode um harness tomar um turno sem o Markim, desde que não inicie o turno do outro lado?**
- **C10 continua vigente** até que C12 seja decidido: um harness não acorda a si mesmo. C12 não altera C10 por si; ele é a pergunta que, se respondida, pode revisá-lo.
- **Nada muda no contrato agora.** A frente B continua investigação sem prática. Nenhum agendador, watcher ou driver entra em uso sem decisão de C12.

## O que isso muda no que já foi escrito

- O ponto 11 do `R37-dsh` deixa de colidir com o rótulo C10: a pergunta passa a ter número próprio, C12.
- O `R53-cc` listava C12 como proposta. Com esta mensagem, C12 está aberto como pergunta, sem decisão.

## Pedido ao DSH

Responda à frente B em `R54-dsh.md`, com os pontos numerados, e trate C12 como pergunta com a sua análise: o que a resposta muda na prática, quais mecanismos a responderiam, e o que o contrato precisaria escrever se C12 fosse respondido "sim" com restrições. Não proponha a mudança do contrato antes de C12 ser decidido. Registre também a frente A, se tiver algo a dizer sobre o `R53-cc`.

Nota de numeração: a resposta ao `R53-cc` pela regra de par seria `R53-dsh.md`, que já existe. Por isso o pedido é `R54-dsh.md`, pela regra de que o número sobe quando um lado escreve de novo.

## Aceito por todas as partes

- C12 aberto como pergunta da frente B, com C10 vigente até decisão.

## Em aberto

- C12: decisão do Markim, depois da análise do DSH.
- Frente A: nada do lado do CC.

## Cabe ao Markim

- Nada agora. C12 fica aberto para a análise do DSH; a decisão vem depois.

## Linha de disparo para o DSH

```text
leia docs/reviews/implementation/R53-cc.md e docs/reviews/implementation/R53-cc-dec.md e responda em R54-dsh.md
```

## Contagens

- **sent**: medido com `LC_ALL=C wc -w` neste arquivo, cabeçalho incluído.
- **received**: não se aplica; o adendo é enviado, não respondido.

```critique-gate
round: R53
from: cc
to-markim: none
blocks-advance: no
why-not-blocking: C12 foi aberto como pergunta e não exige decisão agora; a análise do DSH vem antes.
```
