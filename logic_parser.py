"""Tokenizer, parser, avaliador e gerador de tabela-verdade para fórmulas de lógica proposicional.

Aceita notação simbólica (¬ ∧ ∨ → ↔) e equivalentes em texto (NOT/AND/OR, NÃO/E/OU, ! & | -> <->).
"""

import itertools
import unicodedata


class ParseError(Exception):
    pass


# ---------------------------------------------------------------------------
# AST
# ---------------------------------------------------------------------------

class Var:
    def __init__(self, name):
        self.name = name

    def eval(self, env):
        return env[self.name]

    def __str__(self):
        return self.name


class Not:
    def __init__(self, operand):
        self.operand = operand

    def eval(self, env):
        return not self.operand.eval(env)

    def __str__(self):
        s = str(self.operand)
        if isinstance(self.operand, (And, Or, Implies, Iff)):
            return f"¬({s})"
        return f"¬{s}"


def _wrap(node):
    s = str(node)
    if isinstance(node, (And, Or, Implies, Iff)):
        return f"({s})"
    return s


class And:
    def __init__(self, left, right):
        self.left, self.right = left, right

    def eval(self, env):
        return self.left.eval(env) and self.right.eval(env)

    def __str__(self):
        return f"{_wrap(self.left)} ∧ {_wrap(self.right)}"


class Or:
    def __init__(self, left, right):
        self.left, self.right = left, right

    def eval(self, env):
        return self.left.eval(env) or self.right.eval(env)

    def __str__(self):
        return f"{_wrap(self.left)} ∨ {_wrap(self.right)}"


class Implies:
    def __init__(self, left, right):
        self.left, self.right = left, right

    def eval(self, env):
        return (not self.left.eval(env)) or self.right.eval(env)

    def __str__(self):
        return f"{_wrap(self.left)} → {_wrap(self.right)}"


class Iff:
    def __init__(self, left, right):
        self.left, self.right = left, right

    def eval(self, env):
        return self.left.eval(env) == self.right.eval(env)

    def __str__(self):
        return f"{_wrap(self.left)} ↔ {_wrap(self.right)}"


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

SYMBOL_MAP = {
    "<->": "IFF", "->": "IMPLIES",
    "¬": "NOT", "~": "NOT", "!": "NOT",
    "∧": "AND", "&": "AND", "*": "AND",
    "∨": "OR", "|": "OR", "+": "OR",
    "↔": "IFF", "→": "IMPLIES",
    "(": "LPAREN", ")": "RPAREN",
}
_SYMBOLS_SORTED = sorted(SYMBOL_MAP.keys(), key=len, reverse=True)

WORD_KEYWORDS = {
    "not": "NOT", "nao": "NOT",
    "and": "AND", "e": "AND",
    "or": "OR", "ou": "OR",
    "implica": "IMPLIES",
    "sse": "IFF", "iff": "IFF",
}


def _strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _is_word_char(ch, first=False):
    if ch == "_":
        return True
    if ch.isalpha():
        return True
    if not first and ch.isdigit():
        return True
    return False


def tokenize(text):
    tokens = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue

        matched_symbol = None
        for sym in _SYMBOLS_SORTED:
            if text.startswith(sym, i):
                matched_symbol = sym
                break
        if matched_symbol:
            tokens.append((SYMBOL_MAP[matched_symbol], matched_symbol, i))
            i += len(matched_symbol)
            continue

        if _is_word_char(ch, first=True):
            j = i + 1
            while j < n and _is_word_char(text[j]):
                j += 1
            word = text[i:j]
            key = _strip_accents(word).lower()
            if key in WORD_KEYWORDS:
                tokens.append((WORD_KEYWORDS[key], word, i))
            else:
                tokens.append(("VAR", word, i))
            i = j
            continue

        raise ParseError(f"Caractere não reconhecido: '{ch}' na posição {i + 1}")

    tokens.append(("EOF", "", n))
    return tokens


# ---------------------------------------------------------------------------
# Parser (recursive descent, precedência: ↔ < → < ∨ < ∧ < ¬ < átomo)
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self):
        node = self._iff()
        kind, val, p = self.peek()
        if kind != "EOF":
            raise ParseError(f"Símbolo inesperado '{val}' na posição {p + 1}")
        return node

    def _iff(self):
        left = self._implies()
        while self.peek()[0] == "IFF":
            self.advance()
            right = self._implies()
            left = Iff(left, right)
        return left

    def _implies(self):
        left = self._or()
        if self.peek()[0] == "IMPLIES":
            self.advance()
            right = self._implies()
            return Implies(left, right)
        return left

    def _or(self):
        left = self._and()
        while self.peek()[0] == "OR":
            self.advance()
            right = self._and()
            left = Or(left, right)
        return left

    def _and(self):
        left = self._not()
        while self.peek()[0] == "AND":
            self.advance()
            right = self._not()
            left = And(left, right)
        return left

    def _not(self):
        if self.peek()[0] == "NOT":
            self.advance()
            operand = self._not()
            return Not(operand)
        return self._atom()

    def _atom(self):
        kind, val, p = self.peek()
        if kind == "LPAREN":
            self.advance()
            node = self._iff()
            kind2, val2, p2 = self.peek()
            if kind2 != "RPAREN":
                raise ParseError(
                    f"Parêntese ')' esperado, mas encontrei "
                    f"'{val2 or 'fim da fórmula'}' na posição {p2 + 1}"
                )
            self.advance()
            return node
        if kind == "VAR":
            self.advance()
            return Var(val)
        raise ParseError(
            f"Esperava uma variável, '(' ou negação, mas encontrei "
            f"'{val or 'fim da fórmula'}' na posição {p + 1}"
        )


def get_vars(node):
    if isinstance(node, Var):
        return [node.name]
    if isinstance(node, Not):
        return get_vars(node.operand)
    return get_vars(node.left) + get_vars(node.right)


def parse_formula(text):
    if not text or not text.strip():
        raise ParseError("Fórmula vazia.")
    tokens = tokenize(text)
    root = Parser(tokens).parse()
    variables = sorted(set(get_vars(root)))
    if not variables:
        raise ParseError("A fórmula não contém nenhuma variável.")
    return root, variables


# ---------------------------------------------------------------------------
# Tabela-verdade
# ---------------------------------------------------------------------------

def _collect_subexprs(node, seen):
    if isinstance(node, Var):
        return
    if isinstance(node, Not):
        _collect_subexprs(node.operand, seen)
    else:
        _collect_subexprs(node.left, seen)
        _collect_subexprs(node.right, seen)
    seen[str(node)] = node


def generate_truth_table(root, variables):
    subexprs = {}
    _collect_subexprs(root, subexprs)
    sub_labels = list(subexprs.keys())

    headers = list(variables) + sub_labels

    rows = []
    for combo in itertools.product([True, False], repeat=len(variables)):
        env = dict(zip(variables, combo))
        row = list(combo)
        for label in sub_labels:
            row.append(subexprs[label].eval(env))
        rows.append(row)

    final_label = str(root)
    if final_label in headers:
        final_index = headers.index(final_label)
    else:
        final_index = len(headers) - 1
    final_values = [row[final_index] for row in rows]

    if all(final_values):
        classification = "Tautologia — a fórmula é sempre verdadeira"
    elif not any(final_values):
        classification = "Contradição — a fórmula é sempre falsa"
    else:
        classification = "Contingência — o valor depende das variáveis"

    return headers, rows, classification
