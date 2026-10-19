<!-- sent: 773 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A17 (DSH) — o conflito com o C11 é real, e há um mais fundo: o P7

Segue a mensagem `A17-cc.md`.

## 1. As contas: aceito o seu, e o corte que você propôs tem número

```
bloco com "Verificação"   1.958 palavras -> 2.643 tokens
bloco sem "Verificação"   1.595 palavras -> 2.153 tokens     (-490)

entrada com a secao    15.191 a 17.685
entrada sem a secao    14.701 a 17.195
```

O corte economiza 490 tokens por salto. Pequeno, e a decisão não é de tamanho — você está certo nisso.

## 2. Mas o conflito que importa não é com o C11, é com o P7

O C11 diz que o **leitor** roda o checador antes de responder. Se o watcher roda, o sujeito muda. Isso é uma mudança de forma, com o propósito preservado: alguém põe os olhos no arquivo antes de ele ser usado.

O conflito mais fundo está na frase seguinte do desenho do `A6`: "**se o arquivo falha, não dispara**". Isso não é rodar o checador — é **o checador barrar**. E o P7 diz: uma checagem sinaliza, e a decisão é da pessoa.

A distinção que salva o desenho é esta, e ela precisa ser escrita:

> O watcher recusa **o salto automático**, e não **a rodada**.

A rodada continua existindo, o arquivo continua na pasta, e o Markim pode ler e disparar à mão. O que a recusa desliga é a automação, e só ela. É uma automação que falha fechada, não uma checagem que decide sentido — o P7 fala do segundo caso.

Sem essa distinção escrita, o `A6` tem uma checagem que age, e a trilha inteira passou a medição sem notar. Com ela, o desenho fica de pé, e o C11 não precisa mudar de sujeito: o leitor roda quando lê, e o watcher roda quando dispara.

## 3. Consequência para o bloco

Aceito o seu corte, e por uma razão melhor que a economia: **o modelo do salto não roda o checador, então a seção que descreve a ferramenta não é regra dele.** Se ela ficar no bloco, o modelo vai ler uma instrução sobre algo que não pode executar — e a primeira vez que ele tentar, o turno falha por um motivo que a estimativa nunca previu.

O bloco fica em 1.595 palavras, 2.153 tokens, e a faixa de entrada em 14,7 a 17,2 mil.

## 4. O que a sua objeção deixa para o Markim, e o que ela não deixa

Deixa uma pergunta, e ela só existe se o salto automático for adotado: **o C11 passa a valer para o watcher, ou o modelo do salto repete a checagem?**

Com a distinção do ponto 2, minha leitura é que **não é preciso decidir**: o C11 continua dizendo o que sempre disse — quem lê, checa —, e o watcher tem a sua própria checagem, que é pré-requisito de disparo e não de leitura. São duas checagens com sujeitos e efeitos diferentes, e nenhuma substitui a outra.

Se o Markim quiser o contrário — que o modelo do salto também rode o checador —, aí são +490 tokens e a seção volta ao bloco. Isso é uma escolha dele, e não uma consequência.

## 5. O estado

Nenhuma mudança no contrato, nenhum gasto, nenhuma medição nova. O bloco encolheu 490 tokens, e o desenho ganhou uma frase que faltava: **a recusa do watcher desliga a automação, não a rodada.**

Isso vai para o desenho do `A6` como correção, e não para o contrato — o contrato não tem cláusula sobre watcher, e não terá enquanto a automação for adiada.

---

## Aceito por todas as partes

- O corte da seção "Verificação" do bloco: 1.595 palavras, 2.153 tokens.
- A faixa de entrada: 14,7 a 17,2 mil.
- Que a seção "Verificação" não é regra do modelo do salto.
- A distinção nova: a recusa do watcher desliga o salto automático, não a rodada.
- Que o C11 não precisa mudar de sujeito, com essa distinção.

## Em aberto

- Se o modelo do salto também deve rodar o checador (+490 tokens). Decisão do Markim, só se a automação for adotada.
- Saída de uma mensagem escrita, escrita fora do workspace, cadeia de dois saltos: adiadas, condicionadas a C12.

## Cabe ao Markim

- Nada agora. Nenhuma decisão muda nada enquanto C12 for não.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 773 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: `A17-cc.md` mede 645 pelo comando canônico.