"""Interpretação de frases em português para fórmulas de lógica proposicional.

Abordagem baseada em regras (sem IA/API externa, offline, sem custo). Reconhece:
  - "X se e somente se Y"      -> X ↔ Y
  - "se X então Y" / "se X, Y" -> X → Y
  - "X ou Y"                   -> X ∨ Y
  - "X e Y"                    -> X ∧ Y
  - "não X" / "nao X"          -> ¬X
Trechos que não casam com nenhum padrão viram proposições atômicas (P1, P2, ...),
registradas numa legenda para o usuário conferir o que cada uma significa.
"""

import re


class NLParseError(Exception):
    pass


class NaturalLanguageParser:
    def parse(self, text):
        self.counter = 1
        self.legend = {}
        formula = self._parse_clause(text)
        if not self.legend:
            raise NLParseError("Não consegui identificar nenhuma proposição na frase.")
        return formula, self.legend

    def _make_var(self, clause):
        clause = clause.strip().strip(".").strip()
        if not clause:
            raise NLParseError(
                "Frase incompleta: parece faltar o texto de uma proposição "
                "(confira se não ficou nada em branco depois de 'e', 'ou', 'se' etc.)."
            )
        label = f"P{self.counter}"
        self.counter += 1
        self.legend[label] = clause
        return label

    def _parse_clause(self, text):
        text = text.strip()
        if not text:
            raise NLParseError("Frase incompleta.")

        m = re.search(r"\bse\s+e\s+somente\s+se\b", text, re.IGNORECASE)
        if m:
            left, right = text[:m.start()], text[m.end():]
            return f"({self._parse_clause(left)} ↔ {self._parse_clause(right)})"

        m = re.match(r"^\s*se\s+(.*?)\s*,?\s*ent[aã]o\s+(.*)$", text, re.IGNORECASE)
        if m:
            return f"({self._parse_clause(m.group(1))} → {self._parse_clause(m.group(2))})"

        parts = re.split(r"\bou\b", text, flags=re.IGNORECASE)
        if len(parts) > 1:
            return "(" + " ∨ ".join(self._parse_clause(p) for p in parts) + ")"

        parts = re.split(r"\be\b", text, flags=re.IGNORECASE)
        if len(parts) > 1:
            return "(" + " ∧ ".join(self._parse_clause(p) for p in parts) + ")"

        m = re.match(r"^\s*n[aã]o\s+(.*)$", text, re.IGNORECASE)
        if m:
            return f"¬{self._parse_clause(m.group(1))}"

        return self._make_var(text)
