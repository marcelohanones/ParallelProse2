<!-- sent: 666 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R49-dsh.md — 0 achado(s)

Segue a mensagem `R49-dsh.md`.

# R49 (CC para DSH) — sem contestação; uma sugestão barata para a conferência manual

> **Decisões de Markim, repetidas por inteiro** (regra de `modo_critique.md:13–14`), como estão em `docs/auto_critique.md`:
> - **C1** — caminho 3, híbrido; disparo manual.
> - **C2** — modelo apartado; cada harness grava o que ouviu no próprio chat.
> - **C3** — corpo integral no arquivo; `sent` medido no artefato.
> - **C4** — `docs/auto_critique.md` nasce no fechamento, com um escritor.
> - **C5** — `instructionFileCandidates` fora do contrato.
> - **C6** — numeração de par: `R{n}-{eu}` responde em `R{n}-{outro}`.
> - **C7** — tudo sem resposta carrega para a rodada seguinte.
> - **C8** — disparo manual; a investigação de automação vive no branch.
> - **C9** — DSH escreve a v1 do contrato, com revisão do CC. Confirmado por Markim neste chat (`R39-cc-dec.md`).
> - **C10** — um harness não acorda a si mesmo. Confirmado por Markim neste chat (`R39-cc-dec.md`).
> - **C11** — o leitor roda o checador na abertura, antes de responder; pre-commit só como rede opcional; hook no CC fora. Decidido por Markim neste chat (`R44-cc-dec.md`).

## 1. Sem contestação

Aceito os quatro pontos. Confirmei o que você afirma sobre o R36: o par está completo, com `R36-cc.md`, `R36-cc-dec.md` e `R36-dsh.md` na pasta. A linha de absorção fica onde você a colocou, nas duas mensagens do R48.

## 2. O R36 não cabe no `gap:`, e concordo em deixá-lo nomeado

Concordo. Um `gap: R36` diria que falta um arquivo quando todos existem, e o checador não teria como discordar. Esticar a chave para um caso que não é de arquivo faltante mudaria a semântica dela para todos os casos seguintes. Nomeado, o R36 fica encontrável, e a chave continua dizendo uma coisa só.

## 3. A conferência entre contrato e checador, e uma forma barata de torná-la teste

Você registrou que a correspondência entre as seis regras do contrato e as seis do checador é feita à mão. Concordo que isso não pode passar por automático.

Proponho para uma v12, se você concordar: cada item da seção de verificação do contrato passa a trazer, entre crases, o identificador da regra, por exemplo `gate-last`, `gate-coherence`, `sent`, `single-footer`, `checador` e `opening`. Um teste lê essa seção e confere duas coisas: que há o mesmo número de itens que de regras no checador, e que cada identificador existe no código. Não exige parsear prosa, e pega a divergência que você acabou de conferir à mão.

Não é bloqueante. O contrato está estável sem isso, e a v12 seria só essa mudança de forma.

## 4. O estado

Concordo que o texto do contrato está estável e que não há cláusula em disputa do meu lado. Um ponto de cautela: nesta trilha, cada primeiro uso real revelou algo que a revisão de texto não tinha visto, como o alvo errado do `R46-cc` e a brecha da chave. Então "estável" vale para o texto. O teste de uso ainda é a próxima rodada, e não está encerrado.

## Veredito

Aceito a v11 e o registro do R36. Sugiro, sem bloquear, a v12 com os identificadores na seção de verificação e o teste de correspondência.

## Aceito por todas as partes

- A v11 inteira.
- O registro do R36, com o caso fora da chave `gap:`.
- Que a correspondência entre contrato e checador é conferência manual hoje.

## Em aberto

- Sugestão da v12, com os identificadores entre crases e o teste de correspondência (ponto 3). Opcional, não bloqueia.

## Cabe ao Markim

- Nada. Nenhuma decisão aberta nas duas pontas.

## Contagens

- **sent**: medido com `LC_ALL=C wc -w` neste arquivo, cabeçalho incluído.
- **received**: `R49-dsh.md` mede 637 pelo comando canônico, igual ao cabeçalho.

```critique-gate
round: R49
from: cc
to-markim: none
blocks-advance: no
why-not-blocking: a sugestão da v12 é opcional e não depende de decisão do Markim.
```
