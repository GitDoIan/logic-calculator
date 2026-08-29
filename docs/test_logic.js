/* Testes do porte JS, espelhando test_logic.py, rodados via Node. */
const { parseFormula, generateTruthTable } = require("./logic.js");
const { NaturalLanguageParser } = require("./nl_parser.js");

function check(desc, condition) {
  const status = condition ? "OK " : "FALHOU";
  console.log(`[${status}] ${desc}`);
  if (!condition) process.exit(1);
}

{
  const { root: root1 } = parseFormula("p AND q");
  const { root: root2 } = parseFormula("p ∧ q");
  check("texto e símbolo geram a mesma fórmula (AND)", String(root1) === String(root2) && String(root1) === "p ∧ q");
}

{
  const { root } = parseFormula("nao p ou q");
  check("palavras em português (nao/ou)", String(root) === "¬p ∨ q");
}

{
  const { root } = parseFormula("p ∨ q ∧ r");
  check("∧ tem precedência maior que ∨", String(root) === "p ∨ (q ∧ r)");
}

{
  const { root, variables } = parseFormula("p -> q");
  const { headers, rows } = generateTruthTable(root, variables);
  check("cabeçalhos incluem variáveis e fórmula", JSON.stringify(headers) === JSON.stringify(["p", "q", "p → q"]));
  const expected = [true, false, true, true];
  const got = rows.map((r) => r[r.length - 1]);
  check("tabela-verdade de p → q está correta", JSON.stringify(got) === JSON.stringify(expected));
}

{
  const { root, variables } = parseFormula("p ∨ ¬p");
  const { classification } = generateTruthTable(root, variables);
  check("p ∨ ¬p é tautologia", classification.startsWith("Tautologia"));
}

{
  const { root, variables } = parseFormula("p ∧ ¬p");
  const { classification } = generateTruthTable(root, variables);
  check("p ∧ ¬p é contradição", classification.startsWith("Contradição"));
}

{
  let threw = false;
  try { parseFormula("p ∧"); } catch (e) { threw = true; }
  check("erro esperado em fórmula incompleta", threw);
}

{
  let threw = false;
  try { parseFormula("(p ∧ q"); } catch (e) { threw = true; }
  check("erro esperado em parêntese não fechado", threw);
}

{
  const { formula, legend } = new NaturalLanguageParser().parse("se chove então a rua molha");
  check("condicional em PT-BR", formula === "(P1 → P2)");
  check("legenda da condicional", JSON.stringify(legend) === JSON.stringify({ P1: "chove", P2: "a rua molha" }));
  const { root, variables } = parseFormula(formula);
  const { classification } = generateTruthTable(root, variables);
  check("fórmula convertida de NL é válida e calculável", classification.startsWith("Contingência"));
}

{
  const { formula } = new NaturalLanguageParser().parse("nao chove");
  check("negação em PT-BR", formula === "¬P1");
}

{
  const { formula } = new NaturalLanguageParser().parse("chove e neva");
  check("conjunção em PT-BR", formula === "(P1 ∧ P2)");
}

{
  const { formula } = new NaturalLanguageParser().parse("chove ou neva");
  check("disjunção em PT-BR", formula === "(P1 ∨ P2)");
}

{
  const { formula } = new NaturalLanguageParser().parse("a luz acende se e somente se o interruptor esta ligado");
  check("bicondicional em PT-BR", formula === "(P1 ↔ P2)");
}

{
  const { formula } = new NaturalLanguageParser().parse("eu estudo, senão eu reprovo");
  check("senão em PT-BR", formula === "(¬(P1) → P2)");
}

{
  const { formula } = new NaturalLanguageParser().parse("eu estudo, se não, eu reprovo");
  check("se não (duas palavras) em PT-BR", formula === "(¬(P1) → P2)");
}

{
  const { formula } = new NaturalLanguageParser().parse("eu suei muito, portanto vou tomar banho");
  check("portanto no meio da frase", formula === "(P1 → P2)");
}

{
  const { formula } = new NaturalLanguageParser().parse("eu joguei bola, então estou cansado");
  check("então no meio da frase (sem 'se')", formula === "(P1 → P2)");
}

console.log("\nTodos os testes passaram.");
