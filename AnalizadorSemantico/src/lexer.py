"""
lexer.py — Tokenizador para el lenguaje ClaudioComp
Produce una lista de objetos Token con campos: tipo, valor, linea.
"""

import re
from dataclasses import dataclass


@dataclass
class Token:
    tipo: str
    valor: str
    linea: int

    def __repr__(self):
        return f"Token({self.tipo}, {self.valor!r}, línea={self.linea})"


# ─────────────────────────────────────────────
#  Palabras reservadas
# ─────────────────────────────────────────────
PALABRAS_RESERVADAS = {
    "int":    "INT",
    "float":  "FLOAT_T",
    "string": "STRING_T",
    "bool":   "BOOL_T",
    "if":     "IF",
    "hilux":  "HILUX",
    "else":   "ELSE",
    "while":  "WHILE",
    "return": "RETURN",
    "true":   "TRUE",
    "false":  "FALSE",
}

# ─────────────────────────────────────────────
#  Patrones (orden importa: más largo primero)
# ─────────────────────────────────────────────
PATRONES = [
    # Comentarios (ignorados, pero actualizan contador de líneas)
    ("COMENTARIO_BLOQUE", r"/\*[\s\S]*?\*/"),
    ("COMENTARIO_LINEA",  r"//[^\n]*"),

    # Literales
    ("NUM_FLOAT",  r"\d+\.\d+"),
    ("NUM_INT",    r"\d+"),
    ("CADENA",     r'"(?:[^"\\]|\\.)*"'),

    # Operadores de dos caracteres (antes que los de uno)
    ("IGUAL",        r"=="),
    ("DIFERENTE",    r"!="),
    ("MAYOR_IGUAL",  r">="),
    ("MENOR_IGUAL",  r"<="),
    ("AND",          r"&&"),
    ("OR",           r"\|\|"),

    # Operadores de un carácter
    ("SUMA",   r"\+"),
    ("RESTA",  r"-"),
    ("MULT",   r"\*"),
    ("DIV",    r"/"),
    ("ASIGN",  r"="),
    ("MAYOR",  r">"),
    ("MENOR",  r"<"),
    ("NOT",    r"!"),

    # Delimitadores
    ("PAREN_A",  r"\("),
    ("PAREN_C",  r"\)"),
    ("LLAVE_A",  r"\{"),
    ("LLAVE_C",  r"\}"),
    ("PCOMA",    r";"),

    # Identificadores / palabras reservadas
    ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),

    # Espacios y saltos de línea
    ("NUEVA_LINEA", r"\n"),
    ("ESPACIO",     r"[ \t\r]+"),

    # Cualquier otro carácter = error
    ("ERROR", r"."),
]

REGEX_MAESTRA = re.compile(
    "|".join(f"(?P<{nombre}>{patron})" for nombre, patron in PATRONES),
    re.DOTALL,
)


def tokenizar(codigo: str) -> list:
    """
    Tokeniza el código fuente ClaudioComp.
    Retorna una lista de Token; los comentarios y espacios se descartan.
    Al final siempre hay un token EOF.
    """
    tokens = []
    linea = 1

    for m in REGEX_MAESTRA.finditer(codigo):
        tipo = m.lastgroup
        valor = m.group()

        # Actualizar número de línea en comentarios de bloque y saltos
        if tipo == "COMENTARIO_BLOQUE":
            linea += valor.count("\n")
            continue
        if tipo == "COMENTARIO_LINEA":
            continue
        if tipo == "NUEVA_LINEA":
            linea += 1
            continue
        if tipo == "ESPACIO":
            continue

        # Clasificar identificadores vs palabras reservadas
        if tipo == "IDENT":
            tipo = PALABRAS_RESERVADAS.get(valor, "IDENT")

        tokens.append(Token(tipo=tipo, valor=valor, linea=linea))

    tokens.append(Token(tipo="EOF", valor="", linea=linea))
    return tokens
