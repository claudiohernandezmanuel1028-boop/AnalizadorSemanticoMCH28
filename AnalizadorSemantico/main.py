"""
main.py — Interfaz gráfica tkinter para el Analizador Semántico ClaudioComp
Estilo oscuro Catppuccin Mocha
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

# Asegurar que el directorio del proyecto esté en el path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.semantic import analizar_semantico

# ─── Paleta de colores Catppuccin Mocha ───────────────────────────────────────
C_BASE    = "#1e1e2e"
C_MANTLE  = "#181825"
C_SURFACE = "#313244"
C_BLUE    = "#89b4fa"
C_TEXT    = "#cdd6f4"
C_RED     = "#f38ba8"
C_GREEN   = "#a6e3a1"
C_MAUVE   = "#cba6f7"
C_PEACH   = "#fab387"
C_OVERLAY = "#45475a"
C_SUBTEXT = "#6c7086"

# ─── Ejemplos de código ───────────────────────────────────────────────────────

CODIGO_INICIAL = """\
// Ejemplo inicial
int edad = 20;
float precio = 150.50;
bool activo = true;

if (edad >= 18) {
    string mensaje = "Mayor de edad";
    precio = precio + 5.0;
}
"""

CODIGO_CORRECTO = """\
// Programa sin errores semánticos
int contador = 0;
float total = 100.0;
bool activo = true;
string nombre = "ClaudioComp";

contador = contador + 1;
total = total * 2.0;

if (activo) {
    int resultado = contador + 5;
    bool valido = activo;
}

while (contador < 10) {
    contador = contador + 1;
}
"""

CODIGO_ERRORES = """\
// Programa con errores semánticos
int x = 10;
int x = 20;
string nombre = "Hola";
bool flag = true;

y = 5;
x = nombre;
x = x + flag;
int z = x + nombre;
"""


# ─── Aplicación principal ─────────────────────────────────────────────────────

class AnalizadorApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Compilador Claudio — Analizador Semántico")
        self.root.geometry("1280x780")
        self.root.minsize(1100, 680)
        self.root.configure(bg=C_BASE)

        self._aplicar_estilos()
        self._construir_interfaz()

    # ── Estilos ttk ───────────────────────────────────

    def _aplicar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook",
                        background=C_BASE, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=C_SURFACE, foreground=C_TEXT,
                        font=("Segoe UI", 10, "bold"), padding=[14, 5])
        style.map("TNotebook.Tab",
                  background=[("selected", C_BLUE)],
                  foreground=[("selected", C_MANTLE)])

        style.configure("Treeview",
                        background=C_BASE, foreground=C_TEXT,
                        rowheight=24, fieldbackground=C_BASE,
                        font=("Consolas", 10))
        style.configure("Treeview.Heading",
                        background=C_SURFACE, foreground=C_BLUE,
                        font=("Segoe UI", 10, "bold"), relief=tk.FLAT)
        style.map("Treeview", background=[("selected", C_OVERLAY)])

        style.configure("TScrollbar",
                        background=C_OVERLAY, troughcolor=C_SURFACE,
                        arrowcolor=C_TEXT, borderwidth=0)

    # ── Construcción de la interfaz ───────────────────

    def _construir_interfaz(self):
        # Cabecera
        frame_header = tk.Frame(self.root, bg=C_MANTLE, pady=10)
        frame_header.pack(fill=tk.X)

        tk.Label(frame_header,
                 text="🧠 Compilador Claudio — Analizador Semántico",
                 font=("Segoe UI", 16, "bold"),
                 bg=C_MANTLE, fg=C_TEXT).pack()
        tk.Label(frame_header,
                 text="Manuel Claudio Hernandez  |  2-21-0644",
                 font=("Segoe UI", 10),
                 bg=C_MANTLE, fg=C_MAUVE).pack()

        # Cuerpo principal
        frame_cuerpo = tk.Frame(self.root, bg=C_BASE)
        frame_cuerpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._construir_panel_editor(frame_cuerpo)
        self._construir_panel_resultados(frame_cuerpo)

        # Barra inferior
        self._construir_barra_botones()
        self._construir_barra_estado()

    # ── Panel izquierdo: editor ───────────────────────

    def _construir_panel_editor(self, parent):
        frame = tk.Frame(parent, bg=C_BASE)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(frame,
                 text="📝 Código Fuente ClaudioComp",
                 font=("Segoe UI", 10, "bold"),
                 bg=C_BASE, fg=C_BLUE).pack(anchor="w", pady=(0, 3))

        frame_edit = tk.Frame(frame, bg=C_SURFACE, bd=1, relief=tk.FLAT)
        frame_edit.pack(fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(frame_edit, bg=C_OVERLAY)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = tk.Scrollbar(frame_edit, orient=tk.HORIZONTAL, bg=C_OVERLAY)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.editor = tk.Text(
            frame_edit,
            font=("Consolas", 12),
            bg=C_BASE, fg=C_TEXT,
            insertbackground="#f5c2e7",
            selectbackground=C_OVERLAY,
            wrap=tk.NONE,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            padx=10, pady=10,
            relief=tk.FLAT, borderwidth=0,
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.editor.yview)
        scroll_x.config(command=self.editor.xview)

        self.editor.insert("1.0", CODIGO_INICIAL)

        # Botones de ejemplo en la parte inferior del editor
        frame_ej = tk.Frame(frame, bg=C_BASE)
        frame_ej.pack(fill=tk.X, pady=(5, 0))

        estilo_ej = dict(font=("Segoe UI", 9, "bold"), relief=tk.FLAT,
                         cursor="hand2", padx=10, pady=4, bd=0)

        tk.Button(frame_ej,
                  text="✅  Ejemplo Correcto",
                  bg="#2d4a3e", fg=C_GREEN,
                  activebackground="#1a3429",
                  command=self._cargar_ejemplo_correcto,
                  **estilo_ej).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(frame_ej,
                  text="❌  Ejemplo con Errores",
                  bg="#4a2d2d", fg=C_RED,
                  activebackground="#341a1a",
                  command=self._cargar_ejemplo_errores,
                  **estilo_ej).pack(side=tk.LEFT)

    # ── Panel derecho: notebook de resultados ─────────

    def _construir_panel_resultados(self, parent):
        frame = tk.Frame(parent, bg=C_BASE)
        frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.notebook = ttk.Notebook(frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._construir_tab_lexico()
        self._construir_tab_sintactico()
        self._construir_tab_semantico()

    # ── Tab 1: Léxico ─────────────────────────────────

    def _construir_tab_lexico(self):
        tab = tk.Frame(self.notebook, bg=C_BASE)
        self.notebook.add(tab, text="🔤  Análisis Léxico")

        frame_tabla = tk.Frame(tab, bg=C_SURFACE)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        cols = ("#", "Lexema", "Tipo", "Línea")
        self.tabla_lex = ttk.Treeview(frame_tabla, columns=cols,
                                       show="headings", selectmode="browse")
        for col, w, anc in [("#", 45, tk.CENTER), ("Lexema", 140, tk.W),
                             ("Tipo", 200, tk.W), ("Línea", 55, tk.CENTER)]:
            self.tabla_lex.heading(col, text=col)
            self.tabla_lex.column(col, width=w, anchor=anc)

        self.tabla_lex.tag_configure("error",      foreground=C_RED,   background="#2a1a1a")
        self.tabla_lex.tag_configure("reservada",  foreground=C_MAUVE)
        self.tabla_lex.tag_configure("numero",     foreground=C_PEACH)
        self.tabla_lex.tag_configure("cadena",     foreground=C_GREEN)
        self.tabla_lex.tag_configure("operador",   foreground="#89dceb")
        self.tabla_lex.tag_configure("ident",      foreground=C_TEXT)

        scroll_l = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL,
                                  command=self.tabla_lex.yview)
        self.tabla_lex.configure(yscrollcommand=scroll_l.set)
        self.tabla_lex.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_l.pack(side=tk.RIGHT, fill=tk.Y)

        # Errores léxicos
        self.txt_err_lex = self._construir_caja_errores(tab, "⚠ Errores Léxicos")

    # ── Tab 2: Sintáctico ─────────────────────────────

    def _construir_tab_sintactico(self):
        tab = tk.Frame(self.notebook, bg=C_BASE)
        self.notebook.add(tab, text="🌳  Análisis Sintáctico")

        tk.Label(tab, text="🧩 Nodos del AST",
                 font=("Segoe UI", 10, "bold"),
                 bg=C_BASE, fg=C_BLUE).pack(anchor="w", pady=(4, 3))

        frame_tabla = tk.Frame(tab, bg=C_SURFACE)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        cols = ("#", "Tipo de Nodo", "Detalle", "Estado")
        self.tabla_sint = ttk.Treeview(frame_tabla, columns=cols,
                                        show="headings", selectmode="browse")
        for col, w, anc in [("#", 40, tk.CENTER), ("Tipo de Nodo", 160, tk.W),
                             ("Detalle", 260, tk.W), ("Estado", 60, tk.CENTER)]:
            self.tabla_sint.heading(col, text=col)
            self.tabla_sint.column(col, width=w, anchor=anc)

        self.tabla_sint.tag_configure("ok",    foreground=C_GREEN)
        self.tabla_sint.tag_configure("error", foreground=C_RED, background="#2a1a1a")

        scroll_s = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL,
                                  command=self.tabla_sint.yview)
        self.tabla_sint.configure(yscrollcommand=scroll_s.set)
        self.tabla_sint.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_s.pack(side=tk.RIGHT, fill=tk.Y)

        self.txt_err_sint = self._construir_caja_errores(tab, "⚠ Errores Sintácticos")

    # ── Tab 3: Semántico ──────────────────────────────

    def _construir_tab_semantico(self):
        tab = tk.Frame(self.notebook, bg=C_BASE)
        self.notebook.add(tab, text="🧠  Análisis Semántico")

        # Tabla de símbolos (mitad superior)
        tk.Label(tab, text="📋 Tabla de Símbolos",
                 font=("Segoe UI", 10, "bold"),
                 bg=C_BASE, fg=C_BLUE).pack(anchor="w", pady=(4, 2))

        frame_sim = tk.Frame(tab, bg=C_SURFACE)
        frame_sim.pack(fill=tk.BOTH, expand=True)

        cols_sim = ("#", "Variable", "Tipo", "Ámbito", "Línea")
        self.tabla_sim = ttk.Treeview(frame_sim, columns=cols_sim,
                                       show="headings", selectmode="browse")
        for col, w, anc in [("#", 40, tk.CENTER), ("Variable", 130, tk.W),
                             ("Tipo", 80, tk.CENTER), ("Ámbito", 100, tk.W),
                             ("Línea", 55, tk.CENTER)]:
            self.tabla_sim.heading(col, text=col)
            self.tabla_sim.column(col, width=w, anchor=anc)

        self.tabla_sim.tag_configure("global", foreground=C_BLUE)
        self.tabla_sim.tag_configure("local",  foreground=C_MAUVE)

        scroll_sim = ttk.Scrollbar(frame_sim, orient=tk.VERTICAL,
                                    command=self.tabla_sim.yview)
        self.tabla_sim.configure(yscrollcommand=scroll_sim.set)
        self.tabla_sim.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_sim.pack(side=tk.RIGHT, fill=tk.Y)

        # Tabla de errores semánticos (mitad inferior)
        tk.Label(tab, text="⚠ Errores Semánticos",
                 font=("Segoe UI", 10, "bold"),
                 bg=C_BASE, fg=C_RED).pack(anchor="w", pady=(6, 2))

        frame_err = tk.Frame(tab, bg=C_SURFACE)
        frame_err.pack(fill=tk.BOTH, expand=True)

        cols_err = ("#", "Descripción del Error", "Línea")
        self.tabla_err_sem = ttk.Treeview(frame_err, columns=cols_err,
                                           show="headings", selectmode="browse",
                                           height=6)
        for col, w, anc in [("#", 40, tk.CENTER), ("Descripción del Error", 380, tk.W),
                             ("Línea", 55, tk.CENTER)]:
            self.tabla_err_sem.heading(col, text=col)
            self.tabla_err_sem.column(col, width=w, anchor=anc)

        self.tabla_err_sem.tag_configure("sem_error", foreground=C_RED, background="#2a1a1a")

        scroll_err_sem = ttk.Scrollbar(frame_err, orient=tk.VERTICAL,
                                        command=self.tabla_err_sem.yview)
        self.tabla_err_sem.configure(yscrollcommand=scroll_err_sem.set)
        self.tabla_err_sem.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_err_sem.pack(side=tk.RIGHT, fill=tk.Y)

        # Etiqueta de resultado semántico
        self.lbl_resultado_sem = tk.Label(
            tab, text="",
            font=("Segoe UI", 10, "bold"),
            bg=C_BASE, fg=C_GREEN,
        )
        self.lbl_resultado_sem.pack(anchor="w", pady=(4, 0))

    # ── Utilidad: caja de errores ─────────────────────

    def _construir_caja_errores(self, parent, titulo: str):
        frame_outer = tk.Frame(parent, bg=C_BASE)
        frame_outer.pack(fill=tk.X, pady=(6, 0))

        tk.Label(frame_outer, text=titulo,
                 font=("Segoe UI", 10, "bold"),
                 bg=C_BASE, fg=C_RED).pack(anchor="w")

        frame_inner = tk.Frame(frame_outer, bg="#2a1a1a", height=85)
        frame_inner.pack(fill=tk.X)
        frame_inner.pack_propagate(False)

        scroll = tk.Scrollbar(frame_inner, bg=C_OVERLAY)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        txt = tk.Text(frame_inner,
                      font=("Consolas", 10),
                      bg="#2a1a1a", fg=C_RED,
                      relief=tk.FLAT, borderwidth=0,
                      padx=8, pady=5,
                      state=tk.DISABLED,
                      yscrollcommand=scroll.set)
        txt.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=txt.yview)
        return txt

    # ── Barra de botones ──────────────────────────────

    def _construir_barra_botones(self):
        frame = tk.Frame(self.root, bg=C_MANTLE, pady=8)
        frame.pack(fill=tk.X, padx=10)

        estilo = dict(font=("Segoe UI", 10, "bold"), relief=tk.FLAT,
                      cursor="hand2", padx=18, pady=6, bd=0)

        tk.Button(frame, text="▶  Analizar",
                  bg=C_BLUE, fg=C_MANTLE,
                  activebackground="#74c7ec",
                  command=self.analizar, **estilo).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(frame, text="🗑  Limpiar",
                  bg=C_OVERLAY, fg=C_TEXT,
                  activebackground="#585b70",
                  command=self.limpiar, **estilo).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(frame, text="📂  Cargar Archivo",
                  bg=C_OVERLAY, fg=C_TEXT,
                  activebackground="#585b70",
                  command=self.cargar_archivo, **estilo).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(frame, text="💾  Guardar Resultados",
                  bg=C_OVERLAY, fg=C_TEXT,
                  activebackground="#585b70",
                  command=self.guardar_resultados, **estilo).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(frame, text="✕  Salir",
                  bg=C_RED, fg=C_MANTLE,
                  activebackground="#eba0ac",
                  command=self.root.quit, **estilo).pack(side=tk.RIGHT)

    # ── Barra de estado ───────────────────────────────

    def _construir_barra_estado(self):
        frame = tk.Frame(self.root, bg=C_MANTLE, pady=5)
        frame.pack(fill=tk.X)

        def lbl(texto, color=C_TEXT):
            l = tk.Label(frame, text=texto, font=("Segoe UI", 9),
                         bg=C_MANTLE, fg=color)
            l.pack(side=tk.LEFT, padx=15)
            return l

        self.lbl_tokens     = lbl("Tokens: 0", C_GREEN)
        self.lbl_err_lex    = lbl("Errores léxicos: 0", C_RED)
        self.lbl_err_sint   = lbl("Errores sintácticos: 0", C_RED)
        self.lbl_err_sem    = lbl("Errores semánticos: 0", C_RED)

        self.lbl_estado = tk.Label(frame, text="Listo",
                                   font=("Segoe UI", 9),
                                   bg=C_MANTLE, fg=C_SUBTEXT)
        self.lbl_estado.pack(side=tk.RIGHT, padx=15)

    # ── Carga de ejemplos ─────────────────────────────

    def _cargar_ejemplo_correcto(self):
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", CODIGO_CORRECTO)
        self.lbl_estado.config(text="Ejemplo correcto cargado", fg=C_GREEN)

    def _cargar_ejemplo_errores(self):
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", CODIGO_ERRORES)
        self.lbl_estado.config(text="Ejemplo con errores cargado", fg=C_PEACH)

    # ── Acción principal: Analizar ────────────────────

    def analizar(self):
        codigo = self.editor.get("1.0", tk.END)
        if not codigo.strip():
            messagebox.showwarning("Aviso", "El editor está vacío.")
            return

        self.lbl_estado.config(text="Analizando...", fg="#f9e2af")
        self.root.update()

        try:
            resultado = analizar_semantico(codigo)
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))
            self.lbl_estado.config(text="Error durante el análisis", fg=C_RED)
            return

        self._mostrar_lexico(resultado)
        self._mostrar_sintactico(resultado)
        self._mostrar_semantico(resultado)

        n_sem = len(resultado["errores_sem"])
        self.lbl_err_sem.config(
            text=f"Errores semánticos: {n_sem}",
            fg=C_RED if n_sem > 0 else C_GREEN,
        )
        self.lbl_estado.config(
            text="Análisis completado — Sin errores semánticos" if resultado["ok"]
            else f"Análisis completado — {n_sem} error(es) semántico(s)",
            fg=C_GREEN if resultado["ok"] else C_RED,
        )

    # ── Mostrar resultados léxicos ────────────────────

    def _mostrar_lexico(self, resultado):
        for item in self.tabla_lex.get_children():
            self.tabla_lex.delete(item)

        NOMBRES = {
            "INT": "Palabra Reservada (int)",
            "FLOAT_T": "Palabra Reservada (float)",
            "STRING_T": "Palabra Reservada (string)",
            "BOOL_T": "Palabra Reservada (bool)",
            "IF": "Palabra Reservada (if)",
            "HILUX": "Palabra Reservada (hilux)",
            "ELSE": "Palabra Reservada (else)",
            "WHILE": "Palabra Reservada (while)",
            "RETURN": "Palabra Reservada (return)",
            "TRUE": "Literal Booleano (true)",
            "FALSE": "Literal Booleano (false)",
            "IDENT": "Identificador",
            "NUM_INT": "Número Entero",
            "NUM_FLOAT": "Número Decimal",
            "CADENA": "Cadena de Texto",
            "SUMA": "Operador Suma",
            "RESTA": "Operador Resta",
            "MULT": "Operador Multiplicación",
            "DIV": "Operador División",
            "ASIGN": "Operador Asignación",
            "IGUAL": "Operador Igual",
            "DIFERENTE": "Operador Diferente",
            "MAYOR": "Operador Mayor que",
            "MENOR": "Operador Menor que",
            "MAYOR_IGUAL": "Operador Mayor o Igual",
            "MENOR_IGUAL": "Operador Menor o Igual",
            "AND": "Operador AND",
            "OR": "Operador OR",
            "NOT": "Operador NOT",
            "PAREN_A": "Paréntesis Abre",
            "PAREN_C": "Paréntesis Cierra",
            "LLAVE_A": "Llave Abre",
            "LLAVE_C": "Llave Cierra",
            "PCOMA": "Punto y Coma",
            "ERROR": "⚠ Error Léxico",
            "EOF": "Fin de Archivo",
        }

        TIPOS_RESERVADOS = {"INT", "FLOAT_T", "STRING_T", "BOOL_T",
                            "IF", "HILUX", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE"}

        conteo = 0
        for i, tok in enumerate(resultado["tokens"], 1):
            if tok.tipo == "EOF":
                break
            nombre = NOMBRES.get(tok.tipo, tok.tipo)
            if tok.tipo == "ERROR":
                tag = "error"
            elif tok.tipo in TIPOS_RESERVADOS:
                tag = "reservada"; conteo += 1
            elif tok.tipo in ("NUM_INT", "NUM_FLOAT"):
                tag = "numero"; conteo += 1
            elif tok.tipo == "CADENA":
                tag = "cadena"; conteo += 1
            elif tok.tipo.startswith(("SUMA", "RESTA", "MULT", "DIV",
                                       "ASIGN", "IGUAL", "DIFERENTE",
                                       "MAYOR", "MENOR", "AND", "OR", "NOT")):
                tag = "operador"; conteo += 1
            else:
                tag = "ident"; conteo += 1

            self.tabla_lex.insert("", tk.END,
                                   values=(i, tok.valor, nombre, tok.linea),
                                   tags=(tag,))

        # Errores léxicos
        errs = resultado["errores_lex"]
        self.txt_err_lex.config(state=tk.NORMAL)
        self.txt_err_lex.delete("1.0", tk.END)
        if errs:
            self.txt_err_lex.insert(tk.END, "\n".join(f"  {e}" for e in errs))
            self.txt_err_lex.config(fg=C_RED)
        else:
            self.txt_err_lex.insert(tk.END, "  ✓ No se encontraron errores léxicos.")
            self.txt_err_lex.config(fg=C_GREEN)
        self.txt_err_lex.config(state=tk.DISABLED)

        self.lbl_tokens.config(text=f"Tokens: {conteo}")
        n_lex = len(errs)
        self.lbl_err_lex.config(text=f"Errores léxicos: {n_lex}",
                                  fg=C_RED if n_lex else C_GREEN)

    # ── Mostrar resultados sintácticos ────────────────

    def _mostrar_sintactico(self, resultado):
        for item in self.tabla_sint.get_children():
            self.tabla_sint.delete(item)

        # Aplanar el AST para mostrarlo en la tabla
        ast = resultado.get("ast_nodos", None)
        # Extraemos nodos directamente del análisis
        # Para la tabla sintáctica reconstruimos desde el resultado
        # usando los nodos del AST que ya se procesaron
        nodos_flat = []
        try:
            from src.lexer import tokenizar
            from src.parser import parsear
            tokens_validos = [t for t in resultado["tokens"] if t.tipo not in ("ERROR", "EOF")]
            # Re-añadir EOF
            from src.lexer import Token
            tokens_validos.append(Token("EOF", "", 0))
            ast_local, _ = parsear(tokens_validos)
            self._aplanar_ast(ast_local, nodos_flat)
        except Exception:
            nodos_flat = []

        for i, nodo in enumerate(nodos_flat, 1):
            tipo_nodo = nodo.get("tipo", "")
            detalle   = self._detalle_nodo(nodo)
            es_error  = tipo_nodo == "ErrorSintactico"
            tag = "error" if es_error else "ok"
            icono = "✗" if es_error else "✓"
            self.tabla_sint.insert("", tk.END,
                                    values=(i, tipo_nodo, detalle, icono),
                                    tags=(tag,))

        # Errores sintácticos
        errs = resultado["errores_sint"]
        self.txt_err_sint.config(state=tk.NORMAL)
        self.txt_err_sint.delete("1.0", tk.END)
        if errs:
            self.txt_err_sint.insert(tk.END, "\n".join(f"  {e}" for e in errs))
            self.txt_err_sint.config(fg=C_RED)
        else:
            self.txt_err_sint.insert(tk.END, "  ✓ No se encontraron errores sintácticos.")
            self.txt_err_sint.config(fg=C_GREEN)
        self.txt_err_sint.config(state=tk.DISABLED)

        n_sint = len(errs)
        self.lbl_err_sint.config(text=f"Errores sintácticos: {n_sint}",
                                   fg=C_RED if n_sint else C_GREEN)

    def _aplanar_ast(self, nodo, lista, profundidad=0):
        """Recorre el AST y añade cada nodo a la lista."""
        if nodo is None:
            return
        tipo = nodo.get("tipo")
        lista.append(nodo)

        if tipo == "Programa":
            for hijo in nodo.get("cuerpo", []):
                self._aplanar_ast(hijo, lista, profundidad + 1)
        elif tipo == "If":
            self._aplanar_ast(nodo.get("cond"), lista, profundidad + 1)
            for hijo in nodo.get("entonces", []):
                self._aplanar_ast(hijo, lista, profundidad + 1)
            for hijo in (nodo.get("sino") or []):
                self._aplanar_ast(hijo, lista, profundidad + 1)
        elif tipo == "While":
            self._aplanar_ast(nodo.get("cond"), lista, profundidad + 1)
            for hijo in nodo.get("cuerpo", []):
                self._aplanar_ast(hijo, lista, profundidad + 1)
        elif tipo in ("DeclVar", "Return", "Asignacion"):
            self._aplanar_ast(nodo.get("expr"), lista, profundidad + 1)
        elif tipo == "BinOp":
            self._aplanar_ast(nodo.get("izq"), lista, profundidad + 1)
            self._aplanar_ast(nodo.get("der"), lista, profundidad + 1)
        elif tipo == "UnOp":
            self._aplanar_ast(nodo.get("expr"), lista, profundidad + 1)

    def _detalle_nodo(self, nodo) -> str:
        tipo = nodo.get("tipo", "")
        if tipo == "DeclVar":
            return f"{nodo.get('tipo_dato')} {nodo.get('nombre')}"
        if tipo == "Asignacion":
            return f"{nodo.get('nombre')} = ..."
        if tipo == "If":
            return f"if (línea {nodo.get('linea', '?')})"
        if tipo == "While":
            return f"while (línea {nodo.get('linea', '?')})"
        if tipo == "Return":
            return f"return (línea {nodo.get('linea', '?')})"
        if tipo == "BinOp":
            return f"op: {nodo.get('op')}"
        if tipo == "UnOp":
            return f"op: {nodo.get('op')}"
        if tipo == "Literal":
            return f"{nodo.get('tipo_dato')}: {nodo.get('valor')}"
        if tipo == "Var":
            return f"var: {nodo.get('nombre')}"
        if tipo == "ErrorSintactico":
            return nodo.get("msg", "")
        if tipo == "Programa":
            return "Inicio del programa"
        return ""

    # ── Mostrar resultados semánticos ─────────────────

    def _mostrar_semantico(self, resultado):
        # Limpiar
        for item in self.tabla_sim.get_children():
            self.tabla_sim.delete(item)
        for item in self.tabla_err_sem.get_children():
            self.tabla_err_sem.delete(item)

        # Tabla de símbolos
        for i, sim in enumerate(resultado["tabla"], 1):
            tag = "global" if sim["ambito"] == "global" else "local"
            self.tabla_sim.insert("", tk.END,
                                   values=(i, sim["nombre"], sim["tipo"],
                                           sim["ambito"], sim["linea"]),
                                   tags=(tag,))

        # Errores semánticos
        errores = resultado["errores_sem"]
        for i, err in enumerate(errores, 1):
            self.tabla_err_sem.insert("", tk.END,
                                       values=(i, err["msg"], err["linea"]),
                                       tags=("sem_error",))

        # Mensaje de resultado
        if resultado["ok"]:
            self.lbl_resultado_sem.config(
                text="✓ Análisis semántico correcto — No se encontraron errores",
                fg=C_GREEN,
            )
        else:
            n = len(errores)
            self.lbl_resultado_sem.config(
                text=f"✗ Se encontraron {n} error(es) semántico(s)",
                fg=C_RED,
            )

    # ── Limpiar ───────────────────────────────────────

    def limpiar(self):
        self.editor.delete("1.0", tk.END)
        for tabla in (self.tabla_lex, self.tabla_sint, self.tabla_sim, self.tabla_err_sem):
            for item in tabla.get_children():
                tabla.delete(item)
        for txt in (self.txt_err_lex, self.txt_err_sint):
            txt.config(state=tk.NORMAL)
            txt.delete("1.0", tk.END)
            txt.config(state=tk.DISABLED)
        self.lbl_resultado_sem.config(text="")
        self.lbl_tokens.config(text="Tokens: 0")
        self.lbl_err_lex.config(text="Errores léxicos: 0", fg=C_RED)
        self.lbl_err_sint.config(text="Errores sintácticos: 0", fg=C_RED)
        self.lbl_err_sem.config(text="Errores semánticos: 0", fg=C_RED)
        self.lbl_estado.config(text="Listo", fg=C_SUBTEXT)

    # ── Cargar archivo ────────────────────────────────

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Abrir archivo ClaudioComp",
            filetypes=[("Archivos ClaudioComp", "*.claudio *.txt"), ("Todos", "*.*")],
            initialdir=os.path.join(BASE_DIR, "examples"),
        )
        if ruta:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", contenido)
                self.lbl_estado.config(
                    text=f"Archivo cargado: {os.path.basename(ruta)}", fg=C_GREEN)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

    # ── Guardar resultados ────────────────────────────

    def guardar_resultados(self):
        if not self.tabla_lex.get_children() and not self.tabla_sim.get_children():
            messagebox.showwarning("Aviso", "No hay resultados para guardar.")
            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar resultados",
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")],
        )
        if not ruta:
            return

        sep = "=" * 70
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(f"{sep}\n  ANÁLISIS LÉXICO — ClaudioComp\n{sep}\n")
                f.write(f"{'#':<5} {'Lexema':<22} {'Tipo':<32} {'Línea'}\n")
                f.write(f"{'-'*70}\n")
                for item in self.tabla_lex.get_children():
                    v = self.tabla_lex.item(item)["values"]
                    f.write(f"{str(v[0]):<5} {str(v[1]):<22} {str(v[2]):<32} {v[3]}\n")

                f.write(f"\n{sep}\n  ANÁLISIS SINTÁCTICO — AST\n{sep}\n")
                f.write(f"{'#':<5} {'Tipo de Nodo':<20} {'Detalle':<35} Estado\n")
                f.write(f"{'-'*70}\n")
                for item in self.tabla_sint.get_children():
                    v = self.tabla_sint.item(item)["values"]
                    f.write(f"{str(v[0]):<5} {str(v[1]):<20} {str(v[2]):<35} {v[3]}\n")

                f.write(f"\n{sep}\n  TABLA DE SÍMBOLOS\n{sep}\n")
                f.write(f"{'#':<5} {'Variable':<18} {'Tipo':<10} {'Ámbito':<15} Línea\n")
                f.write(f"{'-'*70}\n")
                for item in self.tabla_sim.get_children():
                    v = self.tabla_sim.item(item)["values"]
                    f.write(f"{str(v[0]):<5} {str(v[1]):<18} {str(v[2]):<10} {str(v[3]):<15} {v[4]}\n")

                f.write(f"\n{sep}\n  ERRORES SEMÁNTICOS\n{sep}\n")
                errs = self.tabla_err_sem.get_children()
                if errs:
                    for item in errs:
                        v = self.tabla_err_sem.item(item)["values"]
                        f.write(f"  [{v[2]}] {v[1]}\n")
                else:
                    f.write("  ✓ No se encontraron errores semánticos.\n")

                f.write(f"\n{self.lbl_tokens.cget('text')}\n")
                f.write(f"{self.lbl_err_lex.cget('text')}\n")
                f.write(f"{self.lbl_err_sint.cget('text')}\n")
                f.write(f"{self.lbl_err_sem.cget('text')}\n")

            messagebox.showinfo("Guardado", f"Resultados guardados en:\n{ruta}")
            self.lbl_estado.config(text="Resultados guardados", fg=C_GREEN)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")


# ─── Punto de entrada ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = AnalizadorApp(root)
    root.mainloop()
