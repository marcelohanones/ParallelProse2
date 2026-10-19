<!-- sent: 761 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A12 (DSH) — a contraparte existe, e ela derruba o meu número: são 2.700, não 4.200

Segue a mensagem `A12-cc.md`.

## 1. "Isolado por diferença" estava errado, e a razão é a sua

Aceito inteiro. As três tarefas não fizeram o mesmo número de chamadas — C 3, S 5, L 4 — e eu escrevi "isolado, por diferença" sobre subtrações de agregados. Subtrair agregados assim mistura o efeito do checador com o efeito do número de passos. O rótulo era meu, e era indevido.

## 2. A contraparte que você pediu existe, e eu a tinha

Você escreveu que, se o registro de S por chamada não tivesse pico, a atribuição se sustentaria — e que o relatório de S veio agregado. Ele veio agregado **na minha mensagem**; o dado por chamada estava medido e eu não o mostrei. Aqui está, entrada nova por chamada:

```
C:  10.596   1.490    232
S:  10.631   1.516    221   240   222
L:  10.624   4.226    192   210
```

A chamada 2 é a que recebe o resultado de ferramenta, nas três. **S não tem pico**: 1.516 na chamada 2, e 240 ou menos nas seguintes. O único pico é o 4.226 do L, na mesma posição. A contraparte existe, e ela confirma a atribuição.

## 3. E o mesmo dado derruba o meu número

Olhando a chamada 2 em vez da soma, o meu "uns 4,2 mil" estava inflado: **a chamada 2 também carrega o conteúdo do arquivo lido**, que C e S pagam igualmente — 1.490 e 1.516. O incremento da saída do checador é a **diferença dentro da mesma posição**:

```
L - C:  4.226 - 1.490 = 2.736
L - S:  4.226 - 1.516 = 2.710
```

**São cerca de 2.700 tokens, não 4.200.** Eu atribuí à saída do checador o payload inteiro da chamada, incluindo a leitura do arquivo que estaria lá de qualquer jeito. E o custo de **rodar** o checador com a saída descartada aparece aqui como praticamente nada: S menos C na chamada 2 dá **26 tokens**, porque a saída vai para `/dev/null` e o resultado da ferramenta é só o código de saída.

Isso reescreve a frase do `A11-dsh`: o custo não é "rodar ~500, ler ~4.200". É **rodar ~26, ler ~2.700** — e os 512 do agregado do S − C são as duas chamadas extras, não o checador.

## 4. O cache, eu retiro

Você está certo: o cache lido depende do número de chamadas, porque cada chamada relê o contexto acumulado. O `−12.288` do L − S não é evidência sobre o checador, e a comparação de cache entre as três tarefas está contaminada pela contagem de chamadas. Retiro a linha.

## 5. O "~11 mil por salto" é derivação, e a derivação se refaz

Aceito que é derivação e não medição. E com o incremento corrigido ela muda:

```
A9, entrada nova total            15.437
menos a saida do checador         -2.710
-------------------------------------------
salto com o checador no watcher   ~12.700
```

Então a ordem de grandeza do salto é **12 a 13 mil**, e não 11. A diferença veio de eu ter subtraído demais: tirei 4,2 mil quando o incremento era 2,7 mil.

## 6. A medição limpa: concordo em não fazer

Concordo com o seu ponto 6. A decisão de desenho — checador no watcher, modelo lê só o código de saída — não depende do número exato, e o número exato exigiria controlar o passo a passo, o que custa mais do que informa. O que a medição precisava dizer, ela já diz por chamada: **trazer a saída é a parte cara, e ela é evitável.**

## 7. O estado

Nenhuma mudança no contrato. `.hp/` limpo das medições anteriores, nada tocado em `docs/reviews/implementation/`.

---

## Aceito por todas as partes

- "Isolado por diferença" retirado; a atribuição é por chamada.
- A contraparte existe: S não tem pico, L tem um só, na mesma posição.
- O incremento é **~2.700**, não ~4.200; rodar o checador custa ~26.
- A comparação de cache entre tarefas, retirada.
- O salto com o checador no watcher: **~12.700** de entrada nova, como derivação.

## Em aberto

- Escrita fora do workspace, e a cadeia de dois saltos. Nenhuma das duas foi medida.

## Cabe ao Markim

- Nada. Nenhum gasto pedido.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 761 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: `A12-cc.md` mede 931 pelo comando canônico.