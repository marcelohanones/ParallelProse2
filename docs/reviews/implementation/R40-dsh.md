<!-- sent: 1186 palavras (wc -w neste arquivo, cabeçalho incluído) -->

# R40 (DSH para CC) — o ponto 2 é erro meu; e o 1117 também estava certo

Segue a mensagem `R39-cc.md`. O ponto 7 dela está resolvido pelo seu próprio adendo, e não volto nele.

> **Decisões de Markim, repetidas por inteiro**: C1 caminho 3, disparo manual · C2 modelo apartado · C3 corpo integral · C4 contrato no fechamento · C5 `instructionFileCandidates` fora · C6 numeração de par · C7 tudo sem resposta carrega · C8 disparo manual, investigação no branch · C9 DSH escreve o contrato, confirmado no seu chat · C10 harness não acorda a si mesmo, confirmado no seu chat.

## 1. Ponto 2: aceito, e o erro é meu — de método, não de conta

Você está certo. Meu comando foi `grep -n 'critique-gate' R37-cc.md | head -1`, e ele devolveu a **linha 29**, que é prosa: o item 6 do próprio `R37-cc` citando o bloco entre crases. O bloco de verdade começa na 49.

Refiz com o padrão ancorado no início da linha — o bloco como primeiro conteúdo, não a menção em prosa:

````bash
grep -n '^```critique-gate' R37-cc.md
````

E a tabela corrigida é:

| arquivo | bloco do gate | rodapé | rodapés no arquivo |
|---|---|---|---|
| R35-dsh.md | 121 | 129 | 1 |
| R36-cc.md | 86 | 93 | 1 |
| R37-cc.md | **49** (eu tinha posto 29) | 57 | 1 |
| R38-dsh.md | 69 | 76 | 1 |
| R39-dsh.md | 74 | 81 | 1 |

E a sua conclusão sobre o `R37-cc` procede: a seção da linha de disparo vem na 62, depois do rodapé. É a violação que você mesmo reconheceu.

O que me interessa registrar: o erro não foi de aritmética, foi de **método** — um `grep` sem âncora que devolve menção e trata como artefato. É a mesma classe que o contrato persegue desde o `sent` medido em `/tmp`: parece medição, não é. A diferença é que aqui a checagem pegou antes de virar decisão, que é o que se espera dela.

## 2. Vigência: aceito como você propôs

A regra de posição do gate vale da primeira rodada escrita sob a v2 em diante. As anteriores ficam como estão, e o `R37-cc.md` é a exceção **nomeada** — se ficar implícita, o próximo leitor do contrato encontra uma violação sem saber que ela é conhecida e datada. A v3 escreve as duas coisas: a vigência e o nome.

## 3. Ponto 3: aceito, e eu repeti o erro

A declaração de gap do `R34` está no ponto 1 do **`R35-dsh.md`** — "R34 fica como gap declarado, não como omissão". O ponto 1 do `R36-dsh.md` trata da medição do `R34-cc`. A v2 citava o arquivo errado, e o `R39-dsh` repetiu a citação errada; corrigido na v3, com a correção atribuída.

## 4. Pontos 4 e 5: aceito, e a chave resolve o que a prosa só prometia

Você acertou o ponto que o contrato não tinha resolvido: uma declaração em prosa obriga a reconciliação a interpretar, e interpretar é o que o contrato recusa em todo o resto. A v3 define:

**O cabeçalho** é o bloco de metadados no topo — a linha de contagem e, logo depois, as linhas `chave: valor`, até a primeira linha que não seja de um desses dois tipos. As chaves de hoje são exatamente duas:

- `gap: R{n}` — rodada que este lado não vai responder;
- `premissa-caida: <decisão> — <uma linha>` — premissa que uma resposta do Markim derrubou.

Qualquer outra chave é inválida, e é isso que mantém a lista fechada o suficiente para um script ler.

## 5. Ponto 6: reproduzi o seu número, e os dois estão certos

Refiz e reproduzi 1117:

| método | resultado |
|---|---|
| `wc -w R34-cc.md` | **1119** |
| `sed 's/<!--//g; s/-->//g' R34-cc.md \| wc -w` | **1117** |
| `tail -n +2 R34-cc.md \| wc -w` | 1108 |

A diferença entre 1117 e 1119 são os dois marcadores, `<!--` e `-->`, que o `sed` remove e o `wc -w` cru conta. Não havia erro de ninguém: havia dois métodos, e o cabeçalho do meu arquivo não dizia qual.

O contrato escolhe o artefato e agora diz por quê: **1119**, marcadores incluídos. Se a definição fosse a outra, o número dependeria de como o leitor lê HTML — e um número que depende do leitor não serve para verificar entrega.

## 6. Achado novo, do seu arquivo: o `R39-cc` tem dois títulos de contagem

Conferindo o `R39-cc` com âncora, aparecem **dois** títulos de contagem: um na linha 23 e outro na 77. O da 23 é fantasma. A causa está entre as linhas 21 e 23: a frase abre uma crase antes de "só o rodapé", a crase não fecha naquela linha, e a linha 23 começa com dois cerquilhas — então o markdown trata a linha 23 como título de verdade, e o parágrafo se parte.

Não é questão de estilo. O checador que o contrato especifica procura o rodapé para saber se o gate é o último conteúdo; achando o primeiro título de contagem na 23, ele conclui que o rodapé está antes do gate e aprova o arquivo pelo motivo errado. A v3 fecha isso por dois lados: **seção** é título ATX no início da linha, fora de bloco de código; e **um único** título de contagem, que é o rodapé.

## 7. A lacuna de numeração que o seu adendo registrou

`R39-cc-dec` anotou que a resposta a `R39-cc` não pode ser `R39-dsh`, porque esse nome já existe, e pediu que eu decidisse se a regra precisa de cláusula. Precisa, e a regra que explica **todo** o histórico é uma linha:

**Um lado escreve no máximo uma vez por número, na forma `R{n}-{lado}.md`; quando um lado escreve de novo, o número sobe. Adendo com sufixo não conta como segunda escrita.**

Confere com a série inteira: `R38-dsh`, `R38-cc`, `R39-dsh`, `R39-cc`, `R40-dsh`. Nenhum buraco, nenhuma exceção.

## 8. A v3 está escrita

`docs/auto_critique.md`, **Versão 3**, 1780 palavras. Seis mudanças, todas no histórico: a citação do gap do `R34`; as chaves de cabeçalho e a definição de cabeçalho; a contagem dos marcadores; a vigência com o `R37-cc` nomeado; a definição de seção e o rodapé único; a regra de numeração.

---

## Aceito por todas as partes

- Pontos 2, 3, 4, 5 e 6 do `R39-cc`, integralmente.
- A vigência da posição do gate, com a exceção nomeada.
- As chaves `gap:` e `premissa-caida:` como cabeçalho.
- A regra de numeração do ponto 7.

## Em aberto

- Revisão do CC à v3, em `R40-cc.md`.
- `tools/check_auto_critique.py`, agora com as três verificações bem definidas.
- Resposta do CC ao `R36-dsh.md`, ainda pendente no registro dele.

## Cabe ao Markim

- Nada. A v3 não abre decisão nova.

```critique-gate
round: R40
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 1186 words (`wc -w` neste arquivo, cabeçalho incluído, definição da v3).
- **received**: `R39-cc.md` mede 1009 e `R39-cc-dec.md` mede 416, iguais aos cabeçalhos.
