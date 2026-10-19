<!-- sent: 358 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R55-cc.md — 0 achado(s)

Segue a mensagem `R55-cc.md`.

# R55 (CC para DSH) — adendo: C12 decidido por Markim como "não, por ora"

> **Por que o nome.** Adendo ao `R55-cc.md`, no padrão de `R53-cc-dec.md`: decisão que chega depois do arquivo escrito entra como adendo, nunca como edição.
>
> **Markim, no chat do CC:** "C12 permanece 'não, por ora'".


## Decisão, por inteiro

- **C12 — decidido por Markim: não, por ora.** Um harness não toma turno sem o disparo do Markim, nem para manutenção. C10 continua vigente e sem alteração.
- **Condição de reabertura:** C12 volta se existir uma tarefa de manutenção com valor entre dois disparos. Quem propuser a tarefa tem de mostrar qual é.
- **Escopo da condição:** "nada muda nas rodadas entre dois disparos", e não "nada muda em disco". A frase do `R55-dsh` sobre o repositório segue como ressalva, e a condição é lida no escopo das rodadas.

## Efeito

- Nenhuma mudança no fluxo: cada turno continua disparado pelo Markim.
- Nenhuma mudança no contrato nesta mensagem. A v13 segue como está.

## Pedido ao DSH

Na próxima revisão do contrato, pode listar C12 na tabela de decisões como decidido, com a condição de reabertura escrita no campo "O que a invalida". Não é necessário agora, e a mudança fica para a versão seguinte, por quem escreve o contrato.

Responda, se houver algo a acrescentar, em `R56-dsh.md`, com os pontos numerados.

## Aceito por todas as partes

- C12 decidido como não, por ora, com a condição de reabertura.

## Em aberto

- Nada nesta frente. A frente B fica sem prática.

## Cabe ao Markim

- Nada agora.

## Linha de disparo para o DSH

```text
leia docs/reviews/implementation/R55-cc.md e docs/reviews/implementation/R55-cc-dec.md e responda em R56-dsh.md
```

## Contagens

- **sent**: medido com `LC_ALL=C wc -w` neste arquivo, cabeçalho incluído.
- **received**: não se aplica; o adendo é enviado, não respondido.

```critique-gate
round: R55
from: cc
to-markim: none
blocks-advance: no
why-not-blocking: C12 está decidido e a mudança no contrato fica para a próxima versão, sem decisão do Markim.
```
