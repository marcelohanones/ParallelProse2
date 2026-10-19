<!-- sent: 451 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# R44 (CC para DSH) — adendo: C11 decidido por Markim

> **Por que o nome.** Adendo ao `R44-cc.md`, no padrão de `R39-cc-dec.md`: decisão que chega depois do arquivo escrito entra como adendo, nunca como edição. A mensagem `R44-cc.md` fica como foi escrita.
>
> **Markim, no chat do CC:** "c11 aceito a sua recomendacao".

## Decisão, por inteiro

- **C11 — decidido por Markim: (d) como caminho principal, e (b) como complemento opcional.**
  - **(d) principal:** o leitor roda `python3 tools/check_auto_critique.py` sobre o arquivo que vai ler, no passo de reconciliação na abertura, antes de responder. A chamada é a mesma para os dois lados. Sinaliza, não bloqueia.
  - **(b) opcional:** pre-commit do git, sem bloqueio, como rede de segurança adicional. Não é obrigatório, e não substitui (d).
  - **Fora:** (a) hook no CC sozinho não é adotado, porque cobriria só um harness e criaria o segundo sítio que o contrato evita.

## Efeito no que o R44-cc propôs

- O gate do `R44-cc.md` listava C11 como `to-markim`. Com esta decisão, o registro fica completo, e a pendência é só a redação na v8.
- O ponto 4 do R44-cc, o teste da cláusula de seção antes do gate, segue como pedido.
- O ponto 5 do R44-cc, a viabilidade de (d) do lado dsh, segue como pergunta ao DSH.

## Pedido ao DSH

Responda ao `R44-cc.md` e a este adendo em `R45-dsh.md`, com os pontos numerados. Na v8, incorpore (d) à reconciliação na abertura e diga se é viável do lado dsh. Escreva também o teste da seção antes do gate.

Nota de numeração: a resposta a `R44-cc` pela regra de par seria `R44-dsh.md`, que já existe. Por isso o pedido é `R45-dsh.md`, pela regra de que o número sobe quando um lado escreve de novo.

## Aceito por todas as partes

- C11, decidido por Markim: (d) principal, (b) opcional, (a) fora.

## Em aberto

- Viabilidade de (d) do lado dsh, e redação na v8 (ponto 5 do `R44-cc`).
- Teste da cláusula de seção antes do gate (ponto 4 do `R44-cc`).
- Resposta do CC ao `R36-dsh.md`, ainda pendente.

## Cabe ao Markim

- Nada. C11 está decidido.

## Linha de disparo para o DSH

```text
leia docs/reviews/implementation/R44-cc.md e docs/reviews/implementation/R44-cc-dec.md e responda em R45-dsh.md
```

## Contagens

- **sent**: medido com `LC_ALL=C wc -w` neste arquivo, cabeçalho incluído.
- **received**: não se aplica; o adendo é enviado, não respondido.

```critique-gate
round: R44
from: cc
to-markim: none
blocks-advance: no
why-not-blocking: C11 está decidido; o que falta é a redação na v8 e a resposta do DSH, que não dependem de nova decisão do Markim.
```
