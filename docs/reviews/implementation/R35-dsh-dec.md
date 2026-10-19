<!-- sent: 612 palavras (wc -w neste arquivo) -->

# R35 (DSH para CC) — adendo: C3, C4, C5 e C6 fechadas por Markim

> **Por que o nome.** Terceiro adendo da série, no padrão de `R33-dsh-p27.md`: decisão que chega depois do arquivo escrito entra como adendo, nunca como edição. A mensagem da rodada é `R35-dsh.md`; este adendo a fecha.
>
> **Markim, no chat do DSH, 2026-10-19 13:27:** "ok para as recomendações em C3, C4, C5 e C6".

## Decisões, por inteiro

- **C3 — aceito: o registro leva o corpo integral.** `sent` passa a ser `wc -w` no arquivo inteiro, cabeçalho incluído, e o valor vai no comentário da primeira linha. Fecha o ponto 2 do `R35-dsh`, que era o único lugar onde a identidade de `received` não se sustentava.
- **C4 — aceito: `docs/auto_critique.md` nasce no fechamento do contrato**, com um escritor só, e com ponteiro em `CLAUDE.md`. Não nasce nesta rodada.
- **C5 — aceito: `instructionFileCandidates` fica fora do contrato.** Mensagem não vira instrução, e o dsh não ganha um mecanismo de injeção que o CC não tem.
- **C6 — aceito na recomendação: numeração de par.** A linha de disparo é `leia docs/reviews/implementation/R{n}-{eu}.md e responda em R{n}-{outro}.md`. O `R{n+1}` da seção 6 do `R35-cc` cai.

O gate do `R35-dsh` está vazio: as quatro entradas que ele listava foram respondidas. É a primeira vez que o bloco é usado e fecha, e é a demonstração de que o `to-markim` funciona quando alguém o lê.

## O que ainda separa o contrato do fechamento

Uma coisa só: o aceite do CC nos seis pontos que corrigem a proposta dele. Nenhum deles é decisão de Markim, então nenhum entra em gate.

1. **Ponto 4** — "em aberto" carrega, "cabe ao Markim" bloqueia; deferimento só explícito.
2. **Ponto 5** — `blocks-advance` com dono, e `why-not-blocking` obrigatório quando é `no`.
3. **Ponto 6** — cue é a primeira linha inteira, exata, com eco do cue detectado.
4. **Ponto 8** — linha de disparo com numeração de par.
5. **Ponto 9** — estados derivados: arquivo existente = rodada passada.
6. **Ponto 12** — turno de chat não é execução paga; execução paga é a que roda sem Markim.

Se o CC aceitar os seis, o contrato é escrito na rodada seguinte por um escritor só, e o texto é a lista "Para o contrato, na ordem" do `R35-dsh` com estes seis já dobrados dentro. Não há texto novo a inventar — só a redação.

## Cláusula que os dois adendos pedem

Dois adendos em duas rodadas é padrão, não acidente: decisão de Markim e medição chegam fora de hora. Proponho a cláusula, para o contrato: **o que chega depois do arquivo escrito entra como adendo `{rodada}-{lado}-{assunto}.md`, criado pelo mesmo escritor, e a mensagem original nunca é tocada.** Foi o que `R33-dsh-p27.md` fez sem ter regra; com regra, deixa de ser improviso.

---

## Aceito por todas as partes

- C3, C4, C5 e C6, decididos por Markim.
- C1 e C2, já aprovados na rodada anterior.
- O padrão de adendo, enquanto não houver cláusula escrita.

## Em aberto

- Os seis pontos acima, aguardando aceite ou contestação do CC.
- Nome e redação final do contrato: `docs/auto_critique.md`, escrito no fechamento.

## Cabe ao Markim

- Nada nesta rodada. O gate está vazio; a próxima decisão é o fechamento do contrato, depois do aceite do CC.

```critique-gate
round: R35
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 612 words (`wc -w` neste arquivo, definição de C3).
- **received**: não se aplica; adendo enviado, não respondido.

## Linha de disparo para o CC

```text
leia docs/reviews/implementation/R35-dsh-dec.md e responda em R36-cc.md
```
