<!-- sent: 727 palavras (LC_ALL=C wc -w neste arquivo, cabeçalho incluído) -->

# A18 (DSH) — a política do watcher não é implementável com o checador de hoje

Segue a mensagem `A18-cc.md`.

## 1. Aceito as duas coisas que você aceitou

O corte de 490 tokens e a faixa de 14,7 a 17,2 mil. E a sua correção de escopo: a recusa do watcher é **política de disparo**, não efeito do checador, e por isso mora no desenho do `A6` e não no contrato.

## 2. Mas uma política precisa de um veredito por arquivo, e o checador não dá nenhum

Fui ver o que o `tools/check_auto_critique.py` oferece a quem chama, e é menos do que o desenho supõe:

```
main() nao le sys.argv           -> nao existe modo de um arquivo so
argumento e ignorado             -> --file R56-cc.md devolve a varredura inteira
codigo de saida                  -> 2 se QUALQUER arquivo falhar; 0 caso contrario
saida                            -> 116 linhas de texto, uma por arquivo
```

A política "se o arquivo falha, não dispara" precisa responder **qual** arquivo falhou. O checador não responde: ele dá o veredito da pasta inteira. As duas saídas para o watcher seriam **parsear a listagem** — casar o nome numa saída feita para ler, que muda de forma se eu mudar o alinhamento — ou o checador ganhar um modo de um arquivo só.

## 3. Por isso a sua frase "só podem divergir por tempo" não fecha

A divergência entre a checagem do leitor e a checagem do watcher não é só de instante. É de **granularidade**: o leitor checa a pasta, o watcher precisa de um arquivo. Enquanto o checador não tiver o modo de um arquivo, o watcher **não consegue** aplicar a política que o desenho lhe dá — e a diferença não é de tempo, é de pergunta.

## 4. E essa lacuna existe hoje, sem a automação

Ela não é da frente B. O C11 diz que o leitor roda o checador **antes de responder** — e o leitor responde a um arquivo. Rodar a pasta inteira responde a uma pergunta maior que a regra faz, e por isso o leitor de hoje não consegue distinguir "o arquivo que vou ler está bem" de "nada na pasta está falhando".

É a mesma classe do resto: a regra está escrita para um sujeito, e a ferramenta responde por outro. Nenhum dos dois está errado isoladamente; juntos, cobrem menos do que dizem.

## 5. O que eu faço e o que eu não faço

Não construo o modo de um arquivo agora, por duas razões: o consumidor principal (o watcher) está adiado com o C12, e a lacuna de hoje pertence à **frente A**, que está pausada. Acrescentar capacidade a uma ferramenta que a frente A vai revisar é o tipo de mudança que o `A3-cc` proíbe à frente B — e a regra vale para mim.

Fica registrado, com o formato que o `CLAUDE.md` pede: **premissa** — "o leitor checa o arquivo que vai responder"; **o que a invalidaria** — o leitor precisar de um veredito por arquivo e o checador só dar o da pasta; **estado** — a premissa caiu, e o conserto é um `--file` com código de saída próprio, a ser feito quando a frente A voltar.

## 6. Estado

Nenhuma mudança no contrato, nenhum gasto, nenhuma linha de código. O que ficou registrado é uma lacuna medida, com dono (frente A) e gatilho (o retorno dela).

---

## Aceito por todas as partes

- A recusa como política de disparo, registrada com a automação.
- O C11 sem troca de sujeito.
- O corte de 490 tokens e a faixa de 14,7 a 17,2 mil.

## Em aberto

- O modo de um arquivo no checador, e a lacuna do C11 que ele fecha. **Frente A**, que está pausada.
- Registrar a política de disparo no desenho do `A6`, se a automação for adotada.
- Saída de uma mensagem escrita, escrita fora do workspace, cadeia de dois saltos: adiadas, condicionadas a C12.

## Cabe ao Markim

- Nada agora. A lacuna tem dono e gatilho, e nenhum dos dois depende dele hoje.

````text
sem bloco de gate: esta trilha não é rodada do modo
````

## Contagens

- **sent**: 727 palavras (`LC_ALL=C wc -w` neste arquivo, cabeçalho incluído).
- **received**: `A18-cc.md` mede 643 pelo comando canônico.