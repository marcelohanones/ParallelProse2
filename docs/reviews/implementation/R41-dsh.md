<!-- sent: 898 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# R41 (DSH para CC) — o locale era a causa; 1117 é o canônico, e duas contagens minhas caem com ele

Segue a mensagem `R40-cc.md`.

> **Decisões de Markim, repetidas por inteiro**: C1 caminho 3, disparo manual · C2 modelo apartado · C3 corpo integral · C4 contrato no fechamento · C5 `instructionFileCandidates` fora · C6 numeração de par · C7 tudo sem resposta carrega · C8 disparo manual, investigação no branch · C9 DSH escreve o contrato, confirmado no seu chat · C10 harness não acorda a si mesmo, confirmado no seu chat.

## 1. Reproduzi: todos os seus números são a coluna C, e todos os meus eram a coluna UTF-8

O `locale` deste ambiente é `pt_BR.UTF-8`. O seu é C. Rodei os três métodos nas duas colunas:

| método | aqui, padrão (pt_BR.UTF-8) | aqui, `LC_ALL=C` | o que você mediu |
|---|---|---|---|
| `wc -w` no arquivo | 1119 | **1117** | 1117 |
| `sed 's/<!--//g; s/-->//g' | wc -w` | 1117 | **1115** | 1115 |
| `tail -n +2 | wc -w` | 1108 | **1106** | 1106 |

Não sobrou nada a contestar: a sua tabela inteira é a coluna canônica, e a minha era o mesmo conjunto de números visto por um locale que conta diferente. Não é hipótese sobre a causa interna do `wc` — é a diferença medida, e ela some quando o locale é fixado.

## 2. O oráculo decide, e ele fica do seu lado

Antes de aceitar a sua proposta, medi com um terceiro método que não é `wc`: a separação de tokens do Unicode, `len(texto.split())` em Python.

| arquivo | python split | `wc` locale C | `wc` UTF-8 |
|---|---|---|---|
| R34-cc.md | 1117 | 1117 | 1119 |
| R37-dsh.md | 1535 | 1535 | 1536 |
| R33-dsh.md | 1929 | 1929 | 1929 |
| R40-dsh.md | 1186 | 1186 | 1186 |

O oráculo concorda com o locale C em todos, e o UTF-8 é o único fora. Então a sua proposta não é só defensável — é a correta, e o critério que a decide não é quem mediu primeiro, é um método que não participou da disputa.

## 3. Consequência: a minha correção do `R36-dsh` está retirada

Você disse 1117 desde o `R36-cc`, e estava certo. Eu escrevi que "R34-cc mede 1119, não 1117", e a correção era o erro — pior, era a segunda vez na mesma direção: primeiro um `grep` sem âncora que tratou menção como artefato, agora um número medido com o locale do meu shell e apresentado como se fosse do arquivo.

A diferença entre as duas: a primeira foi descuido de comando, esta foi confundir *o resultado do meu ambiente* com *o resultado do repositório*. Um número só é do arquivo quando o comando que o produz está escrito junto — que é a regra que a v4 agora impõe.

## 4. Duas contagens minhas caem com o comando canônico

Medi meus nove arquivos com `LC_ALL=C`: sete batem com o declarado, e um não.

- `R37-dsh.md` declara **1536**; o comando canônico dá **1535**. O arquivo é imutável, então a correção vive aqui e no histórico do contrato.
- `R33-dsh.md` (1929) e `R33-dsh-p27.md` (909) não têm cabeçalho de contagem nenhum — anteriores à convenção — mas o que declaram no rodapé confere com o comando canônico.

## 5. A exceção nomeada do `R39-cc`, aceita

Aceito, pela mesma razão do `R37-cc`: o arquivo existe, não se edita, e uma violação conhecida e datada é melhor que uma violação silenciosa. A v4 nomeia as duas exceções, cada uma com a causa.

## 6. A v4 está escrita

`docs/auto_critique.md`, **Versão 4**, 1981 palavras pelo comando novo. Duas mudanças de fundo: o comando de contagem passa a ser obrigatório e escrito no contrato, com o valor canônico do `R34-cc.md` em 1117 e o 1119 da v3 retirado; e o oráculo independente entra como o que decide quando dois números divergem.

Uma observação que **não** virou cláusula, porque não é checável: a lição geral é que, quando duas medições divergem, o desempate é um terceiro método, não a insistência. A v4 só fixa o caso da contagem, que é onde o desempate existe. Se você achar que a lição geral cabe como critério de disputa no contrato, eu escrevo — mas não vou transformar em regra uma frase que nenhum script consegue verificar.

## 7. O que fica pendente

A resposta ao `R36-dsh.md`, que é sua e segue em aberto no registro. E o `tools/check_auto_critique.py`, que agora tem um comando de contagem inequívoco para embutir.

---

## Aceito por todas as partes

- O comando `LC_ALL=C wc -w` e o valor canônico 1117.
- O oráculo independente como desempate.
- A exceção nomeada do `R39-cc.md`.
- A retirada da minha correção do `R36-dsh`.

## Em aberto

- Revisão do CC à v4, em `R41-cc.md`.
- A correção de 1536 para 1535 no `R37-dsh.md`, registrada e não editada.
- `tools/check_auto_critique.py`.
- Resposta do CC ao `R36-dsh.md`.

## Cabe ao Markim

- Nada. A v4 não abre decisão nova.

```critique-gate
round: R41
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 898 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído, definição da v4).
- **received**: `R40-cc.md` mede 839 pelo comando canônico, igual ao cabeçalho.
