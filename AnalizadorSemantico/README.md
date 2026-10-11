# Analizador Semántico — ClaudioComp

**Autor:** Manuel Claudio Hernandez  
**Matrícula:** 2-21-0644  
**Proyecto:** Compilador ClaudioComp — Fase 3: Análisis Semántico

---

## Descripción

Este proyecto implementa el **Analizador Semántico** para el lenguaje de programación ClaudioComp,
continuando el trabajo de los proyectos anteriores (Analizador Léxico y Analizador Sintáctico).

A diferencia de las fases anteriores (que usaban FLEX y Bison compilados en C), este analizador
está implementado **completamente en Python puro**, lo que elimina la necesidad de herramientas
externas de compilación y facilita su distribución y ejecución en cualquier máquina con Windows
que tenga Python instalado.

El analizador semántico verifica que el código fuente ClaudioComp sea correcto a nivel de
significado: tipos de variables, usos válidos de operadores, declaraciones duplicadas, etc.

---

## Requisitos

- **Python 3.8 o superior** (con `tkinter` incluido, que viene por defecto en la instalación estándar de Python para Windows)
- No se requiere instalar ninguna librería adicional.
- No es necesario compilar nada.

---

## Cómo ejecutar

### Opción 1 — Doble clic

Ejecuta `Ejecutar.bat` con doble clic desde el Explorador de Windows.

### Opción 2 — Terminal

```bash
cd c:\Users\manue\Downloads\Compilador\AnalizadorSemantico
python main.py
```

---

## Cómo ejecutar las pruebas

```bash
cd c:\Users\manue\Downloads\Compilador\AnalizadorSemantico
python tests/test_semantico.py
```

El script ejecuta 10 pruebas y muestra un resumen con PASS/FAIL.

---

## Estructura del proyecto

```
AnalizadorSemantico/
├── main.py                    # Interfaz gráfica tkinter
├── src/
│   ├── lexer.py               # Tokenizador Python para ClaudioComp
│   ├── parser.py              # Parser recursivo descendente → AST
│   └── semantic.py            # Analizador semántico + tabla de símbolos
├── examples/
│   ├── ejemplo_correcto.claudio   # Programa sin errores
│   └── ejemplo_errores.claudio    # Programa con errores semánticos
├── tests/
│   └── test_semantico.py          # Suite de 10 pruebas automáticas
├── docs/
│   └── Lenguaje_ClaudioComp.md    # Documentación del lenguaje
├── Ejecutar.bat               # Lanzador de la interfaz gráfica
└── README.md                  # Este archivo
```

---

## Por qué Python puro (sin FLEX/Bison)

Los analizadores léxico y sintáctico de las fases anteriores usaban herramientas de compilación
(FLEX, Bison, GCC) que requieren configurar el entorno de desarrollo en cada máquina. Para el
analizador semántico se optó por una implementación en Python puro por las siguientes razones:

1. **Portabilidad**: Funciona en cualquier PC con Python instalado, sin configuración adicional.
2. **Distribución sencilla**: No se necesita compilar ni instalar compiladores C.
3. **Mantenibilidad**: El código es más fácil de leer, modificar y extender.
4. **Integración con la GUI**: La interfaz tkinter puede importar directamente los módulos Python.

---

## Errores semánticos que detecta

| Error | Ejemplo |
|-------|---------|
| Variable no declarada | `y = 5;` (sin declarar `y`) |
| Declaración duplicada | `int x = 1; int x = 2;` |
| Tipo incompatible en asignación | `int x = 5; x = "hola";` |
| Operación aritmética inválida | `int z = x + flag;` (flag es bool) |
| Operación lógica inválida | `bool r = a && b;` (a, b son int) |
| Comparación de tipos incompatibles | `bool r = x == "texto";` (x es int) |
| Negación booleana inválida | `bool r = !x;` (x es int) |
| String en operación aritmética | `int r = texto + 5;` |

---

## Reglas semánticas del lenguaje

- Las operaciones `+`, `-`, `*`, `/` solo se permiten entre valores `int` y `float`.
- Los operadores `&&`, `||`, `!` solo se permiten con valores `bool`.
- Los comparadores (`==`, `!=`, `>`, `<`, etc.) requieren que ambos operandos sean del mismo tipo o ambos numéricos.
- Las variables deben declararse antes de usarse.
- No se puede declarar la misma variable dos veces en el mismo ámbito.
- Los bloques `if` y `while` crean un nuevo ámbito; las variables declaradas dentro no son visibles fuera.
