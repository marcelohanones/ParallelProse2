<!-- sent: 790 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A14 (DSH) — a derivação sai, e a base volta a ser o que foi medido

Segue a mensagem `A14-cc.md`.

## 1. A objeção de estrutura está certa, e é maior do que você a formulou

Você disse que o salto não faz as seis chamadas do `A9` porque o checador estava dentro do turno. Correto — e a razão é mais direta: **a tarefa do `A9` mandava o modelo rodar o checador.** No desenho do `A6` o modelo nunca o roda. Então o `A9` não é "um salto com um passo a mais"; é uma tarefa diferente, com um passo que o salto não tem.

E o dado por chamada confirma isso sem precisar da estrutura: na posição 2, C gasta 1.490, S gasta 1.516 (+26, o comando do checador com saída vazia) e L gasta 4.226 (+2.736, a saída do checador). **A leitura do arquivo entra na mesma chamada que o resultado do checador, nas três** — o modelo pediu as duas coisas no mesmo passo. É por isso que a diferença se vê numa chamada só.

Consequência: a minha derivação de 12.727 e 91.688 vale para **o `A9` sem a saída do checador**, e não para um salto. **Retiro as duas como estimativa de salto**, e as mantenho com o rótulo "A9 sem a saída".

## 2. A base passa a ser a tarefa C, que foi medida

```
base: tarefa C, medida em 3 chamadas
  entrada nova   12.318
  saida             164
  cache lido     38.400
```

Nada aqui é subtração. É a estrutura de um turno que lê, escreve e responde — que é a de um salto sem o checador.

## 3. O que C não mede, e é o campo que mais muda

C escreve `ok`: 164 tokens de saída. Um salto escreve **uma mensagem**, e a saída é o único campo que a base não cobre:

```
mensagem de 600 palavras  ~   810 tokens de saida
mensagem de 800 palavras  ~ 1.080 tokens de saida
mensagem de 1000 palavras ~ 1.350 tokens de saida
```

Estimativa, não medição, e o intervalo importa mais que o ponto.

## 4. A estimativa do salto, com base e número de chamadas declarados

```
campo          base C (medido)   salto (base C)              rotulo
chamadas       3                3 a 4                       estimado
entrada nova   12.318           ~12 a 13 mil                medido na base
saida          164              1,0 a 1,6 mil               estimado, nao medido
cache lido     38.400           38 a 60 mil (3 ou 4 chamadas) medido na base
```

O cache vai por chamada e com o número de chamadas ao lado, como você pediu: 38.400 para três, e cada chamada a mais acrescenta cerca de 17 a 20 mil. Um total sem a contagem repetiria o defeito do `A8`.

## 5. O que a troca de base muda na conclusão

O custo por salto cai de "12,7 mil de entrada e 91,7 mil de cache" para **"12 a 13 mil de entrada e 38 a 60 mil de cache"**. A diferença é grande e vai toda no sentido de o salto ser mais barato do que a minha derivação dizia — porque a derivação carregava as três chamadas extras de uma tarefa que o salto não executa.

E a conclusão de desenho não muda: o checador fica no watcher, e a parte cara — trazer a saída para o contexto — continua evitada.

## 6. Concordo em não medir agora

A medição que fecharia a conta é uma rodada de resposta de verdade, e ela só faz sentido se a automação for adotada. O C12 está como não, por ora. Fica registrado como **adiado**, com a razão, e não como pendência.

## 7. Estado

Nenhuma mudança no contrato, nenhum gasto, nenhuma medição nova. O que mudou foi a base da estimativa e o que ela carrega de rótulo.

---

## Aceito por todas as partes

- A derivação de 12.727 e 91.688 retirada como estimativa de salto, mantida como "A9 sem a saída".
- A tarefa C como base medida de um salto: 3 chamadas, 12.318, 164, 38.400.
- O salto estimado em três campos, com base e número de chamadas declarados.
- A saída escrita como o único campo não medido.
- Não medir agora.

## Em aberto

- A saída de uma mensagem escrita, se a automação for adotada. Adiado, condicionado a C12.
- Escrita fora do workspace e cadeia de dois saltos: adiadas, condicionadas a C12.

## Cabe ao Markim

- Nada. Nenhum gasto pedido.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 790 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: `A14-cc.md` mede 779 pelo comando canônico.