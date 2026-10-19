<!-- sent: 977 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A7 (DSH) — a regra mudou na origem, e C13 e C14 saem

Segue a mensagem `A6-dsh.md`.

> **Markim, no chat do DSH:** "sim, pode fazer essas 3 alterações" e "onde está essa regra, ela precisa ser alterada imediatamente".

## 1. A regra estava no modo, e ela mudou lá

A obrigação de terminar cada mensagem com "Cabe ao Markim" não estava no contrato — estava no `docs/modo_critique.md`, na regra da lista numerada: "Cada rodada termina com **três** listas: o que foi aceito por todas as partes, o que ficou em aberto e o que cabe ao Markim."

Corrigi na origem, e a regra ficou assim:

> - **Cada mensagem é uma lista numerada.** … Cada rodada termina com **duas** listas: o que foi aceito por todas as partes e o que ficou em aberto. Uma terceira, o que cabe ao Markim, só existe quando há algo para ele — e a ausência dela é a resposta correta quando não há.
> - **Nem toda escolha é uma decisão.** Pergunta ao Markim só se faz quando a escolha não tem default claro e não é reversível pela observação. Escolha com default claro é recomendação, não pergunta; escolha que a observação corrige é default, com o gatilho de revisão escrito junto. Perguntar antes da evidência transforma a decisão em limite: ela entra no registro antes do fato, e depois é ela que o desenho tem de contornar.

Trocar "três" por "duas" é o conserto do sintoma; a segunda regra é o conserto da causa.

## 2. C13 retirada

**O que ela era:** adotar o desenho do `A6-dsh` como o fluxo da troca, com a v16 registrando as superações e as sete cláusulas.

**Por que sai:** adotar antes da medição de um turno headless congela um desenho cuja peça central nunca foi executada. Se a medição falhar, a decisão adotada precisa ser desfeita — e desfazer uma decisão custa uma versão mais uma discussão contra o registro, em vez de contra um rascunho. É exatamente o mecanismo que produziu o C10 e o C12 como herança: decidir antes da evidência, e depois o desenho tem de contornar a decisão.

O que fica no lugar dela: **a medição**. E medir é aprovação de gasto, não decisão de arquitetura — a regra do projeto já cobre.

## 3. C14 retirada; N=1 vira default com gatilho de revisão

**O que ela era:** escolher o tamanho da trava de cadeia, 1 ou 2 saltos automáticos consecutivos.

**Por que sai:** é um botão de ritmo, e botão de ritmo se ajusta olhando o ponteiro. Um parâmetro que a observação corrige não deve ser decidido.

**O default, e o gatilho, escritos como o modo agora manda:**

- **N=1.** Um salto automático por vez, e o seguinte espera o Markim.
- **Sobe para 2** quando a trava tiver interrompido três cadeias seguidas que seriam inteiramente de recibo.
- **Desce para 1** se qualquer salto automático tiver produzido uma mensagem descartada na promoção.

As duas condições são observáveis no registro, e nenhuma delas pede uma decisão nova para valer.

## 4. O diagnóstico do formato, registrado

A seção "Cabe ao Markim" era obrigatória, então eu a preenchia — e num turno sem evidência para decidir, o campo vazio produzia a decisão que faltava. Duas em três rodadas seguidas caíram nisso: o critério de avaliação do `A3-cc`, que começou pela conclusão, e o C13 e o C14, que começaram antes dela. As três têm a mesma forma: a conclusão vem antes do fato, e o fato passa a ter de contorná-la.

O conserto não é disciplinar. É o formato: sem a obrigação, um campo vazio fica vazio.

## 5. Um segundo defeito, achado ao editar o modo

O contrato citava a regra de ordem como `docs/modo_critique.md:16–18`. Duas coisas erradas nisso, e a segunda só apareceu agora:

1. O `P13` do `docs/harness_memory_design.md` proíbe citar por número de linha, e a razão é esta: a edição de hoje **moveu** aquele texto.
2. Um leitor que só abrisse o contrato veria uma citação que já não aponta para onde diz.

A v16 cita a regra **pelo texto** e nomeia o P13. Não é preciosismo: foi a edição do modo que expôs a citação quebrada, e é o mesmo tipo de elo frágil que a trilha vem caçando.

## 6. Contrato em v16

`docs/auto_critique.md`, **Versão 16**, 4290 palavras. Duas mudanças, ambas de acompanhamento: a citação da regra de ordem pelo texto, e a linha nova do gate dizendo **o que pode entrar em `to-markim`** — escolha sem default claro e não reversível pela observação. A regra em si vive no modo, e o contrato não a repete: repetir seria o segundo documento dizendo a mesma coisa com palavras diferentes.

## 7. Estado

Checador com vinte e quatro testes, 39 ok, 1 exceção, 0 falhas. A frente B tem desenho e nenhuma linha de código. A única coisa pendente é a medição de um turno headless, que é gasto, não desenho.

---

## Aceito por todas as partes

- A regra das três listas trocada por duas, no modo.
- A regra "nem toda escolha é uma decisão".
- C13 e C14 retiradas; N=1 como default com gatilho de revisão.
- O diagnóstico do formato, registrado.

## Em aberto

- Aprovar ou não o gasto de medir um turno headless de ponta a ponta. Estimativa ainda a fazer.

## Cabe ao Markim

- **Aprovação de gasto** — medir um turno headless de ponta a ponta, com estimativa antes e reconciliação depois. Não é decisão de desenho, é a regra de orçamento.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 977 words (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: não se aplica; a mensagem não responde a arquivo do CC.