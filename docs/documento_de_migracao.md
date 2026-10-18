# Documento de migração

## [Instrução] O projeto em duas partes

**O que é o ParallelProse.** Um projeto que pretende colocar dois livros lado a lado, e perguntar o que cada um diz sobre os temas e as teses que ele mesmo escreve. Em termos de sistema, porém, a execução é de um livro de cada vez: a comparação acontece depois, na IA editorial. O resultado não é um resumo de cada livro nem uma lista de semelhanças: é uma prosa que mostra onde os dois autores convergem, onde divergem e o que só um deles sustenta. O nome vem daí: duas prosas paralelas, cada uma com seu endereço no texto original. O produto final é um roteiro de vídeo, e o crédito do roteiro não vem de achar acordo, que é o comportamento padrão de qualquer modelo, mas de recusar o que não se sustenta no texto.

O projeto tem duas partes com funções diferentes, e o resultado depende das duas. O retriever roda por livro: uma vez na primeira rodada e de novo sempre que a IA editorial pedir, sem juízo sobre suficiência e sem síntese.

**O retriever é a testemunha.** Não interpreta. Para cada livro, responde onde o livro fala da pergunta recebida, devolve o trecho exato com seu endereço e registra como procurou: quais variações da consulta tentou, o que voltou e por que parou.

**A IA editorial é a redatora.** Recebe o material de cada livro e escreve a prosa: o que os autores sustentam em comum, onde divergem, o que só um deles diz. A comparação e a conclusão são dela. Ela não busca.

**O juízo da versão anterior.** O sistema da versão anterior tem um juízo de suficiência: o nó E, uma chamada de LLM que decide, por livro, se o material responde à pergunta e se há retentativa. O juízo de suficiência passa a ser da IA editorial.

**A cadeia de consumidores.** O retriever entrega trechos com endereço e o rastro da busca. A IA editorial consome essa entrega, escreve a prosa e confere cada afirmação contra o material. O leitor, o espectador do vídeo, consome a prosa final e não confere nada. A garantia de que nada foi inventado para o espectador vem do elo entre a IA editorial e o retriever.

**A sinergia está na fronteira.** O que o retriever entrega precisa ser o que a IA editorial precisa para escrever sem inventar. O que ela escreve precisa poder ser conferido contra o material. Nenhuma das duas partes garante isso sozinha: o retriever pode devolver trechos corretos e incompletos, e a IA editorial pode escrever bem sobre material insuficiente.

**O formato é construído por iteração.** O formato de saída do retriever e a entrada da IA editorial não são definidos antes. Eles são criados via CRITIQUE, o modo de trabalho em que as partes planejam e discutem antes de executar, sem gastar nada até haver acordo. Nessa iteração, cada lado propõe, o outro consome e aponta o que falta ou sobra, até que a IA editorial consiga escrever e conferir sem precisar de nada além do que recebe. Essa iteração acontece já com este conceito em mãos.

**O que a checagem garante, e o que não garante.** O formato permite que a IA editorial confira que cada afirmação deriva de um trecho com endereço: a afirmação aponta para um campo, o campo aponta para um trecho, e o trecho existe no livro, verbatim. Essa parte é mecânica. Se o trecho sustenta o sentido da afirmação, isso é um julgamento da IA editorial, lendo o trecho. O formato não torna esse julgamento mecânico; precisa torná-lo visível e declarado como julgamento, e não apresentá-lo como verificação automática.

**Uma tensão que o projeto não resolve sozinho.** A IA editorial também é um modelo, e modelos tendem a concordar. A garantia de que nada foi inventado não vem de confiar nela, mas de o formato permitir a checagem.

## [Instrução] Modelo de entrada

A entrada do retriever é um bloco, com três partes: um identificador, uma tese e uma pergunta. Só a pergunta vai à busca. A tese orienta a IA editorial, que a usa para escrever e conferir a prosa. Como ela chega à IA editorial, passando pelo retriever, ainda não está decidido: o mecanismo de transporte faz parte do formato de saída, a ser decidido em conjunto com a IA editorial. Em uma nova rodada, o retriever recebe também o pedido da IA editorial. Um direcionamento estruturado não é uma consulta, e não vai à busca como texto.

O formato de escrita, as regras de tese e de pergunta e o formato de saída estão em `docs/brief_book_inquiries.md`, e esse documento é a referência para o modelo de entrada. Os itens dele marcados como em aberto (vocabulário por livro, perguntas compostas, termos de época e variações alternativas) não estão decididos e não devem ser tratados como regra antes do CRITIQUE com a IA editorial.

## [Instrução] Perguntas Importantes

As perguntas abaixo nasceram para orientar problemas reais. Vale perguntar, para cada uma, o que ela deixa de permitir à recuperação adaptativa, que é o centro do projeto.

**1. O alcance da busca deve ser medido contra trechos conhecidos de resposta?**
Se a medição exige o trecho conhecido, um trecho que responde à tese por outro caminho aparece como falha. Assim, a medição passa a premiar a volta do que já se conhece, e não a capacidade de a busca se ajustar ao vocabulário de cada livro. A pergunta é se essa é a régua certa, e não apenas uma régua possível.

**2. A consulta pode carregar as palavras que a resposta usa?**
A recuperação adaptativa aprende com o vocabulário do material, e as palavras da resposta são a informação mais forte que existe sobre onde ela está. Deixá-las de fora tira justamente o sinal que a adaptação precisa. Essa escolha não deve vir de uma regra de medição: em produção, ninguém sabe de antemão quais são essas palavras, e a decisão precisa valer sem isso.

**3. Um LLM não pode escrever evidência.**
A evidência é o trecho que a busca devolve do livro, e não do modelo.

**4. Quem escreve a consulta da nova rodada: o retriever, a IA editorial, ou nenhum dos dois?**
A pergunta está em aberto e será discutida em rodadas de CRITIQUE. A resposta define onde fica o LLM. Se o retriever escreve, ele precisa de um modelo; se a IA editorial escreve, a consulta vira parte do direcionamento; se nenhum dos dois escreve, a adaptação usa só as regras do retriever.

## A medição como beco sem saída

Esta seção descreve o que a medição produziu em uma versão anterior do projeto. Ali, a medição foi escolhida como caminho para decidir se a busca estava boa, e esse caminho engessou as alternativas: cada novo caminho para o mesmo objetivo precisava passar pela régua já existente, e a régua foi ficando cada vez mais difícil de deixar para trás.

A medição começou como um instrumento para dizer se a busca estava boa. Com o tempo, passou a definir o que
"boa" significa, e isso inverteu a relação entre ela e o produto. A produção deixou de ser projetada para responder
à pergunta da tese e passou a ser projetada para passar na medição.

O mecanismo é recorrente. Uma medição nova exige uma régua, a régua exige uma regra para não ser enganada, e a regra
exige um avaliador para decidir quando algo passou. Quando o avaliador de produção erra, cria-se uma medição para medi-lo, e
essa medição exige outro avaliador. Cada camada nova explica a anterior e não resolve nada da camada de baixo. É uma roda
de hamster: o esforço cresce, o movimento continua, e o sistema não sai do lugar.

O resultado prático é que a medição passou a ocupar o lugar da decisão de produto. Perguntas como "o que a busca
deve entregar?" e "quem decide que já há material suficiente?" foram respondidas por critérios de medição, sem que
ninguém tivesse decidido se esses critérios servem à tese. Quando a produção ficou impossível de justificar com
essas medições, a saída foi acrescentar mais uma camada, e não questionar a primeira.

Em consequência, o que o sistema faz em produção hoje depende de decisões tomadas para a medição, e não de uma
definição do que a recuperação deveria ser. Para o redesenho, isso significa que a medição não pode ser o ponto de
partida: ela só deve voltar depois que o problema de produção estiver definido em termos próprios.

## [Instrução] Pontos conceituais do projeto

1. **Definir a pergunta do editor antes de qualquer estrutura.** A pergunta do bloco vem do editor, quem escreve as teses. A unidade de saída do retriever (trecho, parágrafo, bloco) deve ser escolhida pelo que a IA editorial precisa receber para escrever e conferir a prosa, e não pelo que a busca faz.

2. **Mapa do que cada componente pode ver em produção.** Uma tabela com consulta, texto do livro, material recuperado, veredito e referência de acerto. Cada componente declara quais entradas usa. A referência de acerto aparece como algo que só o avaliador enxerga, e não se mistura com o que roda.

3. **Orçamento como contrato de entrada.** O limite de caracteres devolvidos é uma restrição da IA editorial, que lê o material, e deve ser declarado no início, com um responsável. Quando aparece tarde, corta material depois que a busca já decidiu. Onde esse limite é aplicado é uma decisão do formato de saída, a ser tomada com a IA editorial. O número de consultas de busca por bloco é outro limite, o da feature de parada, e não se confunde com esse.

4. **Glossário próprio.** Cada termo do vocabulário do projeto tem uma definição escrita no próprio repositório, a partir das decisões dele. Termos de versões anteriores só entram se forem decididos de novo; nenhum termo carrega um sentido herdado sem ser redefinido.

5. **Premissa escrita junto de cada decisão.** Cada decisão registra o que a tornou necessária e o que a invalidaria. A ausência desse registro é a raiz do problema, então ele precisa existir desde o início, e não ser reconstruído depois.

6. **Quais bibliotecas deixam de ser padrão.** Para cada biblioteca usada, escrever o que o projeto faria sem ela. Se a resposta for "algo mais simples e igualmente correto", a biblioteca está sendo usada por hábito. Se for "não consigo", a dependência é real e precisa ser registrada, junto com o desenho que ela impõe.

## [Instrução] Regras de processo a migrar

- **Modo CRITIQUE:** descrito em `modo_critique.md`, a copiar para `docs/` do novo repositório. Migrar o método, sem os critérios e os números que ele produziu.
- **Compartilhamento de memória entre ferramentas:** um escritor por arquivo, quando mais de uma ferramenta usa a mesma memória. Decidir se o novo repositório precisa disso antes de migrar.
- **Orçamento antes de gasto:** qualquer execução que gaste chamadas de API precisa de estimativa e aprovação antes, com reconciliação depois.
- **Redesenho por causa:** agrupar os problemas por causa, ordenar pelo fluxo, tratar um item por vez, com critérios checáveis sem modelo. Migrar o método, sem os critérios que ele produziu.

## [Instrução] Formato de saída e IA editorial

O formato de saída do retriever será lido por uma IA editorial, que transformará o material devolvido em prosa. Portanto, o formato deve ser acordado com essa IA editorial, via CRITIQUE. Esse formato é discutido já com o conceito do projeto como um todo em mãos, e não antes. A definição final do formato de saída do retriever e da entrada da IA editorial será decidida em conjunto, via CRITIQUE. Até lá, nenhum documento deve afirmar o que o retriever entrega ou o que a IA editorial recebe além do que está registrado aqui.

## [Instrução] Premissas do desenho em grafos separados

O desenho com dois grafos, um para a busca e outro para a IA editorial, parte destas premissas:

1. **Cada parte faz o que faz melhor.** O retriever executa a busca por regras, de forma determinística. A IA editorial julga o sentido, escreve e decide pedir nova rodada.
2. **Um único grafo misturava a busca, o juízo e a composição, e cada parte mudava a outra.** Uma mudança na forma dos trechos alterava o que o juízo via, e uma mudança no juízo alterava a busca que seguia.
3. **A adaptação dentro da busca não depende de julgamento.** Variações, vocabulário do livro, cobertura de regiões e parada são decisões do retriever, tomadas com as entradas da própria chamada.
4. **A adaptação entre rodadas depende da IA editorial, e é explícita.** Só ela decide que o material não basta, e isso chega ao retriever por um pedido com conteúdo declarado.
5. **Repetibilidade e cache exigem que a busca dependa só de entradas declaradas.** Por isso o retriever não guarda estado entre chamadas: o que ele precisa da rodada anterior vem no pedido.
6. **A fronteira é um contrato escrito.** Entram o bloco, a pergunta, o direcionamento e o rastro anterior; saem os trechos e o rastro.
7. **Não há um segundo juiz.** O julgamento de sentido fica com a IA editorial, e as ferramentas que ela usa para isso fazem parte do papel dela, não formam um segundo juízo.
8. **O grafo da IA editorial entra no repositório novo.** Os dois grafos ficam juntos, cada um com responsabilidade própria.

## [Instrução] A IA editorial como grafo

A IA editorial é um grafo próprio, e entra no repositório novo. Ela recebe os trechos e a tese, julga se o material basta, e então escreve a prosa e a confere contra os trechos, ou pede uma nova rodada com um direcionamento. O julgamento de sentido é dela.

## [Instrução] Pedido de nova rodada

Uma nova rodada é um pedido da IA editorial ao retriever, com o bloco, a pergunta, o direcionamento e o rastro das rodadas anteriores. O direcionamento começa com formato estruturado, e não texto livre: texto livre obrigaria um modelo de linguagem dentro do retriever. O formato final é decidido em CRITIQUE.

## [Sugestão] Features para a recuperação adaptativa

Sugestões, não decisões. Todas se aplicam a um livro por execução.

1. **Consultas derivadas só da tese, em varredura.** Um conjunto fixo de N consultas, geradas por regra sobre a própria tese. Não depende do que voltou, então não reforça a região já achada.

2. **Vocabulário do próprio livro, construído na ingestão.** Um índice de termos e coocorrências por livro, versionado com a ingestão. Serve de fonte de vocabulário que não depende da primeira passada.

3. **Escolha da próxima consulta por cobertura de regiões.** Com endereços posicionais, é possível medir quais regiões do livro já foram visitadas e priorizar as que não foram. A adaptação passa a considerar cobertura, além de relevância.

4. **Decomposição da pergunta em cláusulas, por regra.** Dividir a pergunta em partes (por pontuação ou por termos) e consultar cada parte. É determinística e não exige modelo, mas não sabe se as partes da pergunta cobrem as partes da tese.

5. **Canal de busca denso como base, léxico como consulta separada.** Cada canal de busca devolve seu próprio ranking, e a fusão é uma decisão declarada, não o padrão da biblioteca. "Denso" descreve a família de recuperação por representação vetorial (embeddings): consulta e trechos são transformados em vetores e ranqueados pela proximidade de sentido. A alternativa de outra família é a recuperação esparsa, por contagem de termos, como o BM25. A escolha do modelo de embedding é uma decisão separada.

6. **Parada definida antes da execução.** Cada bloco tem um número máximo de consultas à busca, fixado antes da execução. A busca para quando esse número se esgota ou quando não restam regiões do livro a visitar, o que vier primeiro. O limite de caracteres devolvidos é outra restrição, de outro responsável (a IA editorial), e seu ponto de aplicação é uma decisão do formato de saída. Nenhum juízo decide a parada.

7. **Rastro estruturado por consulta.** Texto da consulta, canal de busca, posição de cada trecho devolvido, região visitada e motivo da parada. É o que permite distinguir "o livro não trata disso" de "a busca não tentou essa forma".

8. **Cache por (livro, consulta, versão da ingestão, versão do código de recuperação, configuração da busca e modelo de embedding).** Mesma chave, mesmo resultado.

9. **Variações da consulta geradas por modelo (multi-query).** Um LLM propõe algumas variações da consulta, a busca roda com cada uma, e os resultados são unidos. Depende da pergunta 4: se essa pergunta não for respondida a favor do modelo, esta feature não entra. Quando entrar, cada variação precisa aparecer no rastro, com a indicação de que foi gerada por modelo.

## [Sugestão] Varredura inicial do corpus

Uma passada sobre o texto de cada livro, antes de qualquer consulta, que produz uma estrutura descritiva por livro: vocabulário e posições, sem julgamento e sem pergunta. Ela descreve o texto e não diz o que o livro não trata; uma afirmação de ausência continua dependendo de busca e do rastro. Fica por livro, versionada pela ingestão, e alimenta as features 2 e 3.

## [Sugestão] Bibliotecas para a parte adaptativa

Nomes e funções não verificados em versões atuais. Mapeamento para as features acima.

| feature | bibliotecas | o que resolvem |
|---|---|---|
| 1. vocabulário do livro | `gensim` (word2vec ou fastText, treinados no próprio livro), `spaCy` (lemas e substantivos), `YAKE` ou `KeyBERT` (palavras-chave) | vizinhos de termos e termos característicos, calculados a partir do texto, sem depender da primeira passada |
| 2. cobertura de regiões | nenhuma pronta; `max_marginal_relevance_search` do LangChain, com o Chroma, dá diversidade, mas não cobertura posicional | a cobertura por endereço precisa ser implementada, porque nenhuma biblioteca conhece a posição no livro |
| 3. decomposição da tese | `spaCy` (análise de dependências e chunks nominais) | divisão em cláusulas por estrutura gramatical, sem modelo generativo |
| 4. denso e léxico | `chromadb` e `rank-bm25`, já no projeto; a fusão é uma função de poucas linhas | os dois rankings separados, e a fusão declarada no código |
| 5. rastro | `pydantic` (já no projeto) para o esquema | o esquema importa; a biblioteca só serializa |
| 6. cache | `joblib` (`Memory`) ou `diskcache` | cache com chave que inclui a versão da ingestão, a versão do código de recuperação, a configuração da busca e o modelo de embedding |

Referência opcional: `pyserini` (com Anserini) tem RM3 e Rocchio como implementações de referência, úteis para comparação. Exige Java.

As bibliotecas de vocabulário trazem valores padrão (dimensões do word2vec, janela de coocorrência, limite de palavras-chave) que precisam ser escolhidos e registrados, não herdados.

## [Instrução] Memória de ingestão a migrar (epub)

O carregador de epub foi entregue como código de primeira passagem, de propósito, para ser revisto depois. Ele não foi pensado como definitivo, e os pontos abaixo são as arestas conhecidas que essa revisão precisa tratar. Não são regressões.

- Arquivos de epub sem entrada no sumário recebem o nome do arquivo como título do capítulo, e isso produz documentos minúsculos de front matter (por exemplo, um arquivo com um único caractere).
- Várias entradas do sumário apontando para um mesmo arquivo mantêm só o primeiro título.
- Um capítulo dividido em vários arquivos vira vários documentos.
- Parágrafos aninhados (`<li><p>`) podem duplicar texto.
- O despacho é só pela extensão, sem verificação do conteúdo.

**Por que importa:** a ingestão precisa produzir os parágrafos com endereço posicional e capítulo. Qualquer uma dessas arestas altera os endereços e os textos que chegam à recuperação.

## [Instrução] Instruções para a ingestão

**Objetivo.** Transformar cada arquivo de livro em epub em uma lista de parágrafos com endereço posicional, sem julgamento e sem depender de nenhuma pergunta.

**Entrada.** Um arquivo por livro, com a edição registrada (título, tradutor, ano e fonte do arquivo). A edição faz parte do identificador da ingestão.

**Saída.** Para cada parágrafo: o índice posicional no livro, o capítulo e a posição dentro dele, o texto como aparece na edição, a marcação de citação quando o autor cita outro e a fonte impressa, se houver. O índice posicional é atribuído uma única vez, na ingestão. Nenhum outro componente cria endereços.

**Identificador da versão.** Um identificador derivado da entrada (arquivo, edição, versão do código de ingestão). Todo artefato gerado a partir dos parágrafos carrega esse identificador, e a comparação entre artefatos é recusada quando ele não bate.

**Testes exigidos, um por aresta conhecida:**
- arquivo sem entrada no sumário, ou de front matter: nenhum documento minúsculo de front matter. O arquivo não gera capítulo nem endereço: é classificado como aparato no manifesto do livro (estrutural, ou de outro autor) e listado no relatório de ingestão. Arquivo não classificado interrompe a execução. (Emendado em CRITIQUE, decisão M1.)
- várias entradas do sumário apontando para o mesmo arquivo: cada título preservado;
- capítulo dividido em vários arquivos: um só capítulo na saída, com a ordem preservada;
- parágrafo aninhado (`<li><p>`): nenhuma duplicação de texto;
- arquivo com extensão errada: detectado pelo conteúdo, não só pela extensão;
- quebras de linha internas ao parágrafo: o texto final não tem quebras artificiais no meio de frases.

**Proibições.**
- nenhum juízo sobre o texto, nenhuma pergunta, nenhuma seleção de parágrafos nesta etapa. A classificação de um arquivo é um juízo do manifesto, declarado no relatório.

**Critério de pronto.** Os testes passam com os arquivos de entrada reais, e rodar a ingestão duas vezes gera a mesma saída, com o mesmo identificador de versão.
