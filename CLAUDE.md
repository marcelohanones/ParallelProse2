# CLAUDE.md — ParallelProse2

## Fonte

O documento de migração (`docs/documento_de_migracao.md`) dá as regras iniciais. Cada etapa tem um ledger próprio, mais específico, que registra as decisões tomadas depois: quando um ledger contradiz o documento de migração, o ledger vale. Para ingestão, o ledger é `docs/ingest.md`. Para o contrato entre o retriever e a IA editorial, o ledger é `docs/contract_retriever_editorial.md`, acordado via CRITIQUE e não por uma etapa só.

## Escopo de leitura

Não leia o projeto ParallelProse: código, documentos, nem a memória de harness dele. As decisões de arquitetura de lá não valem aqui. Uma citação a ele num documento deste repositório é contexto e não autoriza ir buscá-la. Em caso de dúvida, pare e pergunte antes de ler.


## O projeto

Dois livros lado a lado. A execução é de um livro por vez; a comparação acontece na IA editorial. O produto é uma prosa que mostra convergência, divergência e o que só um autor sustenta, com endereço no texto original. O crédito vem de recusar o que não se sustenta, não de achar acordo.

## Dois grafos, com fronteira escrita

- **Retriever:** busca por regras, de forma determinística. Testemunha: devolve o trecho com endereço e o rastro da busca. Não interpreta, não sintetiza, não julga suficiência.
- **IA editorial:** julga o sentido, escreve a prosa, confere cada afirmação contra o material e decide pedir nova rodada.
- O retriever não guarda estado entre chamadas. O que ele precisa da rodada anterior vem no pedido.
- Não há segundo juiz. Ferramentas usadas pela IA editorial fazem parte do papel dela.

## Regras de evidência

- Evidência é o trecho que a busca devolve do livro, nunca texto do modelo.
- Um endereço posicional é atribuído uma única vez, na ingestão. Nenhum outro componente cria endereços.
- Juízo se relata; porta é mecânica. Uma checagem mecânica pode recusar, mas não decide sentido.

## Processo

- **Modo CRITIQUE:** descrito em `docs/modo_critique.md`. Antes de qualquer execução paga, numerar os pontos, verificar a afirmação da outra parte, estimar o custo e fixar a barra. Nada que pertence ao Markim é decidido pelo CC.
- **Orçamento antes de gasto:** qualquer execução que gaste chamadas de API tem estimativa e aprovação antes, com reconciliação depois.
- **Redesenho por causa:** agrupar problemas por causa, ordenar pelo fluxo, tratar um item por vez, com critérios checáveis sem modelo.
- **Medição não é ponto de partida:** ela só volta depois que o problema de produção estiver definido em termos próprios.
- **Premissa escrita junto de cada decisão:** cada decisão registra o que a tornou necessária e o que a invalidaria.

## Harness memory

`docs/harness_memory_design.md` registra o desenho acordado para compartilhar memória entre Claude Code e dsh — um escritor por arquivo, três camadas, limites medidos. Leia antes de mudar como qualquer um dos dois harnesses guarda ou carrega memória.
