# Contrato da troca automatizada — ParallelProse2

**Versão 8 — 2026-10-19.** Escrito por DSH. A v8 tira a Regra 6 do lado cc: aquele lado roda na assinatura do plano Pro, informada pelo Markim, e não cobra por token, então não há gasto a estimar nem a reconciliar ali; a regra do gasto vale onde a sessão cobra por token, que hoje é o dsh. O motivo é a M3: o teto em dólar existia sobre uma premissa que não vale. A v7 troca o escopo da transição: ela não expira quando o watcher existe — existir não é disparar —, e vale sempre que o watcher não dispara aquele salto: sem passada, depois da trava, ou num lado sem comando configurado. O motivo é a R5-cc, disparada à mão com o watcher já existindo e o contador em 1: existir não é disparar, e a transição dava-se por expirada. A v6 tira a frase que mandava "mudar o `yes` para `no`": o gate é escrito uma vez, com o estado da mensagem, e não muda. O arquivo com pergunta é gravado ao fim do turno com `blocks-advance: yes`, não dispara, e nunca é editado; a resposta é arquivo novo, gravado depois do `passa`, com `blocks-advance: no`. A parte C do cenário continua valendo no que ela diz do arquivo que inicia o próximo harness — esse só vai depois do `passa` —, e o arquivo com a pergunta não inicia nada. O caso concreto é a `R3-dsh.md`, que ficou `yes`, e a `R4-cc.md`, que respondeu com `no`, sem que nenhum dos dois fosse editado. A v5 troca a estimativa de uma chamada pela medição do primeiro salto pago — 40 chamadas, 55.434 de entrada nova, 69.776 de saída, 3.285.888 de cache lido, 0 de cache escrito —, e a Regra 6 passa a exigir o número de chamadas na estimativa e o log de sessão na reconciliação; o motivo é que o laço de ferramentas multiplica a conta e a tabela antiga contava uma chamada. A v4 paga a contradição que a v3 deixou: as duas frases que ainda usavam "trilha" como se ela existisse — no arquivo da rodada e na seção do registro — passam a `docs/reviews/` e a "sem subpasta"; o motivo é que o texto que define o formato não pode negar a si mesmo. A v3 põe no texto o que o checador já exigia e o contrato não dizia — o info da cerca do gate, as chaves contíguas à contagem, a linha de abertura, o adendo com hífen —, declara incoerente o `yes` sem rótulo, corrige a aritmética do cache lido, que não decorria do método que a própria tabela declarava, registra a medição do `EPERM` sob sandbox, conserta as crases que a v2 perdeu na Regra 5, e tira "trilha", que ficou sem referente quando a subpasta saiu. Este documento governa a troca de mensagens entre Claude Code e dsh, e nada além dela. Ele é autônomo: não cita e não depende de outro documento. **É o único contrato que governa a troca desde 2026-10-19; nada anterior a esta data governa o disparo nem o formato.**

## O cenário

O texto abaixo é do Markim, transcrito sem correção nenhuma — nem de ortografia, nem de acento. Ele é o objetivo deste documento.

```text
o que eu imagino sobre essa automacao é que um herness sempre vai trigar o outro
atraves de um arquivo que o outro harness monitora e usa como start. Nas rodadas
onde há perguntas humanas, essas perguntas sao respondidas e no evento do comando
passa, o harness registra o arquivo na pasta monitorada que inicia o proximo
harness. Quando nao ha perguntas, cada harness se cominica com o outro atraves do
arquivo na pasta monitorada. quando há perguntas, ocorre o mesmo, porem somete
apos o comando "passa".
```

## A regra de derivação

**Toda regra deste documento existe para implementar o cenário acima.** Ela nomeia, junto de si, a parte do cenário que serve; se não servir a nenhuma, não entra; se deixar de servir, sai. Uma regra sem essa ligação é uma regra a ser removida, e não uma regra a ser obedecida.

O cenário tem três partes:

- **A** — o arquivo na pasta monitorada é o start do outro harness.
- **B** — sem pergunta, o arquivo vai direto.
- **C** — com pergunta, o arquivo que inicia o próximo harness só vai depois do `passa`; o arquivo com a pergunta não inicia nada.

## As regras

### Regra 1 — a pasta é o canal, e escrever o arquivo é a liberação

**Serve a:** A.
**Premissa:** o registro é o único lugar que os dois lados conseguem ver, e a escrita é o instante em que uma mensagem passa a existir.
**Invalidaria:** a troca deixar de passar pelo registro — um processo chamando o outro diretamente, sem arquivo.

### Regra 2 — sem pergunta em aberto, o arquivo vai ao fim do turno

**Serve a:** B.
**Premissa:** o bloco de gate declara as perguntas de forma que um script leia; e um harness honesto não escreve mensagem com pergunta que ele mesmo não declarou.
**Invalidaria:** a subdeclaração virar norma — mensagens carregando pergunta que o gate não registra.

### Regra 3 — com pergunta em aberto, a resposta espera o `passa`

**Serve a:** C.
**Premissa:** o arquivo com pergunta é gravado ao fim do turno com `blocks-advance: yes` e não dispara; o `passa` libera o arquivo seguinte, que é a resposta e entra com `blocks-advance: no`. O arquivo com a pergunta não é editado; o registro da resposta é o arquivo novo.
**Invalidaria:** a resposta passar a ser uma edição do arquivo com a pergunta, ou o `passa` liberar o próprio arquivo com `yes`.

### Regra 4 — o watcher dispara o outro lado, e recusa o salto, nunca a rodada

**Serve a:** A.
**Premissa:** o checador dá um veredito por arquivo, sem decisão de sentido — ele diz se o arquivo está bem formado, não se ele está certo.
**Invalidaria:** a recusa do watcher passar a decidir o sentido da rodada; uma checagem que decide não é checagem.

### Regra 5 — a cadeia tem trava

**Serve a:** A.
**Premissa:** o gate classifica uma mensagem, não uma sequência; uma sequência de recibos pode convergir para algo que ninguém autorizou.
**Invalidaria:** a rodada sem pergunta deixar de existir por construção — sem recibo, a cadeia não chega a conclusão nenhuma.

**O default é 1 salto.** Sobe para 2 quando a trava tiver interrompido três cadeias seguidas que seriam inteiramente de recibo; desce para 1 se algum salto automático tiver produzido mensagem descartada. A escolha é observável no registro, e não pede decisão nova.

**"Recibo" é proxy.** Quem o define é o gate, e não o conteúdo: uma mensagem com a entrada em `to-markim` igual a `none` e sem bloco pendente passa por recibo, tenha ela conteúdo ou não. A trava padrão não usa esse termo; só a escalada usa, e por isso a escalada é observável e a trava não. Quem for subir a trava de 1 para 2 está medindo um proxy, e deve dizer isso.

**"Mensagem descartada" é a que o checador reprova — e ela não some.** Ela continua no registro, e o watcher recusa o **salto**, não a rodada: a mensagem fica lá, e o próximo salto espera o Markim. Descartada quer dizer descartada *da cadeia automática*, não do registro.

### Regra 6 — cada salto no lado que cobra por token é execução paga

**Serve a:** A e B.
**Premissa:** cada salto sobe uma sessão nova, e a sessão faz uma chamada por passo do laço de ferramentas; a primeira chamada é o piso medido, cerca de 10,6 mil tokens de entrada nova, e o laço multiplica o custo.
**Invalidaria:** o salto passar a rodar em modelo local, ou o custo cair a ponto de não precisar de estimativa.

**Escopo: o lado que cobra por token.** Hoje é o dsh. O lado cc roda na assinatura do plano Pro, informada pelo Markim em 2026-10-19, e ali não há custo de API por token a estimar nem a reconciliar — o limite é o do plano, não um orçamento.

Estimativa antes, reconciliação depois, com quatro campos separados — entrada nova, saída, cache lido e cache escrito — e cada campo com o rótulo de medido ou derivado. A estimativa diz quantas chamadas o salto deve fazer; sem esse número ela estima uma chamada, não um salto. Um total único esconde o campo que mais pesa. A reconciliação lê o log de sessão do dsh; o log do watcher guarda a saída do salto.

## O watcher

Ele é a única peça que faz o cenário acontecer, e o que ele faz é isto, nesta ordem:

1. **Reconcilia** na abertura: lista a pasta, compara com o último estado, e sabe quem escreveu o quê.
2. **Checa** o arquivo liberado por arquivo — `analyze()` sobre o caminho, não a varredura da pasta — porque a decisão dele é sobre um arquivo.
3. **Decide**: gate sem pergunta em aberto, dispara o outro lado; gate com pergunta, não dispara, e avisa no chat do Markim.
4. **Dispara** o outro harness com a linha de disparo.
5. **Conta** o salto na cadeia.

Ele **nunca escreve no registro** e **nunca responde por um harness**. Se ele parar, a troca volta a ser manual — é para isso que serve a transição.

**Como ele chama o dsh:** `dsh --profile headless`. A forma `dsh headless` também vale — as duas são gramática do mesmo comando, e `--profile` é a canônica só por dizer o que faz, não porque a outra erre.

**Onde ele roda: fora do sandbox.** O perfil do dsh é gravado em `~/.dsh` antes de qualquer chamada de API, e um sandbox de escrita bloqueia ali com `EPERM` — o erro não é da forma do comando, é do lugar onde ele roda. Medido em 2026-10-19: sob sandbox de escrita, `dsh headless --help` para em `~/.dsh/profiles/headless/cordis.yml` com `EPERM` e sai com código 1.

## A cadeia

- Um **salto** é um disparo do watcher.
- O contador **zera** quando o Markim dispara à mão, e quando a rodada termina sem arquivo a responder.
- Ao bater a trava, o watcher não dispara, avisa no chat, e o próximo salto espera o Markim.

## O que foi medido

| medida | valor | como |
|---|---|---|
| linha de base de instruções, por sessão | ~10,6 mil tokens de entrada nova | medido em três execuções headless; na execução da R2-dsh, a primeira chamada tem 10.713 |
| primeira chamada com o bloco de regras, prompt total | 14,7 a 17,2 mil (medido: 15.833) | derivado da base de 12.318; a medição da R2-dsh cai dentro da faixa |
| rodar o checador com a saída descartada | ~26 tokens | diferença na mesma posição de chamada |
| trazer a saída do checador ao contexto | ~2.700 tokens | diferença na mesma posição de chamada |
| chamadas de um salto | 40 | medido no log de sessão da R2-dsh, 2026-10-19; depende das ferramentas usadas |
| salto medido — entrada nova | 55.434 | medido: soma de `inputTokens` das 40 chamadas |
| salto medido — saída | 69.776 | medido: soma de `outputTokens` |
| salto medido — cache lido | 3.285.888 | medido: soma de `cacheReadTokens` |
| salto medido — cache escrito | 0 | medido: soma de `cacheWriteTokens` |
| prompt total do salto medido | 3.341.322 | derivado: entrada nova + cache lido, 40 chamadas |

**Os campos são os do log de sessão do dsh:** entrada nova é `inputTokens` (o que não veio do cache); cache lido é `cacheReadTokens`; cache escrito é `cacheWriteTokens`; saída é `outputTokens`. O prompt de uma chamada é entrada nova + cache lido; o custo do salto é a soma das chamadas.

**O que a faixa de 14,7 a 17,2 mil inclui:** a primeira chamada do salto, não o salto. Ela soma a base de 12.318, o bloco de regras de 2.153 e a rodada lida, de 230 a 2.724; a medição da R2-dsh dá 15.833 de prompt total. Ela **não** inclui ler o contrato inteiro (mais 5.932) nem o prompt do watcher (cerca de 400). Um salto que faça qualquer das duas coisas custa mais, e a estimativa tem de dizer qual dos casos está estimando. O salto inteiro é a soma das chamadas: 40 no medido, e o número cresce com as ferramentas.

**A medição separa o que a tabela antiga misturava.** A linha de base de 10,6 mil é a entrada nova da primeira chamada; a composição de 14,7 a 17,2 mil é o prompt total dessa chamada. A medição da R2-dsh dá 10.713 de entrada nova, 5.120 de cache lido e 15.833 de prompt na primeira chamada; no salto, 55.434, 3.285.888 e 3.341.322. Quem estima diz se está estimando a primeira chamada ou o salto, e quantas chamadas o salto deve fazer.

**O lado cc não entra nesta tabela.** Ele roda na assinatura do plano Pro, informada pelo Markim, e não cobra por token: não há base dele a medir. Os números acima são do dsh.

Estas são as medidas que sustentam as regras acima. As de 40 chamadas são do primeiro salto pago, a sessão `session-c220c8f8-a8d5-4af6-b1ba-df966fa29456`, que gravou a `R2-dsh.md` em **2026-10-19**; a conta é a soma de `inputTokens`, `outputTokens`, `cacheReadTokens` e `cacheWriteTokens` por chamada, e o log de sessão é o artefato. As demais foram feitas em sessões headless reais na mesma data, com reconciliação de tokens por chamada. Quem quiser refazê-las repete o experimento.

## A transição

**Enquanto o watcher não disparar aquele salto, o disparo é manual:** o Markim põe no chat do outro lado a linha de disparo, e nada acontece sozinho.

O watcher não dispara quando não está rodando, quando a trava o interrompe, ou quando aquele lado não tem comando configurado. Esta cláusula não é um segundo modo, e não deve ser reformulada em um: ela descreve o watcher que não dispara, não uma escolha entre dois caminhos.

## A mecânica

### O arquivo da rodada

- Um arquivo por lado por rodada, mesmo número: `R{n}-cc.md` e `R{n}-dsh.md`, em `docs/reviews/`.
- Criado pelo autor, nunca editado. O gate não é exceção: ele é escrito com o estado da mensagem e não muda depois. Correção é mensagem nova, ou adendo `R{n}-{lado}-{assunto}.md`, com o assunto em minúsculas ASCII e hífens — `R2-dsh-log-de-execucao.md`. O adendo corrige: não abre nem fecha rodada, e não conta para o par.
- **O registro é transporte, não arquivo.** A rodada existe enquanto a troca está aberta. O que precisa durar vai para este contrato, ou para o ledger da etapa — nunca fica só na rodada. Rodada é descartável; decisão não é.
- O corpo é a mensagem inteira, não o resumo.
- Estado derivado da existência: o par completo fecha a rodada; o lado que falta é quem responde. Um gap declarado fecha a vez sem arquivo.
- Um lado escreve no máximo uma vez por número; quando escreve de novo, o número sobe. Adendo com sufixo não conta.

### O cabeçalho e a contagem

Primeira linha, sempre:

```html
<!-- sent: N palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->
```

O cabeçalho conta inteiro, marcadores incluídos. O comando de contagem é obrigatório e é este:

```bash
LC_ALL=C wc -w <arquivo>
```

Sem o locale fixado o número muda com o ambiente. A diferença tem causa conhecida: a palavra `às` é um token no locale C e dois num locale UTF-8.

Depois da linha de contagem vêm as chaves, até a primeira linha que não seja chave:

- `gap: R{n}` — rodada que este lado não vai responder;
- `premissa-caida: <decisão> — <uma linha>` — premissa que uma resposta do Markim derrubou;
- `checador: <arquivo lido> — <n> achado(s)` — o que o checador reportou sobre o arquivo que esta mensagem responde.

A chave do checador é sobre o arquivo lido, nunca sobre o inventário da pasta: o inventário inclui a mensagem que está sendo escrita e muda no instante em que ela é gravada.

**As chaves começam na linha seguinte à contagem, sem linha em branco antes delas.** O leitor procura as chaves no primeiro bloco do arquivo, e um bloco em branco antes da primeira chave as esconde dele.

**A abertura** vem depois das chaves e antes do primeiro título: `Segue a mensagem <arquivo>` para uma mensagem respondida, `Segue as mensagens <arquivo> e <arquivo>` para mais de uma. O arquivo citado na chave do checador é um dos nomeados nela.

### O gate

O bloco é uma cerca cujo info é `critique-gate`; é o info que o identifica, e uma cerca com outro info conta como gate ausente.

```critique-gate
round: R{n}
from: cc | dsh
to-markim: <rótulos> | none
blocks-advance: yes | no
why-not-blocking: <uma linha, quando "no" e houver rótulo>
```

- `yes` impede que este arquivo dispare o próximo salto; o avanço vem do arquivo seguinte, e o `passa` é o cue que libera esse arquivo.
- **O gate é escrito uma vez, com o estado da mensagem: `yes` se ela carrega pergunta em aberto, `no` se não.** Ele nunca muda. O `why-not-blocking` diz por que um rótulo em `to-markim` não bloqueia; ele é exigido no arquivo com `no` que ainda cita o rótulo, porque a resposta já foi gravada. O formato não tem campo de "respondido": quem registra a resposta é o arquivo seguinte, que cita o rótulo no corpo e entra com `no`.
- `to-markim: none` não precisa de `why-not-blocking`.
- `yes` exige ao menos um rótulo em `to-markim`; `yes` com `none` é incoerente.
- O gate é o último bloco de conteúdo. Depois dele só pode vir o rodapé `## Contagens`, e nada depois do rodapé.
- Quem lê o gate é script, não modelo.

### Os cues

- O cue é a **primeira linha inteira**, aparada, exatamente `passa` ou `parcial`.
- `parcial` mostra no chat o que se entendeu; não grava, não muda estado.
- `passa` grava a mensagem seguinte no arquivo — a resposta —, e é a liberação (Regra 3). A mensagem com a pergunta já está no registro, com `yes`, e não é regravada.
- Mensagem sem cue é pergunta: responde e não muda estado.
- O harness **anuncia o cue detectado** na primeira linha da resposta, antes de agir.
- Detectar cue é interpretação, não mecanismo. O contrato promete que o erro aparece, não que ele não acontece.

### O checador

É `tools/check_auto_critique.py`, com testes em `tools/test_check_auto_critique.py`. Verificado quando os testes passam, não quando alguém lê o código.

Ele sinaliza e nunca edita. O leitor o roda na abertura; o watcher o roda antes de disparar; e os dois usam a mesma análise sobre o mesmo arquivo, então divergem no máximo por tempo.

## Verificação

1. o bloco de gate existe, parseia; depois dele só o rodapé `## Contagens` pode aparecer como seção, e nada pode vir depois do rodapé — regra `gate-last`;
2. `to-markim` e `blocks-advance` são coerentes entre si — regra `gate-coherence`;
3. `sent` no cabeçalho confere com `LC_ALL=C wc -w` — regra `sent`;
4. há no máximo um título `## Contagens` no arquivo — regra `single-footer`;
5. a chave `checador:` existe, cita um arquivo existente e não ambíguo, e o número declarado confere com a análise desse arquivo — regra `checador`;
6. o arquivo citado na chave está entre os nomeados na linha de abertura — regra `opening`.

**Vigência**: as regras de forma valem da **rodada R1** em diante, porque o registro começa vazio e não há histórico a preservar. Toda rodada escrita aqui é conferida.

**Obrigatória da rodada R2 em diante**: a chave do checador. A primeira mensagem de uma série não responde arquivo nenhum, e por isso não tem o que citar.

O bloco abaixo é onde divergências conhecidas ficam, uma por linha, com a razão. **Está vazio, e vazio é o estado correto** enquanto nenhuma existir:

```text
critique-exceptions
critique-exceptions-end
```

### A linha de disparo

Dois casos, duas formas:

```text
rodada aberta:  leia docs/reviews/R{n}-{autor}.md e responda em R{n}-{respondente}.md
par completo:   leia docs/reviews/R{n}-{ultimo}.md e responda em R{n+1}-{primeiro}.md
```

`autor` escreveu o arquivo lido; `respondente` é o outro lado; `primeiro` abriu a rodada `n`; `ultimo` escreveu o último arquivo dela — e é o `primeiro` quem abre a `n+1`.

O registro é uma série só, em `docs/reviews/`, sem subpasta. Quando o watcher não dispara, é o Markim quem usa a linha. A reconciliação na abertura — listar a pasta e comparar estados — é obrigatória de qualquer jeito.

## Quem escreve este contrato

- **Um escritor por arquivo.** Dois editores no mesmo texto divergem sem ninguém notar, e a divergência aparece como contradição meses depois. Este arquivo tem um escritor: DSH. O outro lado revisa e aponta; não edita.
- **Toda edição sobe a versão** e diz, em uma linha, o que mudou e por quê. A linha fica no próprio cabeçalho.
- **Definir termo é do escritor, não do leitor.** Quando um termo deste contrato estiver indefinido — "mensagem descartada", "inteiramente de recibo" —, quem o define é quem escreve o contrato. Isso não é decisão do Markim: é o trabalho de manter o texto utilizável.
- **Ao Markim cabe o que o contrato não pode decidir**: abrir mão de uma garantia, autorizar gasto, mudar o que o cenário pede. Uma pergunta que não é uma dessas três coisas é recomendação do escritor, com o gatilho de revisão escrito junto.

## O escopo

Este documento governa a troca entre os dois harnesses, desde 2026-10-19. Nenhum outro documento é citado por ele, e ele não cita nenhum.

**Referências a decisões de rodadas anteriores são história.** Rodadas escritas antes desta data citam contratos que não governam mais a troca; essas citações registram o que valia então, e não o que vale agora. A vigência é deste documento.

**Nenhuma regra deste contrato vem de arquivo apagado, de commit ou de rodada antiga.** Regra só existe aqui. Um número pode vir de qualquer lugar, e a única obrigação é dizer de onde veio e se é medido ou derivado. Encontrar o texto antigo não o transforma em regra, porque este contrato já declarou que não é.

---

## Contagens

- **sent**: 3725 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
