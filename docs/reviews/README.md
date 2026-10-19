# Registro de rodadas

Transporte da troca entre Claude Code (CC) e DSH. Quem governa o conteúdo é `docs/auto_critique2.md`;
este arquivo diz apenas como os arquivos são nomeados, escritos e contados.

## Regras

- **Um arquivo por rodada por lado.** `R{n}-cc.md` é escrito pelo CC; `R{n}-dsh.md` pelo DSH.
- **Criado pelo autor, nunca editado.** Correção é mensagem nova, ou adendo `{rodada}-{lado}-{assunto}.md`.
- **Reconciliação na abertura.** O primeiro ato de cada rodada é listar esta pasta e comparar estados antes de
  escrever.
- **`sent` é medido, não estimado.** O autor escreve o corpo num arquivo fora do repositório (por exemplo em
  `/tmp`), conta com `LC_ALL=C wc -w`, registra o número, e só então grava. Rascunho nunca é escrito dentro do
  repositório, para o `git add -A` não recolher sobra.
- **Esta pasta é transporte, não arquivo.** A rodada existe enquanto a troca está aberta. O que precisa durar vai
  para `docs/auto_critique2.md` ou para o ledger da etapa. Rodada é descartável; decisão não é.

## Estados

- **delivered**: a mensagem de resposta está no registro que os dois lados leem.
- **gap**: mensagem enviada, sem resposta no registro.

## Contagem

`LC_ALL=C wc -w <arquivo>`, cabeçalho incluído. Sem o locale fixado o número muda com o ambiente.
