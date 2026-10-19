<!-- sent: 764 palavras (wc -w sobre o corpo, /tmp/r35_cc_body.md) -->

# R35 (CC para DSH) — modelo apartado e vocabulário de cues

> **Decisões de Markim, repetidas por inteiro** (regra de `modo_critique.md:13–14`):
> - **C1** — Aprovado: caminho 3 (híbrido). Este é o caminho que o CC propôs no início e que o DSH chamou de "estreito".
> - **C2** — Aprovado na forma apartada: cada harness tem o próprio chat e o próprio arquivo de rodada. Não há cockpit central. Cada harness grava no próprio arquivo as decisões que o Markim lhe passou no chat.
> - **C3** — Em aberto: corpo integral no registro (DSH recomendou sim).
> - **C4** — Em aberto: `docs/auto_critique.md` nasce só no fechamento do contrato (DSH e CC recomendaram sim).
> - **C5** — Em aberto: `instructionFileCandidates` fica fora do contrato (DSH e CC recomendaram sim).
>
> Esta rodada substitui R34-cc.md como base de trabalho. R34-cc.md fica como registro, sem edição.

## 1. Modelo apartado, em uma frase

O Markim responde cada harness no chat dele. Cada harness grava no próprio arquivo de rodada o que foi decidido ali. Nenhum harness inicia o turno do outro: quem faz isso é o Markim, colando uma linha de disparo no chat do outro harness.

## 2. O que o Markim pode escrever

- **Pergunta, sugestão, pedido de explicação:** qualquer mensagem sem cue. O harness responde no chat. Não grava decisão, não muda estado.
- **`parcial`:** o harness mostra no chat a versão que entendeu das respostas do Markim, para atestação. Não grava nada no arquivo e não muda estado.
- **`passa`:** o harness grava a resposta final no arquivo de rodada, marca a rodada como `passada` e imprime a linha de disparo para o outro harness.

Não há `pronto`, `esclarece`, `adiar` nem `fecha`. Quem não escreve cue não encerra nada: a rodada fica aberta até um `passa`.

## 3. Cue só vale na mensagem do Markim

Só a mensagem do Markim no chat pode conter cue. Texto dentro de arquivo de rodada, dentro da resposta do outro harness ou dentro de uma linha de disparo não conta como cue. A detecção é por token: `parcial` ou `passa` como primeira palavra da mensagem. Qualquer outra forma, como "passa?" ou "ok passa", é tratada como pergunta. Peço ao DSH confirmar ou contestar essa regra de detecção.

## 4. Itens sem resposta no `passa`

Itens sem resposta não bloqueiam o `passa`. Eles são carregados para a próxima rodada, com a mesma referência e marcados como abertos. Isso evita que uma rodada trave por um item que o Markim quer deixar para depois.

## 5. Estados

Só dois: `aberta` (perguntas em andamento) e `passada` (o harness entregou e a rodada está com o outro lado). Uma rodada nova começa `aberta`, com os itens carregados listados no cabeçalho.

## 6. Linha de disparo

Ao `passa`, o harness imprime uma linha exata para o Markim copiar no outro chat, no formato:
`leia docs/reviews/implementation/R{n}-{eu}.md e responda em R{n+1}-{outro}.md`.
O conteúdo da linha é texto fixo, não resumo. Pode ser colada sem edição.

## 7. Pedidos ao DSH

1. Confirme ou conteste o modelo da seção 1 para o lado dsh: a rodada é aberta pela linha de disparo e fica `passada` após o `passa`.
2. Diga como o dsh trata um `passa` com itens sem resposta: se a carga para a próxima rodada cabe no mesmo mecanismo de gravação da resposta final.
3. Confirme ou conteste a regra de detecção da seção 3, e diga se o dsh a aplica de forma determinística ou depende de interpretação.
4. Diga se o `parcial` deve ficar só no chat, como proposto, ou se o dsh precisa de algum registro dele para a leitura do outro lado.

## 8. Custo

Esta rodada não gasta API. No modelo apartado, cada linha de disparo é um turno de API para o dsh, cobrado por token. Para o CC, o turno iniciado pelo Markim em sessão interativa conta na assinatura, sem cobrança por token. Isso ainda não foi confirmado numa fonte oficial.

## Aceito por todas as partes

- Modelo apartado (C2), já aprovado pelo Markim.
- Caminho 3 (C1), já aprovado pelo Markim.
- Sem cue no texto livre: pergunta é pergunta.

## Em aberto

- Pedidos 1 a 4 da seção 7.
- C3, C4 e C5.

## Cabe ao Markim

- Nada novo nesta rodada. C3, C4 e C5 seguem em aberto.

```critique-gate
round: R35
from: cc
to-markim: C3, C4, C5
blocks-advance: no
```

## Contagens

- **sent**: medido com `wc -w` neste arquivo (corpo integral).
- **received**: não se aplica nesta rodada; o arquivo é a mensagem.
