# Calculadora Lógica

Calculadora de lógica proposicional com interface gráfica, que aceita fórmulas
em notação simbólica, em texto, ou frases em português, e gera a tabela-verdade
completa.

## 1. O que o app faz

Você fornece uma expressão lógica — digitando símbolos, digitando texto, usando
os botões da calculadora, ou escrevendo uma frase em português — e o app:

1. Interpreta essa expressão e monta uma fórmula lógica formal.
2. Calcula o valor da fórmula para **todas as combinações possíveis** de
   verdadeiro/falso das variáveis envolvidas.
3. Mostra o resultado numa tabela-verdade, com uma coluna para cada variável,
   uma coluna para cada subexpressão (passo a passo do cálculo) e a coluna
   final com o resultado da fórmula completa.
4. Classifica a fórmula como **Tautologia** (sempre verdadeira), **Contradição**
   (sempre falsa) ou **Contingência** (depende dos valores das variáveis).

## 2. Estrutura dos arquivos

| Arquivo | Responsabilidade |
|---|---|
| `logic_parser.py` | Tokenizador, parser e avaliador de fórmulas lógicas; gerador da tabela-verdade. |
| `nl_parser.py` | Interpretação de frases em português (baseada em regras, sem IA/API externa). |
| `gui.py` | Interface gráfica (Tkinter). |
| `main.py` | Ponto de entrada — só chama a interface gráfica. |
| `test_logic.py` | Testes automatizados do parser e da tabela-verdade. |
| `build.sh` | Script que empacota tudo num executável único (`.app`). |

## 3. Como a fórmula lógica é interpretada

### 3.1 Operadores aceitos

A calculadora aceita cada operador em três formas equivalentes: **símbolo**,
**palavra em inglês** e **palavra em português**. Você pode misturar as formas
na mesma fórmula.

| Operador | Significado | Símbolos aceitos | Texto aceito |
|---|---|---|---|
| Negação | "não X" | `¬` `!` `~` | `NOT`, `NAO`, `não` |
| Conjunção | "X e Y" | `∧` `&` `*` | `AND`, `e` |
| Disjunção | "X ou Y" | `∨` `\|` `+` | `OR`, `ou` |
| Condicional | "se X então Y" | `→` `->` | `IMPLICA` |
| Bicondicional | "X se e somente se Y" | `↔` `<->` | `SSE`, `IFF` |
| Agrupamento | — | `(` `)` | — |

As variáveis podem ser qualquer letra ou palavra que não seja um desses
operadores (ex.: `p`, `q`, `chove`, `alarme`).

### 3.2 Ordem de precedência (do mais forte para o mais fraco)

```
¬  (negação)
∧  (e)
∨  (ou)
→  (se...então)
↔  (se e somente se)
```

Isso significa que `p ∨ q ∧ r` é interpretado como `p ∨ (q ∧ r)` — igual à
convenção matemática de que multiplicação "vem antes" da soma. Use parênteses
sempre que quiser forçar uma ordem diferente, por exemplo `(p ∨ q) ∧ r`.

### 3.3 Como o parser funciona, por dentro

1. **Tokenização**: o texto é varrido caractere a caractere e quebrado em uma
   lista de tokens (`NOT`, `AND`, `OR`, `IMPLIES`, `IFF`, `LPAREN`, `RPAREN`,
   `VAR`). Símbolos multi-caractere como `<->` e `->` são reconhecidos antes de
   símbolos de um caractere só, e palavras (`and`, `nao`, `sse`...) são
   comparadas sem acento e sem diferenciar maiúsculas/minúsculas.
2. **Parsing (análise sintática)**: um parser recursivo de descida (*recursive
   descent parser*) percorre os tokens respeitando a ordem de precedência da
   seção 3.2, montando uma árvore sintática (AST) onde cada nó é uma variável,
   uma negação, ou uma operação binária com um lado esquerdo e um lado direito.
3. **Avaliação**: para calcular o valor de verdade da fórmula dado um conjunto
   de valores das variáveis, o avaliador percorre essa árvore recursivamente —
   cada tipo de nó sabe como se avaliar a partir do valor dos seus filhos.

## 4. Como a linguagem natural é interpretada

**Importante: não usa IA/modelo de linguagem.** É um interpretador baseado em
regras (expressões regulares), 100% offline, sem custo e sem depender de
internet ou de uma API key. Isso foi uma escolha deliberada para manter o app
simples e gratuito — a limitação é que ele só reconhece os padrões de frase
abaixo, não qualquer frase livre.

Padrões reconhecidos, verificados nesta ordem:

1. `"X se e somente se Y"` → bicondicional
2. `"se X então Y"` (ou `"se X, Y"`, precisa começar a frase com "se") → condicional
3. `"X, senão Y"` / `"X, se não, Y"` → `¬X → Y` ("Y só acontece se X não acontecer")
4. `"X, então Y"` / `"X, portanto Y"` (então/portanto **no meio** da frase, sem precisar de "se" no começo) → condicional
5. `"X ou Y"` → disjunção
6. `"X e Y"` → conjunção
7. `"não X"` / `"nao X"` (só no começo da frase) → negação
8. Qualquer trecho que sobrar depois dessas checagens vira uma **proposição
   atômica**, recebendo automaticamente um rótulo `P1`, `P2`, `P3`... Esses
   rótulos e o texto original de cada um aparecem numa legenda na tela, para
   você conferir o que o app entendeu.

Exemplo: a frase `"se chove então a rua molha"` vira a fórmula `(P1 → P2)`,
com a legenda `P1: chove` e `P2: a rua molha`.

**Limitação conhecida do "senão"**: a regra trata TUDO que veio antes do
"senão"/"se não" como o antecedente que está sendo negado. Em frases curtas de
duas partes isso funciona muito bem (`"estudo, senão reprovo"` → `¬P1 → P2`).
Em frases longas com vários conectores encadeados, o antecedente vira a frase
inteira anterior — o que é uma leitura mecanicamente consistente, mas pode não
bater com a intenção mais "natural" de quem escreveu. Pra resultados mais
previsíveis, prefira frases mais curtas e diretas.

Frases mais complexas são resolvidas recursivamente: por exemplo, `"se chove e
está frio então a rua molha ou congela"` primeiro identifica a estrutura
condicional (`se ... então ...`), e depois processa cada metade separadamente,
encontrando o `"e"` na primeira parte e o `"ou"` na segunda.

## 5. A tabela-verdade

Para uma fórmula com `n` variáveis, existem `2^n` combinações possíveis de
verdadeiro/falso — o app gera uma linha para cada uma. Além das colunas das
variáveis, cada subexpressão da fórmula (cada operação, na ordem em que
aparece) vira uma coluna própria, para você acompanhar o cálculo passo a
passo até chegar na coluna final.

- **V** = verdadeiro
- **F** = falso

Depois de montar todas as linhas, o app olha só para a última coluna
(o resultado da fórmula completa):

- Se todas as linhas são **V** → **Tautologia**.
- Se todas as linhas são **F** → **Contradição**.
- Caso contrário → **Contingência**.

## 6. Usando a interface

A janela tem duas abas:

- **Fórmula Lógica**: campo de texto + botões de calculadora. Os botões `p` a
  `y` inserem variáveis, os botões de operador (`¬ ∧ ∨ → ↔`) inserem o símbolo
  na posição do cursor, `⌫` apaga o último caractere e `Limpar` esvazia o
  campo. O botão `Calcular` processa a fórmula.
- **Linguagem Natural**: caixa de texto para escrever uma frase em português.
  O botão `Converter e Calcular` interpreta a frase, mostra a legenda das
  proposições identificadas, e já calcula a tabela-verdade.

Abaixo das abas aparecem, sempre: a fórmula final interpretada, a
classificação (Tautologia/Contradição/Contingência, com uma cor diferente
para cada uma) e a tabela-verdade completa.

## 7. Rodando o projeto

**Modo desenvolvimento** (precisa de Python 3 instalado):

```bash
cd ~/logic-calculator
python3 main.py
```

**Rodando os testes automatizados:**

```bash
cd ~/logic-calculator
python3 test_logic.py
```

**Gerando o executável único** (não precisa de Python na máquina de destino):

```bash
cd ~/logic-calculator
./build.sh
```

O executável fica em `dist/CalculadoraLogica.app` (macOS).
