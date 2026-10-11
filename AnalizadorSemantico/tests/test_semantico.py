"""
test_semantico.py — Pruebas para el Analizador Semántico de ClaudioComp
Ejecutar desde la raíz del proyecto: python tests/test_semantico.py
"""

import sys
import os

# Asegurarse de que la raíz del proyecto esté en el path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.semantic import analizar_semantico

# ─── Contadores de resultados ─────────────────────────────────────────────────
_pasadas = 0
_falladas = 0


def afirmar(condicion: bool, descripcion: str):
    """Evalúa una condición y muestra PASS o FAIL."""
    global _pasadas, _falladas
    if condicion:
        print(f"  ✅ PASS — {descripcion}")
        _pasadas += 1
    else:
        print(f"  ❌ FAIL — {descripcion}")
        _falladas += 1


# ─── Pruebas individuales ─────────────────────────────────────────────────────

def test_programa_correcto():
    """Código válido no debe producir errores semánticos."""
    print("\n[1] test_programa_correcto")
    codigo = """
    int x = 10;
    float y = 3.14;
    bool flag = true;
    string msg = "hola";
    x = x + 5;
    y = y * 2.0;
    """
    r = analizar_semantico(codigo)
    afirmar(r["ok"], "Sin errores semánticos en código correcto")
    afirmar(len(r["errores_sem"]) == 0, "Lista de errores semánticos vacía")


def test_variable_no_declarada():
    """Usar una variable sin declarar debe producir exactamente 1 error."""
    print("\n[2] test_variable_no_declarada")
    codigo = """
    int x = 5;
    y = 10;
    """
    r = analizar_semantico(codigo)
    afirmar(not r["ok"], "Detectó error semántico")
    afirmar(len(r["errores_sem"]) >= 1, "Al menos 1 error semántico")
    msgs = [e["msg"] for e in r["errores_sem"]]
    afirmar(any("y" in m and "declarada" in m for m in msgs),
            "Error menciona variable 'y' no declarada")


def test_declaracion_duplicada():
    """Declarar la misma variable dos veces debe producir 1 error."""
    print("\n[3] test_declaracion_duplicada")
    codigo = """
    int x = 10;
    int x = 20;
    """
    r = analizar_semantico(codigo)
    afirmar(not r["ok"], "Detectó error semántico")
    afirmar(len(r["errores_sem"]) >= 1, "Al menos 1 error semántico")
    msgs = [e["msg"] for e in r["errores_sem"]]
    afirmar(any("x" in m and ("declarada" in m or "ámbito" in m) for m in msgs),
            "Error menciona variable 'x' duplicada")


def test_tipo_incompatible_asignacion():
    """Asignar un string a una variable int debe ser un error."""
    print("\n[4] test_tipo_incompatible_asignacion")
    codigo = """
    int numero = 5;
    numero = "texto";
    """
    r = analizar_semantico(codigo)
    afirmar(not r["ok"], "Detectó error semántico")
    msgs = [e["msg"] for e in r["errores_sem"]]
    afirmar(any("string" in m and "int" in m for m in msgs),
            "Error menciona incompatibilidad string→int")


def test_operacion_aritmetica_invalida():
    """Sumar int con bool debe generar error aritmético."""
    print("\n[5] test_operacion_aritmetica_invalida")
    codigo = """
    int x = 10;
    bool flag = true;
    int z = x + flag;
    """
    r = analizar_semantico(codigo)
    afirmar(not r["ok"], "Detectó error semántico")
    msgs = [e["msg"] for e in r["errores_sem"]]
    afirmar(any("aritmética" in m or "aritmetica" in m.lower() for m in msgs),
            "Error menciona operación aritmética inválida")


def test_tabla_de_simbolos():
    """La tabla de símbolos debe contener exactamente los símbolos declarados."""
    print("\n[6] test_tabla_de_simbolos")
    codigo = """
    int contador = 0;
    float precio = 9.99;
    bool activo = true;
    string nombre = "test";
    """
    r = analizar_semantico(codigo)
    nombres = {s["nombre"] for s in r["tabla"]}
    afirmar("contador" in nombres, "Símbolo 'contador' en tabla")
    afirmar("precio"   in nombres, "Símbolo 'precio' en tabla")
    afirmar("activo"   in nombres, "Símbolo 'activo' en tabla")
    afirmar("nombre"   in nombres, "Símbolo 'nombre' en tabla")
    # Verificar tipos
    tipos = {s["nombre"]: s["tipo"] for s in r["tabla"]}
    afirmar(tipos.get("contador") == "int",    "Tipo de 'contador' es int")
    afirmar(tipos.get("precio")   == "float",  "Tipo de 'precio' es float")
    afirmar(tipos.get("activo")   == "bool",   "Tipo de 'activo' es bool")
    afirmar(tipos.get("nombre")   == "string", "Tipo de 'nombre' es string")


def test_multiples_errores():
    """Código con 3+ errores: todos deben ser detectados."""
    print("\n[7] test_multiples_errores")
    codigo = """
    int x = 10;
    int x = 20;
    string nombre = "Hola";
    bool flag = true;
    y = 5;
    x = nombre;
    """
    r = analizar_semantico(codigo)
    afirmar(not r["ok"], "Detectó al menos un error")
    afirmar(len(r["errores_sem"]) >= 3,
            f"Al menos 3 errores semánticos (encontrados: {len(r['errores_sem'])})")


def test_ambito():
    """Variables declaradas dentro de un if no deben ser visibles fuera."""
    print("\n[8] test_ambito")
    codigo = """
    int x = 1;
    bool flag = true;
    if (flag) {
        int local_var = 99;
    }
    local_var = 5;
    """
    r = analizar_semantico(codigo)
    # 'local_var' no debe estar declarada en el ámbito global
    msgs = [e["msg"] for e in r["errores_sem"]]
    afirmar(any("local_var" in m and "declarada" in m for m in msgs),
            "Error: 'local_var' no accesible fuera del bloque if")


def test_operacion_logica_invalida():
    """El operador && con operandos no bool debe generar error."""
    print("\n[9] test_operacion_logica_invalida")
    codigo = """
    int a = 1;
    int b = 2;
    bool resultado = a && b;
    """
    r = analizar_semantico(codigo)
    afirmar(not r["ok"], "Detectó error en operación lógica")
    msgs = [e["msg"] for e in r["errores_sem"]]
    afirmar(any("&&" in m or "lógica" in m.lower() or "logica" in m.lower() for m in msgs),
            "Error menciona operación lógica inválida")


def test_cadena_en_aritmetica():
    """Sumar string con int debe generar error aritmético."""
    print("\n[10] test_cadena_en_aritmetica")
    codigo = """
    string texto = "hola";
    int numero = 5;
    int resultado = texto + numero;
    """
    r = analizar_semantico(codigo)
    afirmar(not r["ok"], "Detectó error semántico")
    msgs = [e["msg"] for e in r["errores_sem"]]
    afirmar(any("string" in m or "aritmética" in m or "aritmetica" in m.lower()
                for m in msgs),
            "Error menciona tipo string en operación aritmética")


# ─── Punto de entrada ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  SUITE DE PRUEBAS — Analizador Semántico ClaudioComp")
    print("=" * 60)

    test_programa_correcto()
    test_variable_no_declarada()
    test_declaracion_duplicada()
    test_tipo_incompatible_asignacion()
    test_operacion_aritmetica_invalida()
    test_tabla_de_simbolos()
    test_multiples_errores()
    test_ambito()
    test_operacion_logica_invalida()
    test_cadena_en_aritmetica()

    print("\n" + "=" * 60)
    total = _pasadas + _falladas
    print(f"  RESUMEN: {_pasadas}/{total} pruebas pasaron")
    if _falladas == 0:
        print("  🎉 Todas las pruebas pasaron correctamente.")
    else:
        print(f"  ⚠  {_falladas} prueba(s) fallaron.")
    print("=" * 60)

    sys.exit(0 if _falladas == 0 else 1)
