"""
parser.py — Parser recursivo descendente para ClaudioComp
Produce un AST (árbol de nodos dict) y acumula errores sin lanzar excepciones.
"""

from src.lexer import tokenizar


# ─────────────────────────────────────────────────────
#  Helpers para construir nodos del AST
# ─────────────────────────────────────────────────────

def nodo_programa(cuerpo):
    return {"tipo": "Programa", "cuerpo": cuerpo}

def nodo_decl_var(tipo_dato, nombre, expr, linea):
    return {"tipo": "DeclVar", "tipo_dato": tipo_dato, "nombre": nombre, "expr": expr, "linea": linea}

def nodo_asignacion(nombre, expr, linea):
    return {"tipo": "Asignacion", "nombre": nombre, "expr": expr, "linea": linea}

def nodo_if(cond, entonces, sino, linea):
    return {"tipo": "If", "cond": cond, "entonces": entonces, "sino": sino, "linea": linea}

def nodo_while(cond, cuerpo, linea):
    return {"tipo": "While", "cond": cond, "cuerpo": cuerpo, "linea": linea}

def nodo_return(expr, linea):
    return {"tipo": "Return", "expr": expr, "linea": linea}

def nodo_binop(op, izq, der, linea):
    return {"tipo": "BinOp", "op": op, "izq": izq, "der": der, "linea": linea}

def nodo_unop(op, expr, linea):
    return {"tipo": "UnOp", "op": op, "expr": expr, "linea": linea}

def nodo_literal(tipo_dato, valor, linea):
    return {"tipo": "Literal", "tipo_dato": tipo_dato, "valor": valor, "linea": linea}

def nodo_var(nombre, linea):
    return {"tipo": "Var", "nombre": nombre, "linea": linea}

def nodo_error(msg, linea):
    return {"tipo": "ErrorSintactico", "msg": msg, "linea": linea}


# ─────────────────────────────────────────────────────
#  Clase Parser
# ─────────────────────────────────────────────────────

class Parser:
    TIPOS = {"INT", "FLOAT_T", "STRING_T", "BOOL_T"}

    # Mapa de tipo-token → nombre de tipo de dato
    TIPO_MAP = {
        "INT":     "int",
        "FLOAT_T": "float",
        "STRING_T": "string",
        "BOOL_T":  "bool",
    }

    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0
        self.errores = []

    # ── Primitivas ────────────────────────────────────

    def actual(self):
        return self.tokens[self.pos]

    def avanzar(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def consumir(self, tipo_esperado):
        tok = self.actual()
        if tok.tipo == tipo_esperado:
            return self.avanzar()
        self.errores.append(
            f"Línea {tok.linea}: se esperaba '{tipo_esperado}' pero se encontró '{tok.valor}'"
        )
        return tok  # devuelve el token actual sin avanzar para recuperación

    def es_tipo(self):
        return self.actual().tipo in self.TIPOS

    def fin(self):
        return self.actual().tipo == "EOF"

    # ── Punto de entrada ──────────────────────────────

    def parsear_programa(self):
        cuerpo = []
        while not self.fin():
            stmt = self.parsear_sentencia()
            if stmt is not None:
                cuerpo.append(stmt)
        return nodo_programa(cuerpo)

    # ── Sentencias ────────────────────────────────────

    def parsear_sentencia(self):
        tok = self.actual()

        if self.es_tipo():
            return self.parsear_decl_var()

        if tok.tipo in ("IF", "HILUX"):
            return self.parsear_if()

        if tok.tipo == "WHILE":
            return self.parsear_while()

        if tok.tipo == "RETURN":
            return self.parsear_return()

        if tok.tipo == "IDENT":
            # Puede ser asignación: IDENT = expr ;
            siguiente = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if siguiente and siguiente.tipo == "ASIGN":
                return self.parsear_asignacion()

        # Error de recuperación: consumir hasta ';' o '}'
        linea = tok.linea
        msg = f"Línea {linea}: sentencia no reconocida: '{tok.valor}'"
        self.errores.append(msg)
        # Avanzar hasta encontrar ';', '}' o EOF
        while not self.fin() and self.actual().tipo not in ("PCOMA", "LLAVE_C"):
            self.avanzar()
        if self.actual().tipo == "PCOMA":
            self.avanzar()
        return nodo_error(msg, linea)

    # ── Declaración de variable ───────────────────────

    def parsear_decl_var(self):
        tok_tipo = self.avanzar()
        tipo_dato = self.TIPO_MAP[tok_tipo.tipo]
        linea = tok_tipo.linea

        tok_nombre = self.actual()
        if tok_nombre.tipo != "IDENT":
            msg = f"Línea {linea}: se esperaba nombre de variable"
            self.errores.append(msg)
            self._recuperar_hasta_pcoma()
            return nodo_error(msg, linea)

        nombre = tok_nombre.valor
        self.avanzar()

        if self.actual().tipo == "ASIGN":
            self.avanzar()
            expr = self.parsear_expresion()
            self._consumir_pcoma()
            return nodo_decl_var(tipo_dato, nombre, expr, linea)
        elif self.actual().tipo == "PCOMA":
            self.avanzar()
            return nodo_decl_var(tipo_dato, nombre, None, linea)
        else:
            msg = f"Línea {linea}: se esperaba '=' o ';' después del nombre de variable"
            self.errores.append(msg)
            self._recuperar_hasta_pcoma()
            return nodo_error(msg, linea)

    # ── Asignación ────────────────────────────────────

    def parsear_asignacion(self):
        tok_nombre = self.avanzar()
        nombre = tok_nombre.valor
        linea = tok_nombre.linea
        self.avanzar()  # consume '='
        expr = self.parsear_expresion()
        self._consumir_pcoma()
        return nodo_asignacion(nombre, expr, linea)

    # ── If / Hilux ────────────────────────────────────

    def parsear_if(self):
        tok = self.avanzar()
        linea = tok.linea

        if self.actual().tipo != "PAREN_A":
            msg = f"Línea {linea}: se esperaba '(' después de '{tok.valor}'"
            self.errores.append(msg)
        else:
            self.avanzar()

        cond = self.parsear_expresion()

        if self.actual().tipo != "PAREN_C":
            self.errores.append(f"Línea {linea}: se esperaba ')' para cerrar condición del if")
        else:
            self.avanzar()

        entonces = self.parsear_bloque()
        sino = None

        if self.actual().tipo == "ELSE":
            self.avanzar()
            sino = self.parsear_bloque()

        return nodo_if(cond, entonces, sino, linea)

    # ── While ─────────────────────────────────────────

    def parsear_while(self):
        tok = self.avanzar()
        linea = tok.linea

        if self.actual().tipo != "PAREN_A":
            self.errores.append(f"Línea {linea}: se esperaba '(' después de 'while'")
        else:
            self.avanzar()

        cond = self.parsear_expresion()

        if self.actual().tipo != "PAREN_C":
            self.errores.append(f"Línea {linea}: se esperaba ')' para cerrar condición del while")
        else:
            self.avanzar()

        cuerpo = self.parsear_bloque()
        return nodo_while(cond, cuerpo, linea)

    # ── Return ────────────────────────────────────────

    def parsear_return(self):
        tok = self.avanzar()
        linea = tok.linea
        expr = self.parsear_expresion()
        self._consumir_pcoma()
        return nodo_return(expr, linea)

    # ── Bloque ────────────────────────────────────────

    def parsear_bloque(self):
        sentencias = []
        if self.actual().tipo != "LLAVE_A":
            self.errores.append(f"Línea {self.actual().linea}: se esperaba '{{'")
            return sentencias
        self.avanzar()

        while not self.fin() and self.actual().tipo != "LLAVE_C":
            stmt = self.parsear_sentencia()
            if stmt is not None:
                sentencias.append(stmt)

        if self.actual().tipo == "LLAVE_C":
            self.avanzar()
        else:
            self.errores.append(f"Línea {self.actual().linea}: se esperaba '}}'")

        return sentencias

    # ── Expresiones (precedencia de operadores) ───────
    #  Nivel 0 (menor precedencia): OR
    #  Nivel 1: AND
    #  Nivel 2: ==, !=
    #  Nivel 3: >, <, >=, <=
    #  Nivel 4: +, -
    #  Nivel 5: *, /
    #  Nivel 6 (mayor): unarios !

    def parsear_expresion(self):
        return self._parsear_or()

    def _parsear_or(self):
        izq = self._parsear_and()
        while self.actual().tipo == "OR":
            tok = self.avanzar()
            der = self._parsear_and()
            izq = nodo_binop("||", izq, der, tok.linea)
        return izq

    def _parsear_and(self):
        izq = self._parsear_igualdad()
        while self.actual().tipo == "AND":
            tok = self.avanzar()
            der = self._parsear_igualdad()
            izq = nodo_binop("&&", izq, der, tok.linea)
        return izq

    def _parsear_igualdad(self):
        izq = self._parsear_relacional()
        while self.actual().tipo in ("IGUAL", "DIFERENTE"):
            tok = self.avanzar()
            der = self._parsear_relacional()
            izq = nodo_binop(tok.valor, izq, der, tok.linea)
        return izq

    def _parsear_relacional(self):
        izq = self._parsear_suma()
        while self.actual().tipo in ("MAYOR", "MENOR", "MAYOR_IGUAL", "MENOR_IGUAL"):
            tok = self.avanzar()
            der = self._parsear_suma()
            izq = nodo_binop(tok.valor, izq, der, tok.linea)
        return izq

    def _parsear_suma(self):
        izq = self._parsear_mult()
        while self.actual().tipo in ("SUMA", "RESTA"):
            tok = self.avanzar()
            der = self._parsear_mult()
            izq = nodo_binop(tok.valor, izq, der, tok.linea)
        return izq

    def _parsear_mult(self):
        izq = self._parsear_unario()
        while self.actual().tipo in ("MULT", "DIV"):
            tok = self.avanzar()
            der = self._parsear_unario()
            izq = nodo_binop(tok.valor, izq, der, tok.linea)
        return izq

    def _parsear_unario(self):
        tok = self.actual()
        if tok.tipo == "NOT":
            self.avanzar()
            expr = self._parsear_unario()
            return nodo_unop("!", expr, tok.linea)
        if tok.tipo == "RESTA":
            self.avanzar()
            expr = self._parsear_unario()
            return nodo_unop("-", expr, tok.linea)
        return self._parsear_primario()

    def _parsear_primario(self):
        tok = self.actual()

        if tok.tipo == "NUM_INT":
            self.avanzar()
            return nodo_literal("int", tok.valor, tok.linea)

        if tok.tipo == "NUM_FLOAT":
            self.avanzar()
            return nodo_literal("float", tok.valor, tok.linea)

        if tok.tipo == "CADENA":
            self.avanzar()
            return nodo_literal("string", tok.valor, tok.linea)

        if tok.tipo == "TRUE":
            self.avanzar()
            return nodo_literal("bool", "true", tok.linea)

        if tok.tipo == "FALSE":
            self.avanzar()
            return nodo_literal("bool", "false", tok.linea)

        if tok.tipo == "IDENT":
            self.avanzar()
            return nodo_var(tok.valor, tok.linea)

        if tok.tipo == "PAREN_A":
            self.avanzar()
            expr = self.parsear_expresion()
            if self.actual().tipo == "PAREN_C":
                self.avanzar()
            else:
                self.errores.append(f"Línea {tok.linea}: se esperaba ')' para cerrar expresión")
            return expr

        # Error: token no esperado en expresión
        msg = f"Línea {tok.linea}: token inesperado '{tok.valor}' en expresión"
        self.errores.append(msg)
        # No avanzamos para no perder el token
        return nodo_error(msg, tok.linea)

    # ── Utilidades ────────────────────────────────────

    def _consumir_pcoma(self):
        if self.actual().tipo == "PCOMA":
            self.avanzar()
        else:
            self.errores.append(
                f"Línea {self.actual().linea}: se esperaba ';' al final de la sentencia"
            )

    def _recuperar_hasta_pcoma(self):
        while not self.fin() and self.actual().tipo not in ("PCOMA", "LLAVE_C"):
            self.avanzar()
        if self.actual().tipo == "PCOMA":
            self.avanzar()


# ─────────────────────────────────────────────────────
#  Función pública
# ─────────────────────────────────────────────────────

def parsear(tokens: list):
    """
    Recibe la lista de tokens del lexer y retorna:
      (nodo_programa, errores_sintacticos: list[str])
    """
    p = Parser(tokens)
    ast = p.parsear_programa()
    return ast, p.errores
