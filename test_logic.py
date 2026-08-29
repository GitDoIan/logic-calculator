"""Testes rápidos (sem framework) do parser simbólico, da tabela-verdade e do parser de linguagem natural."""

from logic_parser import parse_formula, generate_truth_table
from nl_parser import NaturalLanguageParser


def check(desc, condition):
    status = "OK " if condition else "FALHOU"
    print(f"[{status}] {desc}")
    if not condition:
        raise SystemExit(1)


def test_symbolic_and_text_equivalence():
    root1, vars1 = parse_formula("p AND q")
    root2, vars2 = parse_formula("p ∧ q")
    check("texto e símbolo geram a mesma fórmula (AND)", str(root1) == str(root2) == "p ∧ q")


def test_portuguese_keywords():
    root, _ = parse_formula("nao p ou q")
    check("palavras em português (nao/ou)", str(root) == "¬p ∨ q")


def test_precedence():
    root, _ = parse_formula("p ∨ q ∧ r")
    check("∧ tem precedência maior que ∨", str(root) == "p ∨ (q ∧ r)")


def test_implication_and_iff():
    root, variables = parse_formula("p -> q")
    headers, rows, classification = generate_truth_table(root, variables)
    check("cabeçalhos incluem variáveis e fórmula", headers == ["p", "q", "p → q"])
    # p=V,q=V -> V ; p=V,q=F -> F ; p=F,q=V -> V ; p=F,q=F -> V
    expected = [True, False, True, True]
    got = [row[-1] for row in rows]
    check("tabela-verdade de p → q está correta", got == expected)


def test_tautology_and_contradiction():
    root, variables = parse_formula("p ∨ ¬p")
    _, _, classification = generate_truth_table(root, variables)
    check("p ∨ ¬p é tautologia", classification.startswith("Tautologia"))

    root, variables = parse_formula("p ∧ ¬p")
    _, _, classification = generate_truth_table(root, variables)
    check("p ∧ ¬p é contradição", classification.startswith("Contradição"))


def test_parse_errors():
    try:
        parse_formula("p ∧")
        check("erro esperado em fórmula incompleta", False)
    except Exception:
        check("erro esperado em fórmula incompleta", True)

    try:
        parse_formula("(p ∧ q")
        check("erro esperado em parêntese não fechado", False)
    except Exception:
        check("erro esperado em parêntese não fechado", True)


def test_natural_language():
    parser = NaturalLanguageParser()
    formula, legend = parser.parse("se chove então a rua molha")
    check("condicional em PT-BR", formula == "(P1 → P2)")
    check("legenda da condicional", legend == {"P1": "chove", "P2": "a rua molha"})

    root, variables = parse_formula(formula)
    headers, rows, classification = generate_truth_table(root, variables)
    check("fórmula convertida de NL é válida e calculável", classification.startswith("Contingência"))

    parser = NaturalLanguageParser()
    formula, legend = parser.parse("nao chove")
    check("negação em PT-BR", formula == "¬P1")

    parser = NaturalLanguageParser()
    formula, legend = parser.parse("chove e neva")
    check("conjunção em PT-BR", formula == "(P1 ∧ P2)")

    parser = NaturalLanguageParser()
    formula, legend = parser.parse("chove ou neva")
    check("disjunção em PT-BR", formula == "(P1 ∨ P2)")

    parser = NaturalLanguageParser()
    formula, legend = parser.parse("a luz acende se e somente se o interruptor esta ligado")
    check("bicondicional em PT-BR", formula == "(P1 ↔ P2)")


if __name__ == "__main__":
    test_symbolic_and_text_equivalence()
    test_portuguese_keywords()
    test_precedence()
    test_implication_and_iff()
    test_tautology_and_contradiction()
    test_parse_errors()
    test_natural_language()
    print("\nTodos os testes passaram.")
