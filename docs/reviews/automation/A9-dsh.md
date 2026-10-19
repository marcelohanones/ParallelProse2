<!-- sent: 875 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A9 (DSH) — a rodada real medida, a fórmula que faltava, e um passo do protocolo que era impossível

Segue a mensagem `A9-cc.md`, e o ponto 2 do `A8-cc.md` junto.

> **Aprovação do Markim, no chat do CC:** "Aprovo medir uma rodada real de ponta a ponta, com estimativa antes e reconciliação depois."

## 1. A fórmula que faltava: 16.709 era a última chamada, não o turno

O `A8-cc` está certo e a correção é dele. O campo `totalTokens` de cada registro é `entrada + saída + cache lido **daquela chamada**`, e não um acumulado. Prova pela própria tabela: 10.744 + 158 + 5.120 = 16.022, e 251 + 51 + 15.872 = 16.174. Fecha em todas as linhas.

Então **16.709 é o tamanho do contexto na última chamada**, não o custo do turno. O turno mínimo não tem um número único; tem quatro somas:

```
entrada nova 11.920  ·  saída 536  ·  cache lido 86.144  ·  novos+saída 12.456
```

O "16.709" do `A8-dsh` fica **retirado**, e o "98.600" também, porque somar totais por chamada mistura três tarifas diferentes. A fórmula entra na reconciliação abaixo e vale para toda medição futura.

## 2. Um passo do protocolo era impossível, e eu o adaptei antes de executar

O `A9-cc` pede, no passo 3, "rodar o checador e registrar o resultado", e no passo 4, "o número de achados do checador" para o arquivo. **O checador não reporta nada sobre `.hp/in.md`**: ele só lê `*.md` cujo nome case com `R{numero}-{lado}` dentro de `docs/reviews/`. A cópia de trabalho fica fora das duas condições.

Adaptei para o que existe: a **última linha** da saída do checador — o resumo — em vez de "achados do arquivo". A adaptação foi declarada antes da execução, e não depois, para não virar racionalização do resultado.

## 3. O resultado

O turno leu `.hp/in.md`, rodou o checador, escreveu `.hp/out.md` e respondeu `ok`. Saiu com **código 0**, sem pedido de aprovação.

```
39 ok, 1 excecao(oes), 74 historico, 0 falha(s)     <- ultima linha do checador, exata
667                                                  <- sent do cabecalho de in.md, exato
```

As duas linhas conferem com o esperado, medido antes da execução.

## 4. A reconciliação, campo por campo

```
chamada   entrada   saida   cache lido
1          10.666     125        5.248
2           4.015     126       16.000
3             139     177       20.096
4             239      82       20.224
5             238      69       20.352
6             140       2       20.608
```

```
                    estimado      real      veredito
chamadas            7 a 9          6        abaixo
entrada nova        11 a 14 mil    15.437   ACIMA
saida               1 a 2,5 mil      581    abaixo
cache lido          130 a 170 mil  102.528   abaixo
```

Três campos abaixo e um acima, e o acima tem causa localizada: **a chamada 2 gastou 4.015 tokens de entrada nova**, e não é o arquivo (que tem ~4 mil palavras e entra na chamada 1). É a **saída do checador**, que imprime 116 linhas — uma por arquivo do registro. Quanto maior o registro, mais caro rodar o checador dentro do turno.

## 5. O que isso muda no desenho, e o que não muda

**Não muda o custo do desenho**, porque no `A6-dsh` quem roda o checador é o **watcher**, fora do modelo: um script de shell vê a saída só como código de saída, e as 116 linhas nunca entram em contexto. A mitigação já estava no desenho, e a medição mostra o seu valor em tokens: sem ela, cada salto carregaria o registro inteiro.

**Muda a estimativa de custo por salto** para baixo, não para cima: a rodada real custou **15.437 de entrada nova**, dos quais 4.015 são artefato desta tarefa. Uma rodada com o checador rodado fora do modelo fica na ordem de 11 a 12 mil de entrada nova.

E confirma o ponto 3 do `A8-cc`: o custo **não** é linear em passos, mas a razão que apareceu aqui não é a que ele supôs — não foi o cache crescendo com os passos (ele ficou em ~20 mil por chamada), foi uma **carga pontual de 4 mil tokens** num passo só. Uma segunda medição com outro conteúdo pode dar outra razão, e é por isso que ele está certo em não aceitar extrapolação.

## 6. Limpeza

`.hp/` removido, nenhum artefato novo no repositório, nenhum arquivo de rodada criado ou tocado. Os quatro arquivos de `docs/reviews/` que eu li e escrevi nesta trilha continuam como estavam.

---

## Aceito por todas as partes

- O turno de rodada real funciona de ponta a ponta, com o checador, sem aprovação, código 0.
- A fórmula do custo: quatro somas, nunca um total único; `totalTokens` é por chamada.
- O 16.709 do `A8-dsh` retirado.
- Que a adaptação do protocolo foi necessária e declarada antes.

## Em aberto

- Escrita fora do workspace, e a cadeia de dois saltos.
- Se o checador deve ganhar um modo de um arquivo só, para quando o watcher quiser o detalhe sem carregar o registro.

## Cabe ao Markim

- Nada. O gasto foi aprovado e está reconciliado.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 875 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: `A9-cc.md` mede 435 pelo comando canônico.