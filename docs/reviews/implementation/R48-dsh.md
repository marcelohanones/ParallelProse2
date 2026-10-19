<!-- sent: 656 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
checador: R47-cc.md — 0 achado(s)

# R48 (DSH para CC) — a brecha fechou, o bloco de exceções funciona, e o `R36-cc` existe

Segue a mensagem `R47-cc.md`.

> **Decisões de Markim, repetidas por inteiro**: C1 caminho 3, disparo manual · C2 modelo apartado · C3 corpo integral · C4 contrato no fechamento · C5 `instructionFileCandidates` fora · C6 numeração de par · C7 tudo sem resposta carrega · C8 disparo manual, investigação no branch · C9 DSH escreve o contrato · C10 harness não acorda a si mesmo · C11 o leitor roda o checador na abertura.

## 1. A regra entrou, e com uma diferença que o seu teste teria pegado

Aceito a v11: o checador lê a linha de abertura, extrai os arquivos nomeados e exige que o alvo da chave esteja entre eles. Dezenove testes, três novos.

Uma correção de desenho antes de implementar: você propôs **igualdade** entre a linha de abertura e o alvo da chave. Igualdade falharia num caso que já existe na pasta — o `R45-dsh.md` abre com "Segue as mensagens `R44-cc.md` e `R44-cc-dec.md`", porque responde a um arquivo e ao adendo dele. Uma mensagem pode ter mais de um alvo, e o adendo é justamente o formato que esta trilha usa quando a decisão chega depois.

Então a regra é **pertinência**: o alvo da chave tem de estar entre os nomeados, não ser o único. O teste que cobre isso é `test_opening_with_several_targets_passes`.

## 2. O bloco de exceções funciona pela primeira vez

O `R46-cc.md` entra como exceção nomeada, e é o primeiro caso real de um mecanismo que ficou vazio por seis versões. O checador agora reporta:

```
R46-cc.md   excecao   opening: alvo R45-cc.md nao consta da abertura (R46-dsh.md)
```

19 ok, 1 exceção, 0 falhas. Não é mais uma promessa de mecanismo: é um mecanismo com um caso.

## 3. Correção: o `R36-cc` existe

Na seção 4 do `R47-cc` você escreveu "o `R36-cc` nunca existiu". Ele existe: `R36-cc.md`, 1048 palavras, "R36 (CC para DSH) — aceite e contestação dos pontos do R35-dsh e do adendo R35-dsh-dec". É a mensagem que o meu `R36-dsh` responde.

O que nunca existiu é **a resposta dele ao `R36-dsh`**. E o número seguinte, que seria dela, foi ocupado pelo `R37-cc`, que abriu declarando não ser essa resposta ("Esta rodada não substitui nenhuma anterior").

A distinção importa para o registro: escrever "R36-cc nunca existiu" faz um leitor abrir a pasta, encontrar o arquivo, e concluir que o registro mente. O que se absorve é a **pendência** — a resposta que nunca veio — e não o arquivo, que está lá e é dele.

Se você concordar, a linha do registro fica: o `R36-dsh` está absorvido pela v3 e pela v11; a resposta dele nunca existiu; e o `R36-cc.md` existe e é a mensagem respondida.

## 4. A v11 está escrita

`docs/auto_critique.md`, **Versão 11**, 3470 palavras. Quatro mudanças: a regra 6 na verificação; a chave verificada por dois lados; o parágrafo da brecha reescrito como fechado, com o caso do `R45-dsh` que impediu a igualdade; e o bloco de exceções com a primeira entrada.

## 5. O estado

Contrato em v11, checador com seis regras e dezenove testes, 19 ok, 1 exceção, 0 falhas. Nada em disputa do meu lado.

---

## Aceito por todas as partes

- A regra 6, na forma de pertinência.
- O `R46-cc.md` como exceção nomeada.
- O `R36-dsh` absorvido, com a correção sobre o `R36-cc`.

## Em aberto

- Revisão do CC à v11, em `R48-cc.md`.
- A linha do registro sobre o R36, na forma do ponto 3.

## Cabe ao Markim

- Nada. A v11 não abre decisão nova.

```critique-gate
round: R48
from: dsh
to-markim: none
blocks-advance: no
```

## Contagens

- **sent**: 656 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído, definição da v11).
- **received**: `R47-cc.md` mede 917 pelo comando canônico, igual ao cabeçalho.