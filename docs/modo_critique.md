# Modo CRITIQUE

**O que é.** Um modo de trabalho em que duas partes planejam juntas antes de qualquer execução, com uma terceira
parte que decide: o Markim. Nada é executado, e nenhum gasto é feito, até que as três partes concordem com o plano,
o resultado esperado e os riscos. As duas partes que propõem e criticam são as que conversam sobre o
trabalho; no novo repositório, uma dessas partes é a IA editorial.

**Regras de funcionamento**

- **Cada mensagem é uma lista numerada.** Cada ponto tem um número, para que possa ser respondido, mantido ou
  retirado por referência. Cada rodada termina com duas listas: o que foi aceito por todas as partes e o que ficou
  em aberto. Uma terceira, o que cabe ao Markim, só existe quando há algo para ele — e a ausência dela é a resposta
  correta quando não há.
- **Nem toda escolha é uma decisão.** Pergunta ao Markim só se faz quando a escolha não tem default claro e não é
  reversível pela observação. Escolha com default claro é recomendação, não pergunta; escolha que a observação
  corrige é default, com o gatilho de revisão escrito junto. Perguntar antes da evidência transforma a decisão em
  limite: ela entra no registro antes do fato, e depois é ela que o desenho tem de contornar.
- **Decisões do Markim têm rótulo próprio** (uma letra e um número, por exemplo `D1`), e são repetidas por inteiro
  no topo de cada mensagem seguinte. Ele precisa ser citado de forma explícita; não deve ter de adivinhar que uma
  pergunta é dele.
- **As perguntas do Markim vêm antes da resposta à outra parte.** Quando uma rodada levanta algo que ele precisa
  decidir ou esclarecer, essas perguntas são enviadas sozinhas, e a mensagem para a outra parte só é escrita depois
  da resposta. Isso evita reescrever a mensagem a cada resposta.
- **Verificar antes de aceitar.** Cada parte reexamina os registros e o código, e reproduz os números da outra
  antes de aceitá-los. Correções importantes costumam ser erros de aritmética encontrados dessa forma.
- **Fixar a barra e a regra de decisão antes de gastar.** A barra e a regra de decisão são escritas antes da
  execução e não podem ser trocadas depois do resultado. Se a métrica for escolhida depois de ver um resultado
  ruim, ela só vale para o futuro, e os dois números são registrados.
- **Uma mudança por execução paga.** Mudar duas coisas ao mesmo tempo torna o resultado impossível de atribuir.
- **O resultado é escrito no formato do projeto:** o que foi feito, por que, o critério cumprido célula por célula,
  e o que o item não resolve.

**Canais.** A comunicação entre as partes ocorre pelo registro: cada parte escreve seus documentos em `docs/`,
e no registro de rodadas em `docs/reviews/` cada lado escreve só o próprio arquivo, conforme o `README.md` dessa
pasta. O que faz um lado começar a responder é a **liberação** do arquivo, descrita em `docs/auto_critique2.md`.
Não há canal direto entre os harnesses. A memória compartilhada (camada 2 do `docs/harness_memory_design.md`) não é canal de mensagens:
ela guarda fatos e decisões duráveis, e o alcance dela no outro harness não é garantido em tempo real.

**Por que existe.** O valor do modo está em que uma afirmação precisa sobreviver a alguém refazendo a conta a partir
dos arquivos. Ele só funciona se o critério existir antes da quantidade estimada de chamadas e se as partes se corrigirem pela medição, e não
pela argumentação.

**Como aplicar.** Antes de qualquer execução: numerar os pontos, verificar localmente cada afirmação da outra parte,
dizer o número de chamadas previsto, e nunca decidir nada que pertence ao Markim. Nenhum dos números, barras ou participantes de
rodadas anteriores vale como ponto de partida; cada rodada nova define os seus.
