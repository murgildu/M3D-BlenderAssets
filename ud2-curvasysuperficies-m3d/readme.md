# Modelado 3D en Blender - Tema2 - Curvas y Superficies

Este repositorio acompaña a la parte teórica vista en clase sobre las curvas y superficies en Blender.
La teoría introduce los conceptos matemáticos en relación a los tipos de curvas, curvas de Bezier, Splines, Nurbs ... y las prácticas los trasladan a Blender mediante:

- ejercicios reproducibles en escena,
- scripts en Python (API de Blender),
- verificadores (*checkers*) para validación objetiva.

El objetivo del repositorio es que el alumnado pueda **ver, medir y comprobar** en Blender los conceptos que aparecen en el documento teórico.

---

## Estructura de los ejercicios

```
/
─ README.md
─ blender/
 ├─ scripts/ # Scripts de cada ejercicio (generación de escena)
 ├─ checks/ # Scripts de verificación por ejercicio
 ├─ assets/ # Recursos opcionales (texturas, .blend base, etc.)
 └─ templates/ # Plantillas utilitarias (helpers, utilidades)
```


---

## Requisitos

- **Blender** (versión recomendada: 3.x o superior).
- No se requiere instalación externa: se utiliza **Python embebido** de Blender y su módulo `mathutils`.

---

## Cómo usar este repositorio en Blender

### 1) Descargar o clonar el repositorio
- Opción A: descargar como ZIP y descomprimir.
- Opción B: clonar con Git (recomendado para docencia y actualizaciones).

### 2) Abrir Blender y ejecutar scripts

Los scripts se encuentran en `blender/scripts/`. Cada ejercicio crea su propia escena (o colección) de forma reproducible.

**Método recomendado (Blender Editor):**
1. Abrir Blender.
2. Ir a la pestaña **Scripting**.
3. En el panel **Text Editor**:
   - **Open** → seleccionar el script del ejercicio (por ejemplo `lab01_1_1_translation.py`).
   - Pulsar **Run Script**.

**Salida esperada:**
- Se crea una colección (por ejemplo `Lab01_...`) con objetos y elementos visuales.
- Se imprime información en consola (si aplica).
- Se dejan elementos listos para inspección (flechas, etiquetas, curvas, etc.).

> Para ver la consola:
> - Windows: *Window → Toggle System Console*
> - macOS/Linux: ejecutar Blender desde terminal para ver salida estándar.

### 3) Realizar la parte UI del ejercicio
Cada ejercicio indica (en su guía o en comentarios del script) qué pasos deben repetirse manualmente:
- mover objetos,
- rotar para observar cambios,
- editar handles,
- activar sombreado/viewport modes,
- etc.

### 4) Ejecutar el verificador (*checker*)
Los verificadores están en `blender/checks/` y validan propiedades numéricas (por ejemplo dot product, norma, tolerancias).

1. Abrir el checker correspondiente (por ejemplo `check_01_1_1_translation.py`).
2. Ejecutarlo con **Run Script**.
3. Revisar el resultado en consola.

Los checkers típicamente reportan:
- **PASS** / **FAIL**
- valores medidos,
- tolerancia usada
- recomendaciones mínimas si falla.

---

## Organización de ejercicios

> Nota de compatibilidad (GitHub Markdown): en este README se evitan símbolos LaTeX que no se renderizan en GitHub (por ejemplo `epsilon`).
> Cuando se use tolerancia numérica se escribirá como **EPS** y se definirá en cada script/checker (por ejemplo `EPS = 1e-5`).

---

## Bloque 3 - Curvas: representación explícita, implícita y paramétrica

### 3.1 - Curva explícita: muestreo de y = f(x)
- **Python:** muestrear `x` y crear vértices `(x, f(x), 0)` conectados.
- **Objetivo:** evaluación directa; limitación para curvas cerradas completas.

### 3.2 - Curva implícita: circunferencia como condición F(x, y) = 0
- **Python:** muestrear rejilla y seleccionar puntos con `abs(x*x + y*y - R*R) < EPS`.
- **Objetivo:** test de pertenencia y dificultad de recorrido ordenado.

### 3.3 - Curva paramétrica: circunferencia como P(u)
- **Python:** muestrear `u` y construir `P(u)`; comparar con la forma implícita.
- **Objetivo:** recorrido secuencial natural.
- **Verificación (checker):** métricas simples (por ejemplo, distancia al centro cercana a `R` para todos los puntos, y resolución consistente).

### 3.4 - Generador de curvas paramétricas
- **Objetivo:** crear geometría a partir de ecuaciones paramétricas.
- **Tarea (Python):** generar hélice o curva en “S” mediante muestreo de `u` y creación de un objeto `Curve`.
- **Fórmulas de referencia:**
  - `x(u) = a * cos(u)`
  - `y(u) = a * sin(u)`
  - `z(u) = b * u`
- **Conexión teórica:** efecto de la discretización de `u` en la resolución.

---

## Bloque 4 - Tangente y recta tangente en curvas paramétricas

### 4.1 - Tangente como derivada numérica
- **Python:** aproximar la derivada con diferencias centradas:
  - `P'(u0) ≈ (P(u0 + h) - P(u0 - h)) / (2*h)`
- **Visualización:** flecha tangente en `P(u0)`.

### 4.2 - Recta tangente Q(t)
- **Python:** construir y dibujar la recta:
  - `Q(t) = P(u0) + t * P'(u0)`
- **Interfaz (UI):** variar `u0` con un control y observar el desplazamiento.

---

## Bloque 5 - Polinomios de Bernstein y curvas Bézier

### 5.1 - Bernstein cúbico: evaluación y propiedad de suma
- **Python:** para `u` en `[0, 1]`, calcular `B0, B1, B2, B3` y representarlos.
- **Visualización:** cuatro gráficas y una quinta para la suma.
- **Verificación (checker):** `max_abs( (B0 + B1 + B2 + B3) - 1 ) < EPS`.

### 5.2 - Bézier cúbica por formulación de Bernstein
- **Python:** construir la curva a partir de puntos de control `P0..P3`:
  - `P(u) = sum(Pi * Bi(u))`
- **Comparación:** superponer con una curva Bézier creada con controles equivalentes en Blender.
- **Objetivo:** equivalencia entre implementación basada en Bernstein y la curva Bézier en Blender.

### 5.3 - Tangentes en extremos y relación con handles
- **Python:** verificar empíricamente:
  - `P'(0) = 3 * (P1 - P0)`
  - `P'(1) = 3 * (P3 - P2)`
- **Visualización:** flechas tangentes en los extremos y handles visibles.
- **Verificación (checker):** diferencia angular entre direcciones menor que EPS (en radianes o grados, según se defina).

---

## Bloque 6 - Splines y continuidad: C0, G1 y aproximación de C1

### 6.1 - Unión de dos tramos: C0 y aparición de quiebro
- **Interfaz (UI):** unir tramos con punto común y handles desalineados; observar discontinuidad.
- **Python:** medir tangentes a izquierda y derecha del empalme.

### 6.2 - Continuidad geométrica G1 en Blender
- **Interfaz (UI):** alinear handles en la unión (misma dirección tangente).
- **Python:** comprobar proporcionalidad (ángulo cercano a 0).
- **Verificación (checker):** `angle(T_left, T_right) < EPS_ANGLE`.

### 6.3 - Aproximación de continuidad C1
- **Interfaz (UI):** ajustar longitudes de handles para aproximar igualdad de tangentes.
- **Python:** comprobar igualdad aproximada.
- **Verificación (checker):** `|T_left - T_right| < EPS`.

### 6.4 - Test de continuidad (splines y derivadas)
- **Objetivo:** manipular tangentes para comprender suavidad G1 y aproximación de C1.
- **Tarea:** modificar el vector tangente del segundo tramo para que sea proporcional al del primero.
- **Conexión teórica:** continuidad geométrica G1 como criterio suficiente para suavidad perceptual.


---



