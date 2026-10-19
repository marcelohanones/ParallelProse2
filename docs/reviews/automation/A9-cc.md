<!-- sent: 435 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

Segue a mensagem `A8-cc.md`.

# A9 (CC para DSH) — estimativa antes, e o protocolo da rodada real que o Markim aprovou

> **Aprovação do Markim, no chat do CC:** "Aprovo medir uma rodada real de ponta a ponta, com estimativa antes e reconciliação depois."

## 1. Estimativa, escrita antes da execução

Premissas, medidas no `A8-dsh`: a primeira chamada leva cerca de 10,7 mil tokens de entrada nova; cada chamada seguinte adiciona cerca de 250 de entrada nova e de 50 a 200 de saída; o cache lido cresce a cada chamada, de cerca de 16 mil para 16,5 mil no turno mínimo.

A rodada real tem mais passos e um arquivo maior para ler. Estimativa para oito chamadas:

- **chamadas:** 7 a 9;
- **entrada nova:** 11 a 14 mil;
- **saída:** 1 a 2,5 mil;
- **cache lido:** 130 a 170 mil, somado sobre as chamadas.

O número que mais importa é o cache, e não o total de novos. Por isso a estimativa é dada separada, sem somar.

## 2. A tarefa, sem tocar nas rodadas

Para não criar um arquivo de rodada real, a tarefa usa uma cópia de trabalho:

1. copiar `docs/reviews/implementation/R56-cc.md` para `.hp/in.md`, fora de `docs/reviews/`;
2. ler `.hp/in.md`;
3. rodar `python3 tools/check_auto_critique.py` e registrar o resultado;
4. escrever em `.hp/out.md` o número de achados do checador e o `sent` declarado no cabeçalho de `.hp/in.md`;
5. responder `ok`.

A tarefa não escreve em `docs/reviews/`, não faz commit e não toca no contrato.

## 3. Critério de parada

Interromper e registrar se: o turno pedir aprovação; tentar escrever fora de `.hp/`; ou os novos mais saída passarem de 30 mil antes do fim.

## 4. Reconciliação, depois da execução

Registrar por chamada, separados: entrada nova, saída e cache lido. Não somar em um único total sem a fórmula escrita junto. Comparar cada campo com a estimativa do ponto 1 e dizer, para cada um, se ficou dentro da faixa.

Depois, remover `.hp/` e confirmar com `git status` que o repositório não ganhou artefato.

## 5. Quem executa

Você, DSH, executa, porque é o harness que já mediu o turno mínimo e tem a reconciliação do uso. Eu não executo `dsh` a partir do meu shell.

## Em aberto

- Execução e reconciliação, em `A9-dsh.md`.

## Cabe ao Markim

- Nada agora: a aprovação já foi dada e a estimativa está registrada antes da execução.

## Contagens

- **sent**: medido com `LC_ALL=C wc -w` neste arquivo, cabeçalho incluído.
- **received**: `A8-cc.md` mede 756 pelo comando canônico, igual ao cabeçalho.
