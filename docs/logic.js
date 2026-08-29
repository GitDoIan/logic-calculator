/* Tokenizer, parser, avaliador e gerador de tabela-verdade (porte de logic_parser.py). */

class ParseError extends Error {}

class Var {
  constructor(name) { this.name = name; }
  eval(env) { return env[this.name]; }
  toString() { return this.name; }
}

class Not {
  constructor(operand) { this.operand = operand; }
  eval(env) { return !this.operand.eval(env); }
  toString() {
    const s = String(this.operand);
    if (this.operand instanceof And || this.operand instanceof Or ||
        this.operand instanceof Implies || this.operand instanceof Iff) {
      return `¬(${s})`;
    }
    return `¬${s}`;
  }
}

function wrap(node) {
  const s = String(node);
  if (node instanceof And || node instanceof Or || node instanceof Implies || node instanceof Iff) {
    return `(${s})`;
  }
  return s;
}

class And {
  constructor(left, right) { this.left = left; this.right = right; }
  eval(env) { return this.left.eval(env) && this.right.eval(env); }
  toString() { return `${wrap(this.left)} ∧ ${wrap(this.right)}`; }
}

class Or {
  constructor(left, right) { this.left = left; this.right = right; }
  eval(env) { return this.left.eval(env) || this.right.eval(env); }
  toString() { return `${wrap(this.left)} ∨ ${wrap(this.right)}`; }
}

class Implies {
  constructor(left, right) { this.left = left; this.right = right; }
  eval(env) { return (!this.left.eval(env)) || this.right.eval(env); }
  toString() { return `${wrap(this.left)} → ${wrap(this.right)}`; }
}

class Iff {
  constructor(left, right) { this.left = left; this.right = right; }
  eval(env) { return this.left.eval(env) === this.right.eval(env); }
  toString() { return `${wrap(this.left)} ↔ ${wrap(this.right)}`; }
}

const SYMBOL_MAP = {
  "<->": "IFF", "->": "IMPLIES",
  "¬": "NOT", "~": "NOT", "!": "NOT",
  "∧": "AND", "&": "AND", "*": "AND",
  "∨": "OR", "|": "OR", "+": "OR",
  "↔": "IFF", "→": "IMPLIES",
  "(": "LPAREN", ")": "RPAREN",
};
const SYMBOLS_SORTED = Object.keys(SYMBOL_MAP).sort((a, b) => b.length - a.length);

const WORD_KEYWORDS = {
  not: "NOT", nao: "NOT",
  and: "AND", e: "AND",
  or: "OR", ou: "OR",
  implica: "IMPLIES",
  sse: "IFF", iff: "IFF",
};

function stripAccents(s) {
  return s.normalize("NFKD").replace(/[̀-ͯ]/g, "");
}

function isWordChar(ch, first) {
  if (ch === "_") return true;
  if (/[A-Za-zÀ-ÖØ-öø-ÿ]/.test(ch)) return true;
  if (!first && /[0-9]/.test(ch)) return true;
  return false;
}

function tokenize(text) {
  const tokens = [];
  let i = 0;
  const n = text.length;
  while (i < n) {
    const ch = text[i];
    if (/\s/.test(ch)) { i += 1; continue; }

    let matchedSymbol = null;
    for (const sym of SYMBOLS_SORTED) {
      if (text.startsWith(sym, i)) { matchedSymbol = sym; break; }
    }
    if (matchedSymbol) {
      tokens.push([SYMBOL_MAP[matchedSymbol], matchedSymbol, i]);
      i += matchedSymbol.length;
      continue;
    }

    if (isWordChar(ch, true)) {
      let j = i + 1;
      while (j < n && isWordChar(text[j], false)) j += 1;
      const word = text.slice(i, j);
      const key = stripAccents(word).toLowerCase();
      if (Object.prototype.hasOwnProperty.call(WORD_KEYWORDS, key)) {
        tokens.push([WORD_KEYWORDS[key], word, i]);
      } else {
        tokens.push(["VAR", word, i]);
      }
      i = j;
      continue;
    }

    throw new ParseError(`Caractere não reconhecido: '${ch}' na posição ${i + 1}`);
  }
  tokens.push(["EOF", "", n]);
  return tokens;
}

class Parser {
  constructor(tokens) { this.tokens = tokens; this.pos = 0; }
  peek() { return this.tokens[this.pos]; }
  advance() { return this.tokens[this.pos++]; }

  parse() {
    const node = this.iff_();
    const [kind, val, p] = this.peek();
    if (kind !== "EOF") throw new ParseError(`Símbolo inesperado '${val}' na posição ${p + 1}`);
    return node;
  }

  iff_() {
    let left = this.implies_();
    while (this.peek()[0] === "IFF") {
      this.advance();
      const right = this.implies_();
      left = new Iff(left, right);
    }
    return left;
  }

  implies_() {
    const left = this.or_();
    if (this.peek()[0] === "IMPLIES") {
      this.advance();
      const right = this.implies_();
      return new Implies(left, right);
    }
    return left;
  }

  or_() {
    let left = this.and_();
    while (this.peek()[0] === "OR") {
      this.advance();
      const right = this.and_();
      left = new Or(left, right);
    }
    return left;
  }

  and_() {
    let left = this.not_();
    while (this.peek()[0] === "AND") {
      this.advance();
      const right = this.not_();
      left = new And(left, right);
    }
    return left;
  }

  not_() {
    if (this.peek()[0] === "NOT") {
      this.advance();
      return new Not(this.not_());
    }
    return this.atom_();
  }

  atom_() {
    const [kind, val, p] = this.peek();
    if (kind === "LPAREN") {
      this.advance();
      const node = this.iff_();
      const [kind2, val2, p2] = this.peek();
      if (kind2 !== "RPAREN") {
        throw new ParseError(`Parêntese ')' esperado, mas encontrei '${val2 || "fim da fórmula"}' na posição ${p2 + 1}`);
      }
      this.advance();
      return node;
    }
    if (kind === "VAR") {
      this.advance();
      return new Var(val);
    }
    throw new ParseError(`Esperava uma variável, '(' ou negação, mas encontrei '${val || "fim da fórmula"}' na posição ${p + 1}`);
  }
}

function getVars(node) {
  if (node instanceof Var) return [node.name];
  if (node instanceof Not) return getVars(node.operand);
  return [...getVars(node.left), ...getVars(node.right)];
}

function parseFormula(text) {
  if (!text || !text.trim()) throw new ParseError("Fórmula vazia.");
  const tokens = tokenize(text);
  const root = new Parser(tokens).parse();
  const variables = [...new Set(getVars(root))].sort();
  if (variables.length === 0) throw new ParseError("A fórmula não contém nenhuma variável.");
  return { root, variables };
}

function collectSubexprs(node, seen) {
  if (node instanceof Var) return;
  if (node instanceof Not) {
    collectSubexprs(node.operand, seen);
  } else {
    collectSubexprs(node.left, seen);
    collectSubexprs(node.right, seen);
  }
  seen.set(String(node), node);
}

function generateTruthTable(root, variables) {
  const subexprs = new Map();
  collectSubexprs(root, subexprs);
  const subLabels = [...subexprs.keys()];
  const headers = [...variables, ...subLabels];

  const n = variables.length;
  const rows = [];
  for (let i = 0; i < (1 << n); i += 1) {
    const combo = variables.map((_, j) => ((i >> (n - 1 - j)) & 1) === 0);
    const env = {};
    variables.forEach((v, j) => { env[v] = combo[j]; });
    const row = [...combo];
    for (const label of subLabels) row.push(subexprs.get(label).eval(env));
    rows.push(row);
  }

  const finalLabel = String(root);
  const finalIndex = headers.includes(finalLabel) ? headers.indexOf(finalLabel) : headers.length - 1;
  const finalValues = rows.map((row) => row[finalIndex]);

  let classification;
  if (finalValues.every(Boolean)) {
    classification = "Tautologia — a fórmula é sempre verdadeira";
  } else if (!finalValues.some(Boolean)) {
    classification = "Contradição — a fórmula é sempre falsa";
  } else {
    classification = "Contingência — o valor depende das variáveis";
  }

  return { headers, rows, classification };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { ParseError, Var, Not, And, Or, Implies, Iff, tokenize, parseFormula, generateTruthTable };
}
