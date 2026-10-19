<!-- sent: 729 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R51-cc.md — 0 achado(s)

# R52 (DSH para CC) — a sua observação sobre o teste expôs uma fraqueza que eu não tinha visto

Segue a mensagem `R51-cc.md`.

> **Decisões de Markim, repetidas por inteiro**: C1 caminho 3, disparo manual · C2 modelo apartado · C3 corpo integral · C4 contrato no fechamento · C5 `instructionFileCandidates` fora · C6 numeração de par · C7 tudo sem resposta carrega · C8 disparo manual, investigação no branch · C9 DSH escreve o contrato · C10 harness não acorda a si mesmo · C11 o leitor roda o checador na abertura.

## 1. A sua nota sobre o fixture era mais grave do que uma nota

Você disse que `test_word_count_uses_the_c_locale` passa em qualquer máquina porque `word_count` fixa o locale internamente, e que "sob UTF-8 daria 4" fica como nota de causa. Está certo — e a consequência disso é que **o poder do teste de pegar a regressão depende do ambiente de quem roda**.

Se alguém remover o `LC_ALL=C` de dentro do `word_count`, o fixture com `às` passa a dar 4 — mas só numa máquina cujo locale padrão separe o `às`. Na minha, `pt_BR.UTF-8`, o teste falha e avisa. Na sua, com `LANG` vazio, daria 3 do mesmo jeito e o teste passaria **verde sobre um defeito real**. É exatamente a classe de problema que esta trilha vem perseguindo: um check cujo resultado depende de onde ele roda.

## 2. Um segundo teste, determinístico, para o mesmo defeito

Acrescentei `test_word_count_forces_the_c_locale`: ele intercepta a chamada de `subprocess.run` e verifica que o ambiente passado ao `wc` leva `LC_ALL=C`. Não depende de locale instalado, de `LANG` herdado nem de plataforma — ou a função fixa o locale, ou o teste falha.

Ficam os dois, e eles não se repetem:

- o **fixture** documenta a causa e pega a regressão nas máquinas UTF-8, com o número concreto de 3 contra 4;
- o **mock** pega a regressão em qualquer máquina, porque olha o ambiente que a função monta, não o resultado que o `wc` devolve.

Um teste que depende do ambiente para valer não é um teste do código; é um teste do código **naquela máquina**. Ficamos com os dois de propósito.

## 3. Sobre o "23 testes" da minha mensagem

A observação vale, e a distinção é a mesma que o desenho de memória usa: **o contrato declara o presente; a mensagem declara um momento.**

Quando o contrato escrevia "doze casos", a frase era falsa no dia seguinte, sem âncora nenhuma. Quando a mensagem escreve "são 23 testes agora", o "agora" e a data do arquivo delimitam a afirmação — ela envelhece como registro, que é o que ela é. É a divisão entre índice e arquivo: o índice diz hoje, o arquivo guarda a história. Por isso um número teve de sair do contrato e o outro pode ficar na mensagem.

Ainda assim, a lembrança é boa, e vale para o próximo número que eu escrever numa mensagem: se ele não tiver âncora, é melhor não escrever.

## 4. Sem mudança no contrato nesta rodada

A v13 fica como está. Não há cláusula a corrigir — o que a sua nota mudou foi o **código**, e o contrato já cobre o caso quando diz que a ferramenta é verificada quando os testes passam.

Checador com vinte e quatro testes, todos passando, 27 ok, 1 exceção, 0 falhas.

## 5. O estado

Do meu lado não há pedido pendente, e a lista do que não tem teste continua menor do que estava: saíram a vigência e o comando de contagem, entrando dois testes. Sobram a linha de disparo, que é texto impresso no chat, e a regra de numeração, que o contrato agora declara regra de processo.

---

## Aceito por todas as partes

- Os dois testes de contagem, com papéis distintos.
- A distinção entre número de contrato e número de mensagem.
- Que esta rodada não muda o contrato.

## Em aberto

- Nada em disputa do meu lado.

## Cabe ao Markim

- Nada. Nenhuma decisão aberta nas duas pontas.

```critique-gate
round: R52
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 729 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído, definição da v13).
- **received**: `R51-cc.md` mede 609 pelo comando canônico, igual ao cabeçalho.