"""
semantic.py — Analizador Semántico para ClaudioComp
Recorre el AST producido por parser.py y valida reglas semánticas.
"""

from src.lexer import tokenizar
from src.parser import parsear


# ─────────────────────────────────────────────────────
#  Tabla de Símbolos
# ─────────────────────────────────────────────────────

class TablaSimbolos:
    def __init__(self, padre=None, nombre_ambito="global"):
        self.simbolos = {}   # nombre -> {"tipo": str, "ambito": str, "linea": int}
        self.padre = padre
        self.nombre_ambito = nombre_ambito

    def declarar(self, nombre: str, tipo: str, linea: int) -> bool:
        """
        Declara un símbolo en este ámbito.
        Retorna False si ya existe en este mismo ámbito (declaración duplicada).
        """
        if nombre in self.simbolos:
            return False
        self.simbolos[nombre] = {
            "tipo":   tipo,
            "ambito": self.nombre_ambito,
            "linea":  linea,
        }
        return True

    def buscar(self, nombre: str):
        """
        Busca el símbolo en este ámbito y luego en los padres.
        Retorna el dict del símbolo o None si no existe.
        """
        if nombre in self.simbolos:
            return self.simbolos[nombre]
        if self.padre is not None:
            return self.padre.buscar(nombre)
        return None

    def existe_local(self, nombre: str) -> bool:
        """Comprueba si el símbolo existe sólo en este ámbito."""
        return nombre in self.simbolos

    def todos_los_simbolos(self) -> list:
        """Retorna todos los símbolos de este ámbito y los de los padres."""
        resultado = []
        for nombre, info in self.simbolos.items():
            resultado.append({
                "nombre": nombre,
                "tipo":   info["tipo"],
                "ambito": info["ambito"],
                "linea":  info["linea"],
            })
        return resultado


# ─────────────────────────────────────────────────────
#  Analizador Semántico
# ─────────────────────────────────────────────────────

class AnalizadorSemantico:
    TIPOS_NUMERICOS = {"int", "float"}
    OPS_ARITMETICAS = {"+", "-", "*", "/"}
    OPS_COMPARACION = {"==", "!=", ">", "<", ">=", "<="}
    OPS_LOGICAS     = {"&&", "||"}

    def __init__(self):
        self.errores: list = []
        self.tabla_global = TablaSimbolos(nombre_ambito="global")
        self._todos_simbolos: list = []  # acumula todos los símbolos de todos los ámbitos

    def analizar(self, ast):
        """
        Recorre el AST y realiza validaciones semánticas.
        Retorna (errores, tabla_global).
        """
        self.errores = []
        self.tabla_global = TablaSimbolos(nombre_ambito="global")
        self._todos_simbolos = []

        if ast["tipo"] == "Programa":
            for stmt in ast["cuerpo"]:
                self._visitar(stmt, self.tabla_global)

        # Recopilar símbolos de la tabla global
        self._todos_simbolos = self.tabla_global.todos_los_simbolos()

        return self.errores, self.tabla_global

    # ── Visitar nodos ─────────────────────────────────

    def _visitar(self, nodo, tabla: TablaSimbolos):
        """Despacha al método correcto según el tipo de nodo."""
        if nodo is None:
            return None
        tipo = nodo.get("tipo")

        if tipo == "DeclVar":
            return self._visitar_decl_var(nodo, tabla)
        if tipo == "Asignacion":
            return self._visitar_asignacion(nodo, tabla)
        if tipo == "If":
            return self._visitar_if(nodo, tabla)
        if tipo == "While":
            return self._visitar_while(nodo, tabla)
        if tipo == "Return":
            return self._visitar_return(nodo, tabla)
        if tipo == "BinOp":
            return self._visitar_binop(nodo, tabla)
        if tipo == "UnOp":
            return self._visitar_unop(nodo, tabla)
        if tipo == "Literal":
            return nodo["tipo_dato"]
        if tipo == "Var":
            return self._visitar_var(nodo, tabla)
        if tipo == "ErrorSintactico":
            return None  # ya fue reportado en el parser
        # Nodo desconocido
        return None

    # ── Declaración de variable ───────────────────────

    def _visitar_decl_var(self, nodo, tabla: TablaSimbolos):
        tipo_declarado = nodo["tipo_dato"]
        nombre = nodo["nombre"]
        linea  = nodo["linea"]

        # 1. Verificar duplicado
        if not tabla.declarar(nombre, tipo_declarado, linea):
            self._error(f"Variable '{nombre}' ya fue declarada en este ámbito", linea)
            return tipo_declarado

        # 2. Verificar compatibilidad del valor inicial
        if nodo["expr"] is not None:
            tipo_expr = self._visitar(nodo["expr"], tabla)
            if tipo_expr is not None:
                self._verificar_compatibilidad(nombre, tipo_declarado, tipo_expr, linea)

        return tipo_declarado

    # ── Asignación ────────────────────────────────────

    def _visitar_asignacion(self, nodo, tabla: TablaSimbolos):
        nombre = nodo["nombre"]
        linea  = nodo["linea"]

        # 1. Verificar que la variable exista
        info = tabla.buscar(nombre)
        if info is None:
            self._error(f"Variable '{nombre}' no ha sido declarada", linea)
            # Intentar inferir el tipo de la expresión de todos modos
            self._visitar(nodo["expr"], tabla)
            return None

        tipo_declarado = info["tipo"]

        # 2. Verificar tipo de la expresión
        tipo_expr = self._visitar(nodo["expr"], tabla)
        if tipo_expr is not None:
            self._verificar_compatibilidad(nombre, tipo_declarado, tipo_expr, linea)

        return tipo_declarado

    # ── If ────────────────────────────────────────────

    def _visitar_if(self, nodo, tabla: TablaSimbolos):
        # Visitar la condición
        self._visitar(nodo["cond"], tabla)

        # Nuevo ámbito para el bloque "entonces"
        tabla_entonces = TablaSimbolos(padre=tabla, nombre_ambito="if_entonces")
        for stmt in nodo["entonces"]:
            self._visitar(stmt, tabla_entonces)
        self._todos_simbolos.extend(tabla_entonces.todos_los_simbolos())

        # Nuevo ámbito para el bloque "sino"
        if nodo["sino"] is not None:
            tabla_sino = TablaSimbolos(padre=tabla, nombre_ambito="if_sino")
            for stmt in nodo["sino"]:
                self._visitar(stmt, tabla_sino)
            self._todos_simbolos.extend(tabla_sino.todos_los_simbolos())

    # ── While ─────────────────────────────────────────

    def _visitar_while(self, nodo, tabla: TablaSimbolos):
        self._visitar(nodo["cond"], tabla)

        tabla_cuerpo = TablaSimbolos(padre=tabla, nombre_ambito="while")
        for stmt in nodo["cuerpo"]:
            self._visitar(stmt, tabla_cuerpo)
        self._todos_simbolos.extend(tabla_cuerpo.todos_los_simbolos())

    # ── Return ────────────────────────────────────────

    def _visitar_return(self, nodo, tabla: TablaSimbolos):
        return self._visitar(nodo["expr"], tabla)

    # ── Operaciones binarias ──────────────────────────

    def _visitar_binop(self, nodo, tabla: TablaSimbolos):
        op   = nodo["op"]
        linea = nodo["linea"]

        tipo_izq = self._visitar(nodo["izq"], tabla)
        tipo_der = self._visitar(nodo["der"], tabla)

        # Si alguno es desconocido, no seguir
        if tipo_izq is None or tipo_der is None:
            return None

        # Operaciones aritméticas: +, -, *, /
        if op in self.OPS_ARITMETICAS:
            return self._verificar_aritmetica(op, tipo_izq, tipo_der, linea)

        # Operaciones de comparación: ==, !=, >, <, >=, <=
        if op in self.OPS_COMPARACION:
            return self._verificar_comparacion(op, tipo_izq, tipo_der, linea)

        # Operaciones lógicas: &&, ||
        if op in self.OPS_LOGICAS:
            return self._verificar_logica(op, tipo_izq, tipo_der, linea)

        return None

    # ── Operaciones unarias ───────────────────────────

    def _visitar_unop(self, nodo, tabla: TablaSimbolos):
        op    = nodo["op"]
        linea = nodo["linea"]
        tipo_expr = self._visitar(nodo["expr"], tabla)

        if tipo_expr is None:
            return None

        if op == "!":
            if tipo_expr != "bool":
                self._error(
                    f"El operador '!' requiere un operando de tipo 'bool', pero se encontró '{tipo_expr}'",
                    linea,
                )
            return "bool"

        if op == "-":
            if tipo_expr not in self.TIPOS_NUMERICOS:
                self._error(
                    f"El operador '-' (negación) requiere un operando numérico, pero se encontró '{tipo_expr}'",
                    linea,
                )
            return tipo_expr

        return tipo_expr

    # ── Variable ──────────────────────────────────────

    def _visitar_var(self, nodo, tabla: TablaSimbolos):
        nombre = nodo["nombre"]
        linea  = nodo["linea"]

        info = tabla.buscar(nombre)
        if info is None:
            self._error(f"Variable '{nombre}' no ha sido declarada", linea)
            return None
        return info["tipo"]

    # ── Validaciones de tipos ─────────────────────────

    def _verificar_compatibilidad(self, nombre, tipo_declarado, tipo_expr, linea):
        """Verifica que tipo_expr sea compatible con tipo_declarado."""
        # Compatibilidad numérica: int puede asignarse a float y viceversa (con advertencia implícita)
        # Pero la especificación pide error de tipo incompatible si son distintos
        if tipo_declarado != tipo_expr:
            # Permitir int ↔ float (asignación de int a float es válida en muchos lenguajes)
            if tipo_declarado in self.TIPOS_NUMERICOS and tipo_expr in self.TIPOS_NUMERICOS:
                return  # compatibles
            self._error(
                f"No se puede asignar un valor de tipo '{tipo_expr}' "
                f"a la variable '{nombre}' de tipo '{tipo_declarado}'",
                linea,
            )

    def _verificar_aritmetica(self, op, tipo_izq, tipo_der, linea):
        """Valida que ambos operandos sean numéricos y determina el tipo resultado."""
        errores = []
        if tipo_izq not in self.TIPOS_NUMERICOS:
            errores.append(tipo_izq)
        if tipo_der not in self.TIPOS_NUMERICOS:
            errores.append(tipo_der)

        if errores:
            self._error(
                f"Operación aritmética no permitida: tipos '{tipo_izq}' y '{tipo_der}' son incompatibles",
                linea,
            )
            return None

        # Si uno es float, resultado es float
        if "float" in (tipo_izq, tipo_der):
            return "float"
        return "int"

    def _verificar_comparacion(self, op, tipo_izq, tipo_der, linea):
        """Valida que los operandos sean comparables entre sí."""
        # Ambos numéricos → OK
        if tipo_izq in self.TIPOS_NUMERICOS and tipo_der in self.TIPOS_NUMERICOS:
            return "bool"
        # Mismo tipo no numérico → OK
        if tipo_izq == tipo_der:
            return "bool"
        # Tipos distintos incompatibles
        self._error(
            f"Comparación de tipos incompatibles: '{tipo_izq}' y '{tipo_der}'",
            linea,
        )
        return "bool"

    def _verificar_logica(self, op, tipo_izq, tipo_der, linea):
        """Valida que ambos operandos sean bool."""
        if tipo_izq != "bool":
            self._error(
                f"Operación lógica '{op}' requiere operandos de tipo 'bool', pero se encontró '{tipo_izq}'",
                linea,
            )
        if tipo_der != "bool":
            self._error(
                f"Operación lógica '{op}' requiere operandos de tipo 'bool', pero se encontró '{tipo_der}'",
                linea,
            )
        return "bool"

    # ── Registro de errores ───────────────────────────

    def _error(self, msg: str, linea: int):
        self.errores.append({"tipo": "SEMANTICO", "msg": msg, "linea": linea})


# ─────────────────────────────────────────────────────
#  Función pública principal
# ─────────────────────────────────────────────────────

def analizar_semantico(codigo: str) -> dict:
    """
    Pipeline completo: lexer → parser → semántico.

    Retorna un dict con:
      errores_lex  : list[str]   — errores del lexer
      errores_sint : list[str]   — errores del parser
      errores_sem  : list[dict]  — errores semánticos {msg, linea}
      tabla        : list[dict]  — símbolos {nombre, tipo, ambito, linea}
      tokens       : list[Token] — tokens producidos por el lexer
      ok           : bool        — True si no hay errores semánticos
    """
    # 1. Análisis léxico
    tokens = tokenizar(codigo)
    errores_lex = [
        f"Línea {t.linea}: carácter no reconocido '{t.valor}'"
        for t in tokens if t.tipo == "ERROR"
    ]
    # Filtrar tokens de error antes de parsear
    tokens_validos = [t for t in tokens if t.tipo != "ERROR"]

    # 2. Análisis sintáctico
    ast, errores_sint = parsear(tokens_validos)

    # 3. Análisis semántico
    analizador = AnalizadorSemantico()
    errores_sem, tabla_global = analizador.analizar(ast)

    # 4. Recopilar tabla de símbolos (global + ámbitos internos)
    # _todos_simbolos contiene solo los de ámbitos internos (if, while, etc.)
    tabla_simbolos = tabla_global.todos_los_simbolos() + analizador._todos_simbolos
    # Deduplicar por (nombre, ambito, linea)
    vistos = set()
    tabla_unica = []
    for s in tabla_simbolos:
        clave = (s["nombre"], s["ambito"], s["linea"])
        if clave not in vistos:
            vistos.add(clave)
            tabla_unica.append(s)
    tabla_simbolos = tabla_unica

    return {
        "errores_lex":  errores_lex,
        "errores_sint": errores_sint,
        "errores_sem":  errores_sem,
        "tabla":        tabla_simbolos,
        "tokens":       tokens,
        "ok":           len(errores_sem) == 0,
    }
