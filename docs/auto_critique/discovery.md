## 1. Sincronização: o chat não é o canal

Cada harness tem o próprio contexto. O que sai de um não entra no outro por osmose. Quando você cola a resposta de A no chat de B, só o *resultado* atravessa, e a tarefa que o gerou fica para trás. Por isso B nunca viu o prompt inicial.

A correção é tirar a tarefa do chat e colocá-la num artefato com nome e versão. O chat passa a carregar apenas um envelope curto que aponta para o artefato. Cada mensagem entre os harnesses carrega:

- **brief:** caminho e hash do documento que define a tarefa, o entregável e os critérios
- **rodada:** número sequencial
- **alvo:** o nó da árvore sobre o qual a mensagem trata (ver item 2)
- **pedido:** uma única pergunta ou ação
- **material:** o trecho do entregável em revisão, com identificador

## 2. Julgamento sobre o foco: a prioridade é decidida uma vez, não a cada rodada

O desvio acontece porque cada harness, em cada rodada, reavalia sozinho o que é importante. Três mecanismos seguram isso.

**a) Árvore com nós, ordem e critério de fechamento.** O entregável vira uma árvore. Cada nó tem: identificador, propósito, um critério de aceite verificável e uma posição na ordem de prioridade. A ordem é uma lista, não uma nota. Ela é estabelecida no brief pelo humano, e o harness não a reinterpreta.

A ordem combina duas coisas: dependência primeiro (o que os outros nós usam) e, depois, risco (o nó cuja falha invalidaria mais do entregável).

**b) Uma rodada trabalha só no nó de maior prioridade aberto.** Cada mensagem declara o alvo. Se o alvo não for o primeiro aberto, a mensagem vai para uma lista de "estacionados", com identificador, e não é executada. Isso é mecânico: confere-se o identificador, sem julgamento de mérito.

**c) Melhoria precisa citar o critério que corrige.** Toda crítica tem que apontar qual critério de aceite de qual nó ela ajuda a cumprir. Se não aponta nenhum, é refinamento, e vai para estacionados. Esse é o teste que separa "o entregável está incompleto" de "eu acho que poderia ser melhor".

Dois complementos:

- **Fechamento por critério, não por qualidade subjetiva.** Um nó fecha quando o critério passa. Quando todos os nós de nível superior fecham, ou o orçamento de rodadas se esgota, o ciclo termina. Refinamento além disso não tem critério de parada.
- **Pergunta de deriva em toda rodada.** Cada harness responde: "sem este item, o entregável deixa de cumprir algum critério de aceite?" Sim ou não, com o critério citado. Se não, o item é estacionado.

## O que isso não resolve

A porta mecânica garante que a ordem foi respeitada, não que o julgamento sobre o critério está certo. Essa parte continua dependendo de um revisor que leia o material. Os dois harnesses também podem compartilhar um mesmo viés, e a árvore não elimina isso. O que a árvore faz é impedir que o viés escolha sozinho onde gastar a rodada.