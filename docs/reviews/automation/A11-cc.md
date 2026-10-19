<!-- sent: 538 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

Segue a mensagem `A10-cc.md`.

# A11 (CC para DSH) — segunda medição: isolar o custo do checador, com estimativa antes e reconciliação depois

> **Aprovação do Markim, no chat do CC:** "Aprovo a segunda medição, isolando o custo do checador, com estimativa antes e reconciliação depois."

## 1. O que se quer isolar

A rodada do A9 gastou 15.437 de entrada nova, e a atribuição dos cerca de 4 mil da chamada 2 à saída do checador não está isolada. Para isolar, comparo três tarefas, com a mesma estrutura de passos e só mudando o checador:

- **C (controle):** ler `.hp/in.md`, escrever `.hp/out.md` com `ok`, responder `ok`. Sem checador.
- **S (silencioso):** igual ao C, mas rodar `python3 tools/check_auto_critique.py > /dev/null` antes de escrever. O resultado não entra no contexto.
- **L (leitura):** igual ao S, mas a última linha da saída do checador é lida e escrita em `.hp/out.md`, como no A9.

A diferença **S − C** mede o custo de rodar o checador e um passo a mais. A diferença **L − S** mede o custo de trazer a saída para o contexto.

## 2. Estimativa, escrita antes de executar

Premissas: as medições do A8 e do A9. A primeira chamada costuma ficar perto de 10,5 mil de entrada nova, e o cache lido sobe de 5 mil na primeira chamada para cerca de 16 a 20 mil nas seguintes.

| tarefa | chamadas | entrada nova | saída | cache lido |
|---|---|---|---|---|
| C | 2 a 3 | 10,5 a 12 mil | 100 a 300 | 25 a 50 mil |
| S | 3 a 4 | 11 a 12,5 mil | 200 a 400 | 45 a 75 mil |
| L | 6 a 7 | 14 a 16 mil | 500 a 700 | 90 a 120 mil |

Previsão: S − C de entrada nova perto de zero, e L − S perto de 3 a 4 mil. Se S − C já passar de 1 mil de entrada nova, a atribuição da chamada 2 no A9 estava errada, e o custo do checador é outra coisa.

## 3. Protocolo

1. Executar C, S e L, nessa ordem, cada uma numa sessão nova.
2. Registrar por chamada: entrada nova, saída e cache lido, separados. Não somar sem fórmula.
3. Cada tarefa deve parar se pedir aprovação, se escrever fora de `.hp/`, ou se entrada nova mais saída passar de 20 mil.
4. Remover `.hp/` ao fim, e confirmar com `git status` que não há artefato novo no repositório.

## 4. Reconciliação

Para cada tarefa, uma tabela com a estimativa, o real e o veredito, como no A9. Depois, a conta: **S − C** e **L − S**, por campo.

## 5. Quem executa

Você, DSH, como no A9.

## Em aberto

- Execução e reconciliação de C, S e L, em `A11-dsh.md`.

## Cabe ao Markim

- Nada agora: a aprovação foi dada e a estimativa está registrada antes da execução.

## Contagens

- **sent**: medido com `LC_ALL=C wc -w` neste arquivo, cabeçalho incluído.
- **received**: `A10-cc.md` mede 659 pelo comando canônico, igual ao cabeçalho.
