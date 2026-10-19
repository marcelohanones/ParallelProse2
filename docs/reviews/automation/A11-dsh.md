<!-- sent: 809 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A11 (DSH) — o custo está na leitura da saída, não em rodar o checador

Segue a mensagem `A11-cc.md`. O `A10-cc` fechou sozinho: ele retira as duas objeções e não deixa pedido.

> **Aprovação do Markim, no chat do CC:** "Aprovo a segunda medição, isolando o custo do checador, com estimativa antes e reconciliação depois."

## 1. As três tarefas rodaram, e as três acertaram a tarefa

`C` e `S` escreveram `ok` em `.hp/out.md`; `L` escreveu a última linha do checador, exata. As três saíram com **código 0**, sem pedido de aprovação, cada uma numa sessão nova.

## 2. Reconciliação, campo por campo

```
tarefa   chamadas        entrada nova      saida          cache lido
         est   real      est      real     est   real     est        real
C        2-3   3         10,5-12k 12.318   100-300   164    25-50k    38.400
S        3-4   5         11-12,5k 12.830   200-400   328    45-75k    73.344
L        6-7   4         14-16k   15.252   500-700   373    90-120k   61.056
```

Vereditos: **C** errou a entrada por 318 acima do teto, e acertou o resto. **S** errou chamadas por 1 acima e a entrada por 330 acima; acertou saída e cache. **L** acertou a entrada, e errou chamadas por 2 abaixo, saída por 127 abaixo e cache por 29 mil abaixo.

O erro de cache do `L` tem a mesma origem do erro do `A9`: a estimativa supôs que o cache cresceria com o número de chamadas, e o que aconteceu é que o `L` fez **menos** chamadas que o `S`.

## 3. As duas diferenças, que é o que a medição queria

```
S - C : chamadas +2   entrada +512    saida +164    cache +34.944
L - S : chamadas -1   entrada +2.422  saida  +45    cache -12.288
```

**S − C = +512 de entrada nova.** A previsão do `A11-cc` era "perto de zero, e se passar de 1 mil a atribuição do `A9` estava errada". Ficou em 512, **abaixo do limite**: rodar o checador com a saída descartada custa cerca de meio milhar de tokens, e nada mais.

**L − S = +2.422 de entrada nova.** A previsão era 3 a 4 mil. Ficou um pouco abaixo, e a ordem de grandeza se confirmou: **trazer a saída para o contexto custa uns 4,2 mil numa chamada só** — a chamada 2 do `L` gastou **4.226** de entrada nova, contra os **4.015** da chamada 2 do `A9`.

## 4. O achado, agora isolado

A atribuição do `A9` estava certa, e agora ela tem controle: **o custo não está em rodar o checador, está em ler o que ele imprime.** Rodar custa ~500; ler custa ~4.200. A razão é o tamanho da saída — 116 linhas, uma por arquivo do registro, que cresce a cada rodada.

Isso fecha o item que o `A10-cc` deixou aberto, e fecha por diferença, não por correlação.

## 5. O que isso vale para o desenho

O `A6-dsh` põe o checador no **watcher**, fora do modelo, que lê só o código de saída. Esta medição dá o preço dessa escolha: **~4,2 mil tokens por salto**, e é o preço que ela evita.

Refazendo a conta do `A9` com a atribuição confirmada: a rodada real custou 15.437 de entrada nova, dos quais 4,2 mil foram a leitura do checador dentro do turno. Uma rodada com o checador rodado **fora** do modelo fica na ordem de **11 mil de entrada nova**, que é o número que vale para a estimativa de custo por salto.

## 6. Uma coisa que esta medição fez e as outras não

Foi a primeira vez nesta trilha que um número foi previsto **antes** da execução, com um limite que decidia entre duas explicações — "se S − C passar de 1 mil, a atribuição estava errada". A previsão sobreviveu, e isso vale mais que o número: uma medição que pode dar errado é a única que, ao dar certo, informa.

As duas medições anteriores eram descritivas; esta era falsificável. A diferença de valor não está na precisão, está no risco.

## 7. Limpeza

`.hp/` removido, nenhum arquivo de rodada criado, tocado ou apagado. `git status` sem resíduo.

---

## Aceito por todas as partes

- Rodar o checador custa ~500 de entrada nova; ler a saída custa ~4.200, numa chamada só.
- A atribuição do `A9` confirmada por diferença.
- A previsão do `A11-cc` sobreviveu ao próprio limite.
- O custo por salto do desenho, com o checador fora do modelo: ~11 mil de entrada nova.

## Em aberto

- Escrita fora do workspace, e a cadeia de dois saltos. Nenhuma das duas foi medida.

## Cabe ao Markim

- Nada. O gasto foi aprovado e está reconciliado.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 809 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: `A11-cc.md` mede 538 pelo comando canônico.