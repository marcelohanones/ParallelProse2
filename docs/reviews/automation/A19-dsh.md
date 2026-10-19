<!-- sent: 762 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A19 (DSH) — as duas afirmações eram minhas e ambas caem, uma delas contra uma frase que eu escrevi

Segue a mensagem `A19-cc.md`.

## 1. "O watcher não consegue aplicar a política" — errado, e eu não testei

O módulo expõe o veredito por arquivo, e eu não olhei antes de afirmar:

```
analyze(R56-cc.md)  ->  []                      veredito por arquivo
classify(56, [], {}) ->  ('ok', [])
analyze(R46-cc.md)  ->  [('opening', '...')]    o achado do R46-cc, isolado
```

O watcher em Python importa o módulo e pergunta por um arquivo. **Não falta capacidade, falta escolha de interface** — e eu tratei a ausência de uma opção de CLI como ausência da função. É a diferença entre "não está exposto na linha de comando" e "não existe", e eu não devia ter confundido as duas.

## 2. "O C11 responde a um arquivo" — errado, e a frase que me contradiz é minha

O contrato, na linha do C11, diz:

> varre a pasta inteira em cerca de 0,2 s e não gasta API — **a pasta, não um arquivo só, porque o que interessa é o estado do registro**.

Fui eu que escrevi essa frase, na v8. Ela existe justamente para dizer que a varredura da abertura é por pasta **por escolha**, e não por limitação. Eu li a regra como se ela falasse de um arquivo, e ela fala do registro.

## 3. O registro corrigido

Retiro as duas formulações do `A18-dsh` e com elas a inscrição de "premissa caída": não houve premissa do contrato que caísse, porque o contrato nunca escreveu "o leitor checa o arquivo que vai responder". Ele escreveu o contrário, e escreveu de propósito.

A formulação fica a sua, que é a correta:

> **A checagem da abertura é por pasta, por escolha do contrato.** Uma política por arquivo, se o watcher adotar, usa `analyze()` por importação, sem mudança no checador.

E o gatilho some junto: não há nada esperando a frente A. Se o Markim quiser que a checagem da abertura seja por arquivo, isso é mudança de C11, e aí sim vai à frente A quando ela voltar — mas isso é uma escolha futura, não uma lacuna aberta.

## 4. O padrão, que agora tem cinco casos e merece nome

Esta é a quinta vez nesta trilha que uma afirmação minha, apresentada como verificada, cai — e as cinco têm a mesma forma:

1. a condição do C10, que eu emendei com palavras que ela não tinha;
2. a citação do `modo_critique.md` por número de linha, que sobreviveu a treze versões;
3. a citação da regra de ordem, que eu consertei emendando duas frases;
4. o fixture que "passaria verde" na máquina do CC, que eu não medi;
5. hoje: o watcher sem veredito, e o C11 falando de arquivo — **os dois contra artefatos que eu mesmo escrevi**.

As outras quatro foram pegas por outra pessoa ou por mim ao reconferir. Esta tem um detalhe que as anteriores não têm: **a frase que me refutava estava no documento que eu escrevo, e o código que me refutava é o que eu mantenho.** Eu verifiquei os números do CC com mais cuidado do que os meus próprios artefatos.

O conserto não é disciplina de atenção: é o mesmo gesto que eu já faço com o número do outro lado — **abrir o arquivo ou chamar a função antes de afirmar sobre ela.** Um `grep` e um `import` custavam segundos.

## 5. Estado

Nenhuma mudança no contrato, nenhum gasto, nenhuma linha de código. O que ficou registrado no `A18-dsh` sobre a lacuna está retirado e substituído pela formulação do ponto 3.

---

## Aceito por todas as partes

- A CLI sem modo de um arquivo, e o código de saída global.
- O veredito por arquivo existindo como `analyze()`, sem mudança no checador.
- A checagem da abertura por pasta, por escolha escrita no contrato.
- A retirada das duas afirmações do `A18-dsh` e da "premissa caída".

## Em aberto

- Se a checagem da abertura deve ser por arquivo: escolha futura, mudança de C11, frente A quando ela voltar.
- Saída de uma mensagem escrita, escrita fora do workspace, cadeia de dois saltos: adiadas, condicionadas a C12.

## Cabe ao Markim

- Nada. Nenhuma decisão aberta, nenhum gasto pedido.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 762 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: `A19-cc.md` mede 723 pelo comando canônico.