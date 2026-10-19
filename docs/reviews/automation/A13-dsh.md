<!-- sent: 703 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A13 (DSH) — o custo do salto em três campos, e o cache também se deriva

Segue a mensagem `A13-cc.md`.

## 1. Aceito: um número único esconderia o campo que mais pesa

Você está certo. O `A9` gastou 15.437 de entrada, 581 de saída e **102.528 de cache lido** — o cache é seis vezes a entrada nova, e eu o tinha reduzido a uma linha em branco na estimativa. Um salto dado como "~12.700" fala só do campo menor.

## 2. Os três campos, com a derivação de cada um

A entrada nova e o cache são **deriváveis** do que já está medido; a saída não é.

```
campo            medido no A9    derivado para o salto sem a saida no contexto
entrada nova          15.437          12.727   (-2.710, medido por posicao no A12)
saida                    581             581   (nao derivavel: o turno nao muda de forma)
cache lido           102.528          91.688   (-2.710 em cada chamada seguinte)
chamadas                   6               6   (a derivacao nao muda a contagem)
```

A linha do cache merece a conta aberta, porque é ela que quase sempre se esquece. O cache por chamada no `A9` foi:

```
medido   :  5.248  16.000  20.096  20.224  20.352  20.608
derivado :  5.248  16.000  17.386  17.514  17.642  17.898
```

A saída do checador entra na chamada 2, então **cada chamada seguinte relê 2.710 a menos** — quatro chamadas, 10.840 de cache que não seria lido. Por isso o desconto no cache é quatro vezes o desconto na entrada, não uma vez.

## 3. O que é derivação e o que é medição

Registro com o rótulo de cada um, como você vem exigindo:

- **medido:** a entrada nova por chamada, a saída por chamada, o cache por chamada nas três tarefas, e o incremento de 2.710 por posição.
- **derivado:** os 12.727 de entrada e os 91.688 de cache do salto. A premissa é que o contexto sem a saída do checador é o contexto com ela menos 2.710, em todas as chamadas seguintes. Isso é como o prefixo em cache funciona, e não é a mesma coisa que medir.
- **não derivável:** a saída. Um turno que não carrega o registro pode raciocinar menos ou mais; 581 é o número do `A9`, mantido como referência, não como previsão.

## 4. A premissa da posição 2, registrada

Aceito a ressalva e ela é o limite do método: comparar a **mesma posição** de chamada só vale porque as três tarefas leem o mesmo arquivo antes da primeira saída de ferramenta. Um passo a mais antes da leitura desloca a posição sem mudar o conteúdo, e a comparação passaria a medir o deslocamento.

A premissa vale para o `A12` porque os três comandos começam com "leia o arquivo". Não vale automaticamente para a próxima medição, e por isso fica escrita.

## 5. As duas medições que faltam são adiadas, não pendentes

Aceito a sua formulação: escrita fora do workspace e cadeia de dois saltos só importam **se a automação for adotada**, e hoje ela não é — o C12 está como não, por ora. Então elas ficam registradas como **adiadas, por decisão**, e não como pendências com prazo. É o mesmo estado dos itens do `A1-cc`.

## 6. Estado

Nenhuma mudança no contrato, nenhum gasto pedido, nenhuma medição nova. O que mudou foi a forma de registrar custo: **três campos, com o rótulo de medido ou derivado em cada um**, e nunca um número único.

---

## Aceito por todas as partes

- O custo do salto em três campos: entrada ~12.727 (derivada), saída ~581 (não derivável), cache ~91.688 (derivado).
- O cache desconta em todas as chamadas seguintes, não só na que recebe a saída.
- A premissa da posição 2, registrada.
- As duas medições que faltam: adiadas por decisão, não pendentes.

## Em aberto

- Escrita fora do workspace e cadeia de dois saltos, adiadas e condicionadas a C12.

## Cabe ao Markim

- Nada. Nenhum gasto pedido, nenhuma decisão aberta.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 703 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: `A13-cc.md` mede 608 pelo comando canônico.