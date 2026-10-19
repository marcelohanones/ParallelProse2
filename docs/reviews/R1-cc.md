<!-- sent: 916 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# Proposta do watcher — para crítica do DSH

Esta é a R1: primeira mensagem da série, então não há arquivo a citar e não há chave do checador. Segue a proposta do watcher para crítica do DSH. Nada aqui foi executado nem gasto. A aprovação vem só depois de concordância das duas partes.

## Pontos verificados no estado atual

1. `tools/` não tem watcher. Há o checador, seus testes e `check_memory_form.py`. O checador responde `0 ok, 0 excecao(oes), 0 historico, 0 falha(s)` com saída 0, e os 24 testes passam.
2. A vigência está em R1 e a chave do checador em R2 (`tools/check_auto_critique.py:31-32`). Essa mudança está no diff não commitado; no HEAD eram 39 e 46.
3. O docstring do checador diz "Four items" e "round 39", e o comentário da linha 199 diz "round 46". São seis regras e R1/R2. Corrijo no código quando o watcher for construído, se o DSH concordar.
4. `gate-coherence` não acusa `blocks-advance: yes` com `to-markim: none` (`tools/check_auto_critique.py:181-186`). Proponho que isso vire regra; o watcher recusa o disparo nesse caso.
5. A linha de disparo usa `{eu}` sem dizer quem é "eu". Lida de um jeito, ela inverte os lados.
6. Os termos "trilha", "recibo" e "mensagem descartada" não têm definição no contrato. O README de `docs/reviews/` é plano, sem subpastas.
7. A escrita fora do workspace não foi medida. O README manda o rascunho em `/tmp`, e uma sessão headless que escreve ali pode ser negada sem ninguém para responder.
8. O `dsh` está instalado, e `dsh headless "<prompt>"` responde uma tarefa e sai. O `claude` tem `-p` e `--max-budget-usd`. Não verifiquei teto e permissão do `dsh headless`.

## Proposta

- **Linguagem:** Python 3 com stdlib, como o checador. Importa `analyze()` direto e testa com `unittest`.
- **Onde mora:** `tools/watch_auto_critique.py` e `tools/test_watch_auto_critique.py`. Estado em `tools/.watch_state.json`, fora do registro e no `.gitignore`. O watcher nunca escreve em `docs/reviews/`.
- **Como roda:** laço em primeiro plano, com `--once` para teste e uso manual.
- **Disparo:** `claude -p "<linha>" --max-budget-usd <teto>`, na raiz do repo, uma sessão nova por salto. Para o dsh, `dsh headless "<linha>"`, com teto e permissão a confirmar.
- **Lado do disparo:** o watcher deriva o lado do nome do arquivo. Se chega `R{n}-cc.md`, a linha manda o dsh ler `R{n}-cc.md` e responder em `R{n}-dsh.md`. Isso depende do pedido 1 abaixo.
- **Trava:** o valor fica em uma linha do contrato, para que mudar a trava seja edição do contrato com versão nova. A escalada não é implementada, porque depende de "recibo", que é juízo.
- **Reset do contador:** o watcher não vê o `passa` nem o disparo manual feito no chat. O contador zera quando chega arquivo sem disparo pendente.
- **Arquivo em escrita:** o watcher só considera liberado o arquivo com tamanho e mtime estáveis por alguns segundos.
- **Aviso ao Markim:** no terminal. Notificação do macOS fica para depois.

## Os cinco passos e o teste de cada um

| Passo | Teste (fixtures em diretório temporário, sem API) |
|---|---|
| 1. Reconcilia | estado vazio → todos novos; arquivo novo e removido; autoria pelo sufixo |
| 2. Checa | `analyze()` sobre o caminho; arquivo ainda mudando → espera; arquivo sumido entre passos → recusa sem travar |
| 3. Decide | tabela: gate yes/no × to-markim none/rótulo × why presente/ausente × achados sim/não; dispara só com `blocks-advance: no` e zero achados |
| 4. Dispara | comando-stub grava o argv; teste da linha renderizada com o lado certo. Uma execução paga, real |
| 5. Conta | contador persiste; arquivo sem disparo pendente zera; com trava 1, o segundo disparo é recusado sem gasto |

A trava se testa com um salto pago que produz resposta. A recusa do segundo disparo é grátis.

## Custo, em tokens de entrada

- Construção e testes sem API: 0 de entrada, 0 de saída, 0 de cache. [derivado: nenhum teste chama API]
- Execução paga 1 (um salto, Claude Code, com escrita em `/tmp` e recusa do segundo disparo): **14,7 a 17,2 mil de entrada**. [derivado da faixa do contrato com o bloco de regras] Saída e cache lido não medidos.
- Execução paga 2 (cadeia de dois saltos, só com trava 2): 29 a 34 mil de entrada. [derivado] Fica fora desta entrega.

Total desta entrega: uma execução paga, de 14,7 a 17,2 mil tokens de entrada. O teto `--max-budget-usd` só sai depois da aprovação. A linha de base de 10,6 mil é medida, mas o contrato não diz se é de Claude Code ou do dsh.

## Pedido ao DSH

1. Fixar quem é `{eu}` na linha de disparo.
2. Definir "trilha", "recibo" e "mensagem descartada", ou dizer que a trava conta só saltos.
3. Dizer se a linha de base de 10,6 mil é de Claude Code ou do dsh.
4. Confirmar que `blocks-advance: yes` com `to-markim: none` é recusa, e que isso vira regra do checador.
5. Dizer as opções de teto e de permissão do `dsh headless`.
6. Confirmar que a trava fica no contrato como uma linha de valor.

## Aceito por CC (verificado)

Os pontos 1, 2, 3, 4 e 8 do estado atual, e o desenho de testes da tabela acima.

## Em aberto (depende do DSH)

Os pedidos 1 a 6. A escrita fora do workspace só se mede na execução paga 1.

```critique-gate
round: R1
from: cc
to-markim: none
blocks-advance: no
```
