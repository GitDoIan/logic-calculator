(function () {
  const formulaInput = document.getElementById("formula-input");
  const nlInput = document.getElementById("nl-input");
  const legendEl = document.getElementById("legend");
  const formulaDisplay = document.getElementById("formula-display");
  const classificationEl = document.getElementById("classification");
  const tableWrap = document.getElementById("table-wrap");
  const errorEl = document.getElementById("error");

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.target).classList.add("active");
    });
  });

  document.querySelectorAll(".key").forEach((key) => {
    key.addEventListener("click", () => {
      const label = key.dataset.key;
      if (label === "Limpar") {
        formulaInput.value = "";
      } else if (label === "back") {
        formulaInput.value = formulaInput.value.slice(0, -1);
      } else {
        const start = formulaInput.selectionStart ?? formulaInput.value.length;
        const end = formulaInput.selectionEnd ?? formulaInput.value.length;
        const cur = formulaInput.value;
        formulaInput.value = cur.slice(0, start) + label + cur.slice(end);
        const pos = start + label.length;
        formulaInput.setSelectionRange(pos, pos);
      }
      formulaInput.focus();
    });
  });

  document.getElementById("clear-btn").addEventListener("click", () => {
    formulaInput.value = "";
    formulaInput.focus();
  });

  document.getElementById("calc-btn").addEventListener("click", () => {
    compute(formulaInput.value);
  });

  document.getElementById("nl-btn").addEventListener("click", () => {
    const text = nlInput.value.trim();
    legendEl.textContent = "";
    if (!text) {
      showError("Digite uma frase antes de converter.");
      return;
    }
    try {
      const { formula, legend } = new NaturalLanguageParser().parse(text);
      legendEl.textContent = Object.entries(legend).map(([k, v]) => `${k}: ${v}`).join("\n");
      compute(formula);
    } catch (e) {
      showError(e.message);
    }
  });

  function showError(msg) {
    errorEl.textContent = msg;
    errorEl.style.display = "block";
    formulaDisplay.textContent = "";
    classificationEl.style.display = "none";
    tableWrap.innerHTML = "";
  }

  function compute(formulaText) {
    if (!formulaText || !formulaText.trim()) {
      showError("Digite ou monte uma fórmula antes de calcular.");
      return;
    }
    let root, variables, headers, rows, classification;
    try {
      ({ root, variables } = parseFormula(formulaText));
      ({ headers, rows, classification } = generateTruthTable(root, variables));
    } catch (e) {
      showError(e.message);
      return;
    }

    errorEl.style.display = "none";
    formulaDisplay.textContent = `Fórmula: ${root}`;

    classificationEl.style.display = "inline-block";
    classificationEl.textContent = classification;
    classificationEl.className = "classification " +
      (classification.startsWith("Tautologia") ? "taut" :
       classification.startsWith("Contradição") ? "contra" : "conting");

    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    headers.forEach((h) => {
      const th = document.createElement("th");
      th.textContent = h;
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    rows.forEach((row) => {
      const tr = document.createElement("tr");
      row.forEach((v) => {
        const td = document.createElement("td");
        td.textContent = v ? "V" : "F";
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    tableWrap.innerHTML = "";
    tableWrap.appendChild(table);
  }
})();
