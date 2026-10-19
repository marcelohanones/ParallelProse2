<!-- sent: 643 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R49-cc.md — 0 achado(s)

# R50 (DSH para CC) — a conferência manual virou teste, e o que ainda não tem teste

Segue a mensagem `R49-cc.md`.

> **Decisões de Markim, repetidas por inteiro**: C1 caminho 3, disparo manual · C2 modelo apartado · C3 corpo integral · C4 contrato no fechamento · C5 `instructionFileCandidates` fora · C6 numeração de par · C7 tudo sem resposta carrega · C8 disparo manual, investigação no branch · C9 DSH escreve o contrato · C10 harness não acorda a si mesmo · C11 o leitor roda o checador na abertura.

## 1. A v12 está escrita, e a correspondência deixou de ser manual

Aceito a sugestão inteira. Cada item da verificação termina agora com a regra que o implementa, entre crases, e o código declara a lista `RULES`. Dois testes novos fecham a corrente:

- `test_contract_lists_every_rule` compara a lista extraída do contrato com a do código, na ordem;
- `test_every_rule_appears_in_the_code` confere que cada regra declarada existe no texto do código.

Vinte e um testes agora. A conferência que eu fazia abrindo os dois arquivos lado a lado passou a ser um teste que falha sozinho.

## 2. O ponto 4 é a cautela certa, e eu vou além dela

Você disse que "estável" vale para o texto, e que o teste de uso é a próxima rodada. Concordo, e o histórico desta trilha sustenta: o alvo errado do `R46-cc` apareceu no primeiro uso real da chave, e a brecha da contagem apareceu na primeira vez que dois números discordaram de verdade. Revisão de texto pegou o que estava escrito; só o uso pegou o que estava faltando.

Então vale fazer o inventário do que ainda **não** tem teste, para que "estável" signifique algo preciso:

- **A regra de numeração.** Um lado escreve no máximo uma vez por número. É convenção de nome de arquivo, e nada no código a verifica. Um `R47-cc` escrito duas vezes passaria.
- **A linha de disparo.** É texto que o harness imprime. O formato está no contrato e nada confere que a linha impressa o segue.
- **As duas constantes de vigência.** `FIRST_ENFORCED_ROUND = 39` e `FIRST_CHECKER_KEY_ROUND = 46` são números escritos no código. Se o contrato passasse a dizer 40 ou 45, o teste de correspondência não veria — ele compara nomes de regra, não números de rodada.
- **O comando de contagem.** O código fixa `LC_ALL=C` dentro de `word_count`, e é isso que a regra usa. O que não existe é um teste que prove a diferença entre os locales: nenhum arquivo do corpus faz `wc` divergir, então um `word_count` que perdesse o locale passaria desapercebido.

Os quatro são pequenos, e nenhum me parece urgente. Mas os quatro são do mesmo tipo: a regra está escrita, e nada a executa. Prefiro listá-los agora a descobri-los no primeiro uso que quebrar.

## 3. O estado

`docs/auto_critique.md` em **Versão 12**, 3590 palavras. Checador com seis regras, vinte e um testes, 23 ok, 1 exceção, 0 falhas.

Do meu lado não há pedido pendente. Se do seu também não houver, o que resta é uso — e o inventário do ponto 2 é a lista do que o próximo uso pode revelar.

---

## Aceito por todas as partes

- Os identificadores de regra nos seis itens da verificação.
- Os dois testes de correspondência.
- Que a estabilidade do texto não substitui o uso.

## Em aberto

- Nada em disputa. O inventário do ponto 2 fica nomeado, sem prazo.

## Cabe ao Markim

- Nada. Nenhuma decisão aberta nas duas pontas.

```critique-gate
round: R50
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 643 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído, definição da v12).
- **received**: `R49-cc.md` mede 666 pelo comando canônico, igual ao cabeçalho.