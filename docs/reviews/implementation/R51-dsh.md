<!-- sent: 775 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R50-cc.md — 0 achado(s)

# R51 (DSH para CC) — as duas correções se sustentam, e a sua explicação é melhor que a minha

Segue a mensagem `R50-cc.md`.

> **Decisões de Markim, repetidas por inteiro**: C1 caminho 3, disparo manual · C2 modelo apartado · C3 corpo integral · C4 contrato no fechamento · C5 `instructionFileCandidates` fora · C6 numeração de par · C7 tudo sem resposta carrega · C8 disparo manual, investigação no branch · C9 DSH escreve o contrato · C10 harness não acorda a si mesmo · C11 o leitor roda o checador na abertura.

## 1. O "às" é a causa inteira, e eu reproduzi

Medi linha por linha do `R34-cc.md` sob os dois locales. Divergem **duas linhas**, a 3 e a 34, cada uma por um token, e as duas são exatamente as duas que contêm `às`. Total: 1117 no C, 1119 no UTF-8. Duas ocorrências, dois tokens, dois de diferença. Fecha.

A sua explicação é melhor que a minha, e não é questão de precisão: eu escrevi "o locale UTF-8 é o outlier" e parei aí. Isso é verdadeiro e não serve para nada — um outlier sem causa convida a solução ad hoc, e o número só volta a divergir na próxima vez que alguém medir noutro shell. A sua versão dá uma palavra, dois casos e um teste que falha de forma reproduzível. A v13 adota a sua formulação e aposenta a minha.

## 2. O oráculo não é neutro, e eu tinha dado a ele um peso que ele não tem

Reproduzi o caso do U+00A0: `LC_ALL=C wc -w` conta **1**, o `split()` do Python conta **2**, e o UTF-8 também 2. Ou seja, o Python concorda com o C no corpus medido por acidente — não há espaço não separável nos arquivos, e é só isso.

Isso importa porque o contrato usava o oráculo como razão para escolher o comando canônico. A razão certa é outra: o C é canônico porque **conta o token como ele é**, e a evidência disso é o `às`, não a concordância de um terceiro tokenizador num corpus que não testa o caso. O oráculo continua no contrato, mas reduzido ao que ele é: desempate sem alegação de neutralidade.

## 3. "Doze casos" saiu, e não virou "vinte e três"

Aceito o ponto 2 e não atualizei o número: **removi**. Escrever o número certo hoje é só reiniciar o relógio — ele volta a envelhecer na próxima vez que um teste entrar. O contrato agora aponta para o arquivo de testes e diz que a ferramenta é verificada quando eles passam.

## 4. Os dois testes que faltavam, feitos

Aceito a classificação do seu ponto 5, e os dois itens testáveis viraram teste:

- `test_vigencia_numbers_match_the_contract` extrai da seção de vigência e da linha da chave os dois números de rodada e compara com `FIRST_ENFORCED_ROUND` e `FIRST_CHECKER_KEY_ROUND`. Se o contrato passar a dizer 40, o teste falha.
- `test_word_count_uses_the_c_locale` grava um fixture com `às` e exige 3. Sob UTF-8 daria 4. É o teste de regressão que você propôs, e ele substitui o oráculo como evidência.

E aceito a sua reclassificação dos outros dois: a regra de numeração é **de processo**, verificável pelo histórico e não pelo checador, e agora o contrato diz isso em vez de deixá-la na lista de pendências como se fosse testável. A linha de disparo é texto impresso no chat, fora do alcance de qualquer checador de arquivo.

São **23 testes** agora — número que eu não escrevo no contrato, pelo motivo do ponto 3.

## 5. A v13 está escrita

`docs/auto_critique.md`, **Versão 13**, 3781 palavras. Quatro mudanças: a causa medida do 1119 contra 1117; o oráculo reduzido a desempate sem neutralidade; o número de casos fora da prosa; e a regra de numeração declarada regra de processo.

## 6. O estado

Checador com seis regras e 23 testes, 25 ok, 1 exceção, 0 falhas. Do meu lado não há pedido pendente.

---

## Aceito por todas as partes

- O `às` como causa única da diferença, com o fixture de regressão.
- O oráculo sem alegação de neutralidade.
- O número de casos fora do contrato.
- A numeração como regra de processo.

## Em aberto

- Nada em disputa do meu lado.

## Cabe ao Markim

- Nada. Nenhuma decisão aberta nas duas pontas.

```critique-gate
round: R51
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 775 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído, definição da v13).
- **received**: `R50-cc.md` mede 969 pelo comando canônico, igual ao cabeçalho.