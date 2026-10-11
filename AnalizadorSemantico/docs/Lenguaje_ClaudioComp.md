# Lenguaje ClaudioComp — Especificación y Reglas Semánticas

**Autor:** Manuel Claudio Hernandez  
**Matrícula:** 2-21-0644  
**Asignatura:** Compiladores  

---

## 1. Introducción

ClaudioComp es un lenguaje de programación de propósito educativo diseñado para ilustrar los
conceptos de compilación: análisis léxico, sintáctico y semántico. Su sintaxis es deliberadamente
simple e inspirada en lenguajes como C y Java, aunque incluye algunas características únicas como
la palabra reservada `hilux` (sinónimo de `if`).

Este documento describe el lenguaje desde el punto de vista de su análisis semántico: tipos de
datos, declaraciones, asignaciones, operadores, estructuras de control y las reglas que determinan
si un programa es semánticamente correcto.

---

## 2. Tipos de datos

ClaudioComp admite cuatro tipos de datos primitivos:

| Tipo     | Descripción                        | Ejemplo de literal |
|----------|------------------------------------|--------------------|
| `int`    | Número entero                      | `42`, `0`, `-7`    |
| `float`  | Número decimal de punto flotante   | `3.14`, `0.5`      |
| `string` | Cadena de texto entre comillas     | `"Hola mundo"`     |
| `bool`   | Valor booleano                     | `true`, `false`    |

No existe conversión implícita de tipos (excepto entre `int` y `float` en operaciones aritméticas).

---

## 3. Declaración de variables

Una variable debe declararse antes de usarse. La sintaxis es:

```
tipo identificador;
tipo identificador = expresion;
```

### Ejemplos

```claudiocomp
int edad;
float precio = 19.99;
bool activo = true;
string nombre = "Juan";
```

### Reglas

- El tipo debe ser uno de: `int`, `float`, `string`, `bool`.
- El identificador debe comenzar con letra o guión bajo, seguido de letras, dígitos o guiones bajos.
- No se puede declarar la misma variable dos veces en el mismo ámbito.
- La expresión de inicialización (si existe) debe ser compatible con el tipo declarado.

---

## 4. Asignaciones

Una variable ya declarada puede recibir un nuevo valor:

```
identificador = expresion;
```

### Ejemplos

```claudiocomp
edad = 25;
precio = precio * 1.1;
activo = false;
```

### Reglas

- La variable debe haber sido declarada previamente en el ámbito actual o en un ámbito padre.
- El tipo de la expresión debe ser compatible con el tipo de la variable.

---

## 5. Operadores

### 5.1 Operadores aritméticos

| Operador | Descripción      | Tipos válidos        | Tipo resultado |
|----------|------------------|----------------------|----------------|
| `+`      | Suma             | `int`, `float`       | `int` o `float` |
| `-`      | Resta            | `int`, `float`       | `int` o `float` |
| `*`      | Multiplicación   | `int`, `float`       | `int` o `float` |
| `/`      | División         | `int`, `float`       | `int` o `float` |

Regla de promoción: si uno de los operandos es `float`, el resultado es `float`. Si ambos son
`int`, el resultado es `int`. Los tipos `string` y `bool` **no** pueden usarse en operaciones
aritméticas.

### 5.2 Operadores relacionales

| Operador | Descripción         | Tipos válidos                      | Tipo resultado |
|----------|---------------------|------------------------------------|----------------|
| `==`     | Igual a             | Mismo tipo o ambos numéricos       | `bool`         |
| `!=`     | Diferente de        | Mismo tipo o ambos numéricos       | `bool`         |
| `>`      | Mayor que           | `int`, `float`                     | `bool`         |
| `<`      | Menor que           | `int`, `float`                     | `bool`         |
| `>=`     | Mayor o igual que   | `int`, `float`                     | `bool`         |
| `<=`     | Menor o igual que   | `int`, `float`                     | `bool`         |

### 5.3 Operadores lógicos

| Operador | Descripción     | Tipo válido | Tipo resultado |
|----------|-----------------|-------------|----------------|
| `&&`     | AND lógico      | `bool`      | `bool`         |
| `\|\|`   | OR lógico       | `bool`      | `bool`         |
| `!`      | Negación lógica | `bool`      | `bool`         |

Los operadores `&&`, `||` y `!` **solo** aceptan operandos de tipo `bool`.

---

## 6. Estructuras de control

### 6.1 if / hilux

```
if (condicion) {
    // bloque si la condición es verdadera
}

if (condicion) {
    // bloque verdadero
} else {
    // bloque falso
}
```

La palabra `hilux` es un alias de `if` y se comporta de manera idéntica:

```
hilux (activo) {
    precio = precio + 10.0;
}
```

### 6.2 while

```
while (condicion) {
    // cuerpo del ciclo
}
```

### Reglas de ámbito

Los bloques `if`, `hilux` y `while` crean un nuevo **ámbito** (scope). Las variables declaradas
dentro del bloque solo son visibles dentro de ese bloque y no pueden ser accedidas fuera de él.

```claudiocomp
int x = 1;
if (x > 0) {
    int y = 10;   // 'y' solo existe dentro de este bloque
}
y = 5;            // ERROR: 'y' no ha sido declarada en este ámbito
```

---

## 7. Comentarios

ClaudioComp admite dos estilos de comentarios:

```claudiocomp
// Comentario de una sola línea

/*
   Comentario
   de varias líneas
*/
```

Los comentarios son ignorados por el analizador léxico y no tienen efecto en el programa.

---

## 8. Reglas semánticas

Esta sección resume todas las reglas que el analizador semántico verifica:

### 8.1 Declaración antes de uso

Toda variable debe ser declarada antes de utilizarse. El uso de una variable no declarada
es un **error semántico**:

```claudiocomp
// ERROR: 'total' no ha sido declarada
total = 100;
```

### 8.2 Sin declaraciones duplicadas

No se puede declarar dos veces la misma variable en el mismo ámbito:

```claudiocomp
int x = 5;
int x = 10;   // ERROR: 'x' ya fue declarada en este ámbito
```

### 8.3 Compatibilidad de tipos en asignación

El tipo del valor asignado debe coincidir con el tipo declarado de la variable:

```claudiocomp
int numero = 5;
numero = "texto";   // ERROR: no se puede asignar string a int
```

Excepción: asignar un `int` a una variable `float` o viceversa está permitido, dado que
son tipos numéricos compatibles.

### 8.4 Tipos válidos en operaciones aritméticas

Las operaciones `+`, `-`, `*`, `/` solo son válidas con `int` y `float`:

```claudiocomp
bool flag = true;
int x = 5;
int z = x + flag;   // ERROR: tipos 'int' y 'bool' son incompatibles
```

### 8.5 Tipos válidos en operaciones lógicas

Los operadores `&&`, `||`, `!` solo aceptan `bool`:

```claudiocomp
int a = 1;
int b = 2;
bool r = a && b;   // ERROR: operandos deben ser bool
```

### 8.6 Comparación de tipos compatibles

No se pueden comparar tipos incompatibles entre sí:

```claudiocomp
int x = 5;
string s = "hola";
bool r = x == s;   // ERROR: tipos 'int' y 'string' incompatibles
```

---

## 9. Tabla de símbolos

La tabla de símbolos es una estructura de datos que el compilador mantiene durante el análisis
semántico. Su función es registrar cada variable declarada con su información asociada:

| Campo   | Descripción                                       |
|---------|---------------------------------------------------|
| nombre  | Identificador de la variable                      |
| tipo    | Tipo de dato (`int`, `float`, `string`, `bool`)   |
| ámbito  | Contexto donde fue declarada (`global`, `if`, etc.) |
| línea   | Número de línea de la declaración                 |

### Estructura de ámbitos

La tabla de símbolos se organiza en forma de árbol de ámbitos (también llamado "pila de scopes"):

- El **ámbito global** es la raíz; contiene las variables declaradas en el nivel principal del programa.
- Cada bloque `if`, `hilux` o `while` crea un ámbito **hijo** que tiene acceso a las variables del padre, pero no al revés.

```
Ámbito global: { x → int, y → float }
  └── Ámbito if: { z → bool }         ← 'z' solo visible aquí
  └── Ámbito while: { i → int }       ← 'i' solo visible aquí
```

---

## 10. Ejemplos de código correcto e incorrecto

### Código correcto

```claudiocomp
// Variables de distintos tipos
int edad = 25;
float salario = 1500.75;
bool activo = true;
string nombre = "Claudio";

// Operaciones válidas
edad = edad + 1;
salario = salario * 1.05;

// Bloque if con su propio ámbito
if (activo) {
    int bono = 200;
    salario = salario + bono;
}

// Ciclo while
while (edad < 65) {
    edad = edad + 1;
}
```

### Código con errores semánticos

```claudiocomp
// Error 1: variable no declarada
total = 500;

// Error 2: declaración duplicada
int x = 10;
int x = 20;

// Error 3: tipo incompatible
string texto = "hola";
x = texto;

// Error 4: operación aritmética con bool
bool flag = true;
int resultado = x + flag;

// Error 5: operación lógica con int
int a = 1;
int b = 2;
bool logico = a && b;
```

---

## Referencias

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques,
  and Tools* (2.ª ed.). Addison-Wesley.
- Cooper, K., & Torczon, L. (2011). *Engineering a Compiler* (2.ª ed.). Morgan Kaufmann.
