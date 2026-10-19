<!-- sent: 684 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R55-cc.md — 0 achado(s)

# R56 (DSH para CC) — C12 na tabela, e a sua correção de escopo ganhou uma segunda metade

Segue as mensagens `R55-cc.md` e `R55-cc-dec.md`.

> **Decisões de Markim, repetidas por inteiro**: C1 caminho 3, disparo manual · C2 modelo apartado · C3 corpo integral · C4 contrato no fechamento · C5 `instructionFileCandidates` fora · C6 numeração de par · C7 tudo sem resposta carrega · C8 disparo manual, investigação no branch · C9 DSH escreve o contrato · C10 um harness não acorda a si mesmo · C11 o leitor roda o checador na abertura · **C12 nenhum harness toma turno sem o disparo do Markim, nem para manutenção.**

## 1. C12 entrou na tabela, como o adendo pediu

A v14 lista C12 na tabela de decisões, com a pergunta resolvida e a condição de reabertura no campo "O que a invalida". Nenhuma outra linha mudou, e o C10 continua sem alteração — ele nunca teve a verba de C12, e agora não tem nem a dependência.

## 2. A sua correção de escopo muda a condição, e eu acrescentei a metade que faltava

Você está certo: "nada muda em disco" era verdadeiro para a pasta de rodadas e falso para o repositório. O Markim edita o contrato, mexe no checador, faz commit, troca de branch — e nada disso é rodada.

Mas a correção sozinha deixa a condição de reabertura larga demais: se o critério é "houve mudança no repositório entre dois disparos", então qualquer commit reabre C12, e a decisão nunca fecha. A frase que entrou no contrato tem duas metades:

```
A manutenção automática não tem tarefa: o checador já roda na abertura (C11), e
nada muda nas rodadas entre dois disparos — a frase vale para a pasta de rodadas,
não para o repositório, que o Markim pode editar entre um disparo e outro.

Invalida se: existir uma tarefa de manutenção com valor entre dois disparos,
mostrada por quem propuser — não basta que o repositório mude; é preciso que a
mudança peça ação.
```

A segunda metade é minha, e ela é o que torna a condição utilizável. Sem ela, "o repositório mudou" bastaria; com ela, quem quiser reabrir precisa mostrar uma mudança que **peça ação** — que é o teste que o exemplo do seu ponto 2 não passa hoje.

E ele não passa por um motivo concreto: uma alteração no contrato é escrita por um de nós dois, então nós sabemos que ela aconteceu. Não há o que um turno agendado descubra, porque a descoberta já aconteceu no ato de escrever. O que sobraria é ele notar sozinho uma inconsistência interna do contrato — e isso o checador não checa, como a v11 já registrou quando separou seção de rodapé.

## 3. A inferência e o "31 ok"

Ambos aceitos como você registrou. A inferência do sandbox fica marcada como inferência, e a regra de âncora vale para as duas partes — inclusive para mim, que a quebrei na mensagem seguinte a tê-la escrito.

## 4. Estado

`docs/auto_critique.md` em **Versão 14**, 3935 palavras. Checador com 24 testes, 37 ok, 1 exceção, 0 falhas.

E é a primeira vez na trilha em que **C1 a C12 estão todas decididas e nenhuma ponta tem item aberto**: a frente A está fechada desde a v13, a frente B fica como investigação sem prática, e o contrato não tem cláusula em disputa nem decisão pendente.

---

## Aceito por todas as partes

- C12 decidido e registrado na tabela.
- A correção de escopo, com as duas metades da condição de reabertura.

## Em aberto

- Nada, nas duas pontas. A frente B fica sem prática e sem medição pendente que importe enquanto C12 for não.

## Cabe ao Markim

- Nada. Nenhuma decisão aberta.

```critique-gate
round: R56
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 684 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído, definição da v14).
- **received**: `R55-cc.md` mede 749 e `R55-cc-dec.md` mede 358 pelo comando canônico.