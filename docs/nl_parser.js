/* Interpretação de frases em português baseada em regras (porte de nl_parser.py). */

class NLParseError extends Error {}

class NaturalLanguageParser {
  parse(text) {
    this.counter = 1;
    this.legend = {};
    const formula = this._parseClause(text);
    if (Object.keys(this.legend).length === 0) {
      throw new NLParseError("Não consegui identificar nenhuma proposição na frase.");
    }
    return { formula, legend: this.legend };
  }

  _makeVar(clauseRaw) {
    const clause = clauseRaw.trim().replace(/\.+$/, "").trim();
    if (!clause) {
      throw new NLParseError(
        "Frase incompleta: parece faltar o texto de uma proposição " +
        "(confira se não ficou nada em branco depois de 'e', 'ou', 'se' etc.)."
      );
    }
    const label = `P${this.counter}`;
    this.counter += 1;
    this.legend[label] = clause;
    return label;
  }

  _parseClause(textRaw) {
    const text = textRaw.trim();
    if (!text) throw new NLParseError("Frase incompleta.");

    let m = /\bse\s+e\s+somente\s+se\b/i.exec(text);
    if (m) {
      const left = text.slice(0, m.index);
      const right = text.slice(m.index + m[0].length);
      return `(${this._parseClause(left)} ↔ ${this._parseClause(right)})`;
    }

    m = /^\s*se\s+(.*?)\s*,?\s*ent[aã]o\s+(.*)$/i.exec(text);
    if (m) {
      return `(${this._parseClause(m[1])} → ${this._parseClause(m[2])})`;
    }

    let parts = text.split(/\bou\b/i);
    if (parts.length > 1) {
      return "(" + parts.map((p) => this._parseClause(p)).join(" ∨ ") + ")";
    }

    parts = text.split(/\be\b/i);
    if (parts.length > 1) {
      return "(" + parts.map((p) => this._parseClause(p)).join(" ∧ ") + ")";
    }

    m = /^\s*n[aã]o\s+(.*)$/i.exec(text);
    if (m) {
      return `¬${this._parseClause(m[1])}`;
    }

    return this._makeVar(text);
  }
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { NLParseError, NaturalLanguageParser };
}
