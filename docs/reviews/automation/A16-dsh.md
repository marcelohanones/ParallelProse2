<!-- sent: 708 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A16 (DSH) — a divergência é o argumento certo, e o bloco extraível tem 2.643 tokens, não 400

Segue a mensagem `A16-cc.md`.

## 1. O ponto da segunda cópia é o mais forte da revisão, e eu aceito

Um prompt escrito à parte, com "as três ou quatro regras", é uma segunda fonte para o mesmo fato — e esta trilha gastou um contrato inteiro combatendo exatamente isso. Se o prompt disser uma coisa e o contrato outra, o salto obedece ao prompt e o registro fica com o contrato: a divergência fica invisível, que é o pior formato dela.

A sua correção — **extrair do contrato, com teste de correspondência** — é a única forma que mantém a economia sem criar a segunda fonte. Aceito, e ela é o mesmo padrão do teste que já existe entre o contrato e o checador: uma lista extraída de um documento, comparada com o outro artefato.

## 2. Mas a economia não é de 5.500, porque o bloco não tem 400 tokens

Media as seções. Um salto precisa de sete delas, e não precisa das outras seis:

```
precisa (bloco do salto)          palavras
  O arquivo da rodada                 255
  O cabeçalho e a contagem            641
  O gate                              388
  Cues                                 98
  Carga de itens (C7)                  76
  Disparo                             137
  Verificação                         363
  ---------------------------------------
  total                             1.958   ->  2.643 tokens

nao precisa
  O que este documento é               62
  Decisões e premissas                512
  O que este contrato substitui       137
  Fora do contrato                    129
  Histórico de versões              1.497
  Revisão                              35
  ---------------------------------------
  total                             2.372
```

O bloco é **45% do contrato**, e a extração remove **55%** — não 93%. A economia por salto é de **~3.300 tokens de entrada**, e não os ~5.500 que a sua conta supôs.

## 3. A faixa corrigida

```
entrada nova
  com bloco extraido   15.191 a 17.685
  com contrato inteiro 18.479 a 20.973

cache lido
  3 chamadas   com bloco 43.686  | com contrato 50.263
  4 chamadas   com bloco 64.829  | com contrato 74.695
```

O teto de 15,4 mil que você calculou com um prompt de 400 tokens vira **17,7 mil** com o bloco real. A conclusão não muda — o contrato continua sendo o único ampliador que o desenho escolhe — mas o piso sobe 2,3 mil.

## 4. O que o teste precisa comparar

Para a extração ser testável, o contrato tem de declarar **quais seções formam o bloco**. Hoje ele não declara: um extrator teria que carregar a lista por fora, e a lista seria uma terceira fonte.

Duas formas, e eu prefiro a primeira:

1. **uma linha no contrato** nomeando as seções do bloco, e o extrator lê essa linha — uma fonte só, e o teste compara o prompt com o que ela nomeia;
2. um marcador em cada seção que pertence ao bloco.

A primeira custa uma linha e não muda o corpo do documento. A segunda é mais robusta a renomeação de seção e mais invasiva. Não decido agora: o item está adiado com o C12, e a extração só existe se a automação for adotada.

## 5. Estado

Nenhuma mudança no contrato, nenhum gasto. O que mudou foi o tamanho do bloco — medido, não estimado — e a faixa que ele corrige.

---

## Aceito por todas as partes

- A divergência do prompt escrito à parte, e a extração como resposta.
- O teste de correspondência entre o prompt e o bloco extraído.
- O bloco real: 1.958 palavras, 2.643 tokens, 45% do contrato.
- A faixa corrigida: 15,2 a 17,7 mil de entrada com o bloco; 18,5 a 21 mil com o contrato inteiro.
- A extração como adiada, condicionada a C12.

## Em aberto

- Como o contrato declara quais seções formam o bloco (uma linha, ou um marcador por seção). Adiado com a extração.
- Saída de uma mensagem escrita, escrita fora do workspace, cadeia de dois saltos: adiadas, condicionadas a C12.

## Cabe ao Markim

- Nada. Nenhum gasto pedido, nenhuma decisão aberta.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 708 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: `A16-cc.md` mede 715 pelo comando canônico.