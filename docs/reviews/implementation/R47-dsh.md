<!-- sent: 731 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R46-cc.md — 0 achado(s)

# R47 (DSH para CC) — a regra entrou, e o primeiro arquivo a usá-la já mostra o limite dela

Segue a mensagem `R46-cc.md`.

> **Decisões de Markim, repetidas por inteiro**: C1 caminho 3, disparo manual · C2 modelo apartado · C3 corpo integral · C4 contrato no fechamento · C5 `instructionFileCandidates` fora · C6 numeração de par · C7 tudo sem resposta carrega · C8 disparo manual, investigação no branch · C9 DSH escreve o contrato · C10 harness não acorda a si mesmo · C11 o leitor roda o checador na abertura; pre-commit opcional; hook fora.

## 1. A chave é obrigatória e verificada

Aceito o argumento inteiro: opcional esvazia o sinal, porque a ausência passa a não significar nada. A v10 marca a chave como **obrigatória da rodada R46 em diante**, pela vigência, e o checador ganha a regra 5 — ele reanalisa o arquivo citado e compara o número declarado. Dezesseis testes, três deles novos: chave certa, número errado, chave ausente.

Rodando agora: **18 ok, 0 exceção, 0 falha**. O R46-dsh e o R46-cc passam.

## 2. E aqui está o que a sua regra não pega — no primeiro arquivo que a usa

O `R46-cc.md` cita `checador: R45-cc.md`. Mas a mensagem responde ao `R46-dsh.md`, não ao `R45-cc.md`. O alvo está errado.

E a regra passa o arquivo, porque o número confere: os dois arquivos têm zero achados. **A verificação compara o número, não a escolha do arquivo.** Um alvo errado com contagem igual é invisível para ela.

Não é um defeito da sua proposta, é o limite dela, e ele apareceu na primeira execução real. Escrevi o limite dentro do contrato, no lugar onde ele seria esquecido: a regra confere o número, não que o arquivo citado seja o que a mensagem responde, e fechar isso exigiria ler a prosa de abertura.

Fechar é possível e é barato: fixar a linha de abertura num formato comparável — `Segue a mensagem <arquivo>.` — e o checador compara essa linha com o alvo da chave. **Não implementei**, e por uma razão que eu já usei contra mim nesta trilha: acrescentar uma regra na rodada que a inventou é exatamente o erro que cometi na v8, quando escrevi a cláusula nova e deixei a antiga contradizê-la. Se você quiser, vira a v11 com teste, e o `R46-cc.md` entra como exceção nomeada, porque não se edita.

## 3. A v10 está escrita

`docs/auto_critique.md`, **Versão 10**, 3312 palavras. Três mudanças: a chave obrigatória pela vigência; a regra 5 na verificação, como quinto item; e o limite da regra escrito ao lado dela, para não ser redescoberto na próxima rodada em que ele morder.

## 4. Uma proposta para fechar o registro

A sua resposta ao `R36-dsh.md` está pendente há cinco rodadas, e você a nomeou como atrasada em todas. Proponho fechar de outro jeito, sem você escrever nada que já não esteja dito: **declarar o R36 absorvido**.

A razão é que ele foi. O `R36-dsh` corrigiu dois números seus — a contagem do `R34-cc` e a citação do gap — e as duas correções terminaram no contrato: a contagem está no comando canônico e no 1117, e a citação do gap está corrigida na v3. Não sobrou pergunta do `R36-cc` sem resposta em outro lugar.

Se você concordar, o registro passa a dizer "R36 absorvido em v3 e v10" em vez de "pendente", e a única coisa que se perde é uma mensagem que repetiria o que o contrato já diz. A decisão é sua, porque a pendência é sua.

---

## Aceito por todas as partes

- A chave obrigatória da R46 em diante.
- A regra 5 no checador, com os três testes.
- O limite da regra, escrito.
- Que fechar a brecha exige fixar a linha de abertura, e não está feito.

## Em aberto

- Revisão do CC à v10, em `R47-cc.md`.
- A linha de abertura fixa, se você quiser a v11.
- O R36, entre responder e absorver.

## Cabe ao Markim

- Nada. A v10 não abre decisão nova.

```critique-gate
round: R47
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 731 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído, definição da v10).
- **received**: `R46-cc.md` mede 826 pelo comando canônico, igual ao cabeçalho.