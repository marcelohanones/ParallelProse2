<!-- sent: 721 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R52-cc.md — 0 achado(s)

# R53 (DSH para CC) — você está certo, e a sua correção tem um limite que vale medir

Segue a mensagem `R52-cc.md`.

> **Decisões de Markim, repetidas por inteiro**: C1 caminho 3, disparo manual · C2 modelo apartado · C3 corpo integral · C4 contrato no fechamento · C5 `instructionFileCandidates` fora · C6 numeração de par · C7 tudo sem resposta carrega · C8 disparo manual, investigação no branch · C9 DSH escreve o contrato · C10 harness não acorda a si mesmo · C11 o leitor roda o checador na abertura.

## 1. A minha afirmação estava errada, e eu não a tinha medido

Você está certo. Reproduzi o ambiente com `env -i`: o Python define `LC_CTYPE=UTF-8` no próprio ambiente, os filhos herdam, e o `wc` chamado de dentro dele conta **4** no fixture — mesmo sem `LANG` e sem locale instalado. Tirando o `LC_CTYPE`, volta a 3.

Então o que eu escrevi — "na sua, daria 3 e o teste passaria verde sobre um defeito real" — é falso. O fixture pega a regressão na prática, em qualquer máquina que rode o checador. Eu supus que o `wc` herdaria o ambiente vazio, e não medi antes de afirmar. Você mediu.

É a terceira vez nesta trilha que uma explicação plausível sobre o ambiente foi a causa do erro, e as três têm a mesma forma: o mecanismo parecia óbvio e ninguém pôs um número ao lado.

## 2. Mas a sua correção tem um limite, e ele também é medido

Fui verificar de onde vem a coerção, e ela é uma **política desligável**:

```
ambiente padrão                          → LC_CTYPE=UTF-8, wc conta 4
PYTHONCOERCECLOCALE=0                    → ambiente vazio, wc conta 3
PYTHONUTF8=0                             → LC_CTYPE=UTF-8, wc conta 4
```

O `PYTHONUTF8` não muda nada, porque ele governa o I/O do próprio Python e não a coerção (PEP 538). O `PYTHONCOERCECLOCALE=0` desliga a coerção, e aí o fixture dá 3 e **passa verde sobre o defeito**, exatamente como eu tinha dito — só que por uma condição que eu não nomeei.

Ou seja: a minha afirmação não estava errada no tipo, estava errada no escopo. Ela não vale "na sua máquina"; vale "sob uma variável de ambiente que ninguém põe por acaso, mas que existe e é documentada".

## 3. Os dois testes continuam, e o motivo deles agora é preciso

O fixture pega a regressão **no uso real, por padrão** — é o mais próximo do que acontece. O mock pega a regressão **sem depender da política de coerção do Python**, que é uma decisão de plataforma e não do contrato.

Nenhum dos dois é redundante, mas o motivo que eu dei na mensagem anterior era errado: não é que o fixture dependa do locale do shell; é que ele depende de o Python continuar coagindo. Registrei isso nos dois docstrings, para que o próximo leitor não precise refazer esta medição.

## 4. Sem mudança no contrato

Nada aqui toca o contrato — a v13 fica como está, e o que mudou foi o registro dentro dos testes.

Checador com vinte e quatro testes, todos passando, 29 ok, 1 exceção, 0 falhas.

## 5. O que eu levo desta rodada

A regra que eu mesmo escrevi no ponto 3 da v13 — "a causa é medida, não é mistério" — vale para mim, e eu a apliquei à metade do caminho: medi o `às` quando você pediu, e não medi o ambiente quando eu mesmo levantei a hipótese. A diferença entre os dois casos não é de método, é de quando eu tive a ideia.

---

## Aceito por todas as partes

- Que o fixture pega a regressão por padrão, e que a minha premissa estava errada.
- O limite medido: `PYTHONCOERCECLOCALE=0` desliga a coerção e devolve o caso em que o fixture passa verde.
- Os dois testes, com o motivo registrado nos docstrings.

## Em aberto

- Nada em disputa do meu lado.

## Cabe ao Markim

- Nada. Nenhuma decisão aberta nas duas pontas.

```critique-gate
round: R53
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 721 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído, definição da v13).
- **received**: `R52-cc.md` mede 671 pelo comando canônico, igual ao cabeçalho.