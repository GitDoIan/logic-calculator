"""Interface gráfica (Tkinter) da Calculadora Lógica.

Paleta e hierarquia tipográfica inspiradas em princípios de design editorial
minimalista (monocromático quente, cor só com função semântica, espaçamento
generoso) — adaptados aos widgets nativos do Tkinter/ttk.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from logic_parser import parse_formula, generate_truth_table, ParseError
from nl_parser import NaturalLanguageParser, NLParseError

COLORS = {
    "bg": "#FBFBFA",
    "surface": "#FFFFFF",
    "border": "#E5E4E0",
    "text": "#111111",
    "text_muted": "#787774",
    "accent": "#111111",
    "accent_hover": "#333333",
    "taut_bg": "#EDF3EC", "taut_fg": "#346538",
    "contra_bg": "#FDEBEC", "contra_fg": "#9F2F2D",
    "conting_bg": "#E1F3FE", "conting_fg": "#1F6C9F",
}

FONT_UI = ("Helvetica Neue", 12)
FONT_UI_BOLD = ("Helvetica Neue", 12, "bold")
FONT_MONO = ("Menlo", 14)
FONT_MONO_BOLD = ("Menlo", 13, "bold")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora Lógica")
        self.geometry("920x680")
        self.minsize(780, 580)
        self.configure(bg=COLORS["bg"])
        self._build_style()
        self._build_ui()

    # ------------------------------------------------------------- estilo

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Surface.TFrame", background=COLORS["surface"])

        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=FONT_UI)
        style.configure("Muted.TLabel", background=COLORS["bg"], foreground=COLORS["text_muted"], font=FONT_UI)
        style.configure("Formula.TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=FONT_MONO_BOLD)

        for name, bg, fg in [
            ("Taut.TLabel", COLORS["taut_bg"], COLORS["taut_fg"]),
            ("Contra.TLabel", COLORS["contra_bg"], COLORS["contra_fg"]),
            ("Conting.TLabel", COLORS["conting_bg"], COLORS["conting_fg"]),
        ]:
            style.configure(name, background=bg, foreground=fg, font=FONT_UI_BOLD, padding=(10, 5))

        style.configure(
            "TButton", font=FONT_UI, padding=8,
            background=COLORS["surface"], foreground=COLORS["text"],
            borderwidth=1, relief="solid",
        )
        style.map("TButton", background=[("active", "#F0F0EE")])

        style.configure(
            "Accent.TButton", font=FONT_UI_BOLD, padding=(16, 10),
            background=COLORS["accent"], foreground="#FFFFFF", borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLORS["accent_hover"]), ("pressed", COLORS["accent_hover"])],
        )

        style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
        style.configure(
            "TNotebook.Tab", font=FONT_UI, padding=(18, 10),
            background=COLORS["bg"], foreground=COLORS["text_muted"],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["surface"])],
            foreground=[("selected", COLORS["text"])],
        )

        style.configure(
            "TEntry", padding=10, fieldbackground=COLORS["surface"],
            bordercolor=COLORS["border"], lightcolor=COLORS["border"], darkcolor=COLORS["border"],
        )

        style.configure(
            "Treeview", background=COLORS["surface"], fieldbackground=COLORS["surface"],
            foreground=COLORS["text"], font=FONT_MONO, rowheight=28, borderwidth=0,
        )
        style.configure(
            "Treeview.Heading", font=FONT_UI_BOLD,
            background=COLORS["bg"], foreground=COLORS["text"], relief="flat", padding=6,
        )
        style.map("Treeview.Heading", background=[("active", COLORS["bg"])])

        style.configure("TScrollbar", background=COLORS["bg"], troughcolor=COLORS["bg"], borderwidth=0)

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        outer = ttk.Frame(self, padding=(24, 20))
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Calculadora Lógica", font=("Helvetica Neue", 20, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="Monte uma fórmula com símbolos, texto ou uma frase em português.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(2, 16))

        notebook = ttk.Notebook(outer)
        notebook.pack(fill="x")

        tab_symbolic = ttk.Frame(notebook, padding=18)
        notebook.add(tab_symbolic, text="Fórmula Lógica")
        self._build_symbolic_tab(tab_symbolic)

        tab_nl = ttk.Frame(notebook, padding=18)
        notebook.add(tab_nl, text="Linguagem Natural")
        self._build_nl_tab(tab_nl)

        self._build_result_area(outer)

    def _build_symbolic_tab(self, parent):
        ttk.Label(
            parent,
            text="Aceita símbolos (¬ ∧ ∨ → ↔) e texto (NOT/AND/OR, NÃO/E/OU, ! & | -> <->):",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        self.formula_var = tk.StringVar()
        self.formula_entry = ttk.Entry(parent, textvariable=self.formula_var, font=FONT_MONO)
        self.formula_entry.pack(fill="x", pady=(0, 14))

        btn_frame = ttk.Frame(parent)
        btn_frame.pack()

        rows = [
            ["p", "q", "r", "s", "t"],
            ["u", "v", "w", "x", "y"],
            ["(", ")", "¬", "∧", "∨"],
            ["→", "↔", "⌫"],
        ]
        for r, row in enumerate(rows):
            for c, label in enumerate(row):
                ttk.Button(
                    btn_frame, text=label, width=5,
                    command=lambda l=label: self._on_button(l),
                ).grid(row=r, column=c, padx=4, pady=4)

        bottom_bar = ttk.Frame(parent)
        bottom_bar.pack(fill="x", pady=(16, 0))
        ttk.Button(
            bottom_bar, text="Limpar", command=lambda: self._on_button("Limpar"),
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            bottom_bar, text="Calcular", style="Accent.TButton", command=self._on_calculate_symbolic,
        ).pack(side="left", fill="x", expand=True)

    def _on_button(self, label):
        if label == "Limpar":
            self.formula_var.set("")
        elif label == "⌫":
            self.formula_var.set(self.formula_var.get()[:-1])
        else:
            try:
                pos = self.formula_entry.index(tk.INSERT)
            except tk.TclError:
                pos = len(self.formula_var.get())
            cur = self.formula_var.get()
            self.formula_var.set(cur[:pos] + label + cur[pos:])
            self.formula_entry.icursor(pos + len(label))
        self.formula_entry.focus_set()

    def _build_nl_tab(self, parent):
        ttk.Label(
            parent,
            text='Digite uma frase em português (ex: "se chove então a rua molha"):',
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        self.nl_text = tk.Text(
            parent, height=4, font=FONT_MONO, wrap="word",
            bg=COLORS["surface"], fg=COLORS["text"], relief="solid", borderwidth=1,
            highlightthickness=0, padx=10, pady=8,
        )
        self.nl_text.pack(fill="x", pady=(0, 14))

        ttk.Button(
            parent, text="Converter e Calcular", style="Accent.TButton", command=self._on_calculate_nl,
        ).pack(fill="x")

        self.legend_label = ttk.Label(parent, text="", style="Muted.TLabel", justify="left")
        self.legend_label.pack(anchor="w", pady=(12, 0))

    def _build_result_area(self, parent):
        ttk.Separator(parent).pack(fill="x", pady=20)

        self.formula_display = ttk.Label(parent, text="", style="Formula.TLabel")
        self.formula_display.pack(anchor="w")

        self.classification_label = ttk.Label(parent, text="", style="Conting.TLabel")
        self.classification_label.pack(anchor="w", pady=(8, 14))

        table_frame = ttk.Frame(parent, style="Surface.TFrame")
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, show="headings")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

    # ---------------------------------------------------------- handlers

    def _on_calculate_symbolic(self):
        self._compute_and_display(self.formula_var.get())

    def _on_calculate_nl(self):
        text = self.nl_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Aviso", "Digite uma frase antes de converter.")
            return
        try:
            formula_text, legend = NaturalLanguageParser().parse(text)
        except NLParseError as e:
            messagebox.showerror("Erro ao interpretar frase", str(e))
            return

        legend_str = "\n".join(f"{k}: {v}" for k, v in legend.items())
        self.legend_label.config(text=legend_str)
        self._compute_and_display(formula_text)

    def _compute_and_display(self, formula_text):
        if not formula_text.strip():
            messagebox.showwarning("Aviso", "Digite ou monte uma fórmula antes de calcular.")
            return
        try:
            root, variables = parse_formula(formula_text)
            headers, rows, classification = generate_truth_table(root, variables)
        except ParseError as e:
            messagebox.showerror("Erro na fórmula", str(e))
            return

        self.formula_display.config(text=f"Fórmula: {root}")
        if classification.startswith("Tautologia"):
            style_name = "Taut.TLabel"
        elif classification.startswith("Contradição"):
            style_name = "Contra.TLabel"
        else:
            style_name = "Conting.TLabel"
        self.classification_label.config(text=classification, style=style_name)

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = headers
        for h in headers:
            self.tree.heading(h, text=h)
            self.tree.column(h, width=max(70, 13 * len(h)), anchor="center")
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=["V" if v else "F" for v in row], tags=(tag,))
        self.tree.tag_configure("odd", background="#F7F6F3")
        self.tree.tag_configure("even", background=COLORS["surface"])


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
