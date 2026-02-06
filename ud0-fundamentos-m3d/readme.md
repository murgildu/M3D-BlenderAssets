# Modelado 3D en Blender - Repaso de Fundamentos Matemáticos

Este repositorio acompaña a la parte teórica vista en clase sobre los fundamentos algebraicos para el Modelado 3D en Blender.
La teoría introduce los conceptos matemáticos mínimos del álgebra vectorial y las prácticas los trasladan a Blender mediante:

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

## Bloque 1 - Vectores y transformaciones

### 1.1 - Traslación como suma de vectores
- **Interfaz (UI):** mover un vértice u objeto aplicando un vector de traslación dado.
- **Python:** crear un punto `P`, un vector `t` y calcular `P' = P + t`.
- **Visualización:** flechas de `P`, `t` y `P'`.
- **Verificación (checker):** `dist(P', P + t) < EPS`.

### 1.2 - Escalado respecto a un pivote
- **Interfaz (UI):** escalar un conjunto de vértices respecto al *3D Cursor* (pivote).
- **Python:** implementar `P' = C + k(P - C)` y comparar con la transformación aplicada por Blender.
- **Visualización:** antes/después y líneas al pivote `C`.
- **Verificación (checker):** `abs( dist(P', C) / dist(P, C) - k ) < EPS` (para puntos con `P != C`).

### 1.3 - Norma (módulo) y normalización
- **Interfaz (UI):** medir distancias y compararlas con la longitud de un vector.
- **Python:** normalizar `v_hat = v / |v|` y verificar que `|v_hat| = 1`.
- **Visualización:** flecha original y flecha normalizada.
- **Verificación (checker):** `abs(|v_hat| - 1) < EPS`.

### 1.4 - Inspector de vectores (álgebra lineal con `mathutils`)
- **Objetivo:** validar posiciones, distancias y ángulos entre objetos usando `mathutils`.
- **Tarea (Python):** con dos objetos seleccionados (`bpy.context.selected_objects`), calcular:
  - vector diferencia `d = B.location - A.location` y su distancia `|d|`,
  - producto escalar entre los ejes Y locales (vectores frontales),
  - ángulo en grados entre dichos ejes.
- **Conexión teórica:** dot cercano a 1 si las orientaciones coinciden; cercano a 0 si son perpendiculares.

---

## Bloque 2 - Producto escalar: ángulo, ortogonalidad y sombreado

### 2.1 - Producto escalar como medida de alineamiento
- **Interfaz (UI):** rotar un objeto/flecha y observar el cambio angular.
- **Python:** calcular `dot(u, v)`, `cos(theta)` y `theta`; mostrar resultados.
- **Visualización:** etiqueta o indicador con dot y ángulo.

### 2.2 - Ortogonalidad: construcción de un vector perpendicular
- **Interfaz (UI):** construir una dirección perpendicular en el plano XY y comprobarlo.
- **Python:** generar `u = (a, b)` y `v = (-b, a)` y verificar `dot(u, v) = 0`.
- **Verificación (checker):** `abs(dot(u, v)) < EPS`.

### 2.3 - Sombreado difuso tipo Lambert con normales
- **Interfaz (UI):** plano + luz direccional; rotación del plano y observación del brillo.
- **Python:** leer normal `N` y dirección a luz `L`, calcular `I = max(0, dot(N, L))` y mapear a material/color.
- **Visualización:** cambio de color según `I`.
- **Verificación (checker):**
  - caso ortogonal: `I` cercano a 0,
  - caso alineado: `I` cercano a 1 (si `N` y `L` están normalizados).

### 2.4 - Normales y sombreado por umbral (producto escalar)
- **Objetivo:** colorear caras según umbral de iluminación.
- **Tarea (Python):** iterar polígonos y colorear si `dot(n, L) > 0.5`.
- **Conexión teórica:** uso del producto escalar como criterio de alineamiento entre normal y luz.

---

