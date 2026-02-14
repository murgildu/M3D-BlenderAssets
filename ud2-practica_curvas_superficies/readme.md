# Práctica 2 (20 %) - Curvas y superficies: del código a Blender (Logo Murgildu)

## Contexto y objetivo
El objetivo de esta práctica es trabajar las competencias teóricas del tema de **curvas y superficies** mediante dos fases conectadas:

1) **Fase analítica (Python):** revisar e interpretar scripts que implementan herramientas clave (Bernstein, Bézier, elevación de grado, algoritmo de De Casteljau, subdivisión, etc).

2) **Fase aplicada (Blender):** llevar esas ideas a Blender, incorporando partes del código en el **Text Editor** para construir progresivamente el **logo de Murgildu** ¡o cualquier otro que te guste más! (a partir de una imagen de referencia).

La práctica está diseñada para que el código auxiliar esté **completo y ejecutable**, pero tu trabajo consiste en: entenderlo,  identificar funciones relevantes, **extraer/completar/copiar** esas partes al script final que quedará **dentro del .blend que tienes que entregar** (revisa las condiciones de entrega en eGela).

La duración estimada total de la práctica es de ~7 horas.

---


## Material auxiliar disponible 
La teoría y PDFs están en eGela. Si te bloqueas, revisa:
- polinomios de Bernstein,
- definición de Bézier por Bernstein,
- continuidad/tangentes (handles),
- algoritmo de De Casteljau (niveles y subdivisión),
- elevación de grado.

---

## Estructura del repositorio (lo que necesitas aquí)
- `python/scripts_auxiliares/`
  Scripts ejecutables (standalone) para estudiar y reutilizar funciones.
- `starter_blender/`
  Archivo `.blend` inicial ya con el logo (imagen) y recursos necesarios.

---

# Parte 1 - Python: comprensión, estudio y extracción de funciones (≈2h 30m)

## 1.1 Revisa los scripts auxiliares
Ejecuta cada script y asegúrate de comprender qué hace y qué imprime/dibuja:

- `01_bernstein_partition.py`
  Bernstein y la propiedad de **partición de la unidad** (suma=1).

- `02_bezier_influence_move.py`
  Bézier por fórmula y efecto de **mover un punto de control**.

- `03_degree_elevation.py`
  **Elevación de grado** sin cambiar la curva.

- `04_casteljau_levels_subdivision.py`
  **De Casteljau**, niveles, comparación con Bernstein y subdivisión.

### Mini-check auto-evaluación
Antes de pasar a Blender, responde a estas preguntas:

1) ¿Por qué los polinomios de Bernstein se interpretan como pesos?
2) ¿Qué significa que la suma de los Bernstein sea 1?
3) Si muevo un punto de control Pi, ¿por qué no se mueve igual la curva para un u fijo?
4) ¿Qué hace la elevación de grado y por qué no cambia la curva?
5) ¿Qué devuelve De Casteljau en cada nivel y qué significa geométricamente?
6) ¿Para qué sirve subdividir una Bézier?

Si no puedes contestar más de 4 o 5 de estas preguntas, revisa teoría y ejercicios antes de seguir.

---

## 1.2 Funciones que vas a necesitar en Blender
En la Parte 2 tendrás que **copiar / completar** (desde los scripts auxiliares) estas funciones a un Text block dentro del `.blend` (scripting en blender):

**Imprescindibles**
- `bernstein(n, i, u)`
- `bezier_point(P, u)`  (versión sin numpy; o adaptada)
- `de_casteljau_levels(P, u)` o `de_casteljau_point(P, u)`
- `subdivide_bezier(P, u)` (para refinar tramos si lo necesitas)

**Recomendables**
- `elevate_degree(P)`
- `max_curve_distance(P, Q)` (verificación)

Consejo: no copies todo el script. Copia solo funciones + imports necesarios.

---

# Parte 2 - Blender: referencia del logo y construcción progresiva (≈4h)

## 2.0 Preparación: abre el starter .blend
1) Abre el archivo de `starter_blender/`.
2) Debes ver la imagen del logo Murgildu ya incluida como referencia (o lista para añadir).
 También puedes realizar la práctica con cualquier otro logo que te guste :)

Para añadir otro logo, sigue estos pasos:
- Ve a **vista frontal ortográfica**:
  - Numpad `1` (Front)
  - Numpad `5` (Ortho)W
- `Add > Image > Reference` (puedes hacerlo algo transparente en Data Object properties para trabajar más cómodamente)
- Ajusta posición/escala para que quede centrada.

Crea (o usa) una colección llamada `REFERENCE` y mete ahí la imagen.

---

## 2.1 Text Editor: crea tu biblioteca dentro del .blend
En Blender:
1) Abre el panel **Scripting** o el **Text Editor**.
2) Crea un nuevo texto: `P2_LIB`
3) Copia aquí las funciones necesarias desde `python/scripts_auxiliares`.

Recomendación mínima para arrancar:
- `import math`
- funciones de Bernstein
- `bezier_point`
- De Casteljau (al menos `de_casteljau_levels` o `de_casteljau_point`)

Así conseguimos que nuestro `.blend` sea autosuficiente y no depender de archivos externos al entregar.

---

## 2.2 Primer paso del logo: una curva Bézier que puedas muestrear (una prueba de kick off)
Objetivo: validar que tu código dentro de Blender funciona, antes de dibujar el logo real.

1) Crea otro texto: `P2_BUILD_LOGO`
2) En ese texto:
   - define 4 puntos de control (una cúbica simple),
   - muestrea puntos con `bezier_point`,
   - crea una polilínea (mesh) con esos puntos.

### Resultado esperado
- En la escena aparece una curva de prueba como polilínea.
- Puedes cambiar P0..P3 y re-ejecutar el script para ver cambios.

Si este paso falla, NO sigas al logo: arregla primero el pipeline (código → geometría).

---

## 2.3 Trazo del logo por tramos (curvas cúbicas)
Objetivo: construir el contorno del logo como una unión de segmentos cúbicos.

### Método recomendado
1) Divide el contorno del logo en **tramos**: por ejemplo:
   - contorno del casco (varios tramos)
   - contorno de las gafas
   - detalles internos (circuitos) si llegas

2) Para cada tramo, defines **un segmento cúbico** con 4 puntos:
   - P0 y P3: extremos del tramo
   - P1 y P2: controlan la tangente/curvatura

3) Muestras cada segmento con tu función `bezier_point` y esta los cose en una sola polilínea.

### Qué se evalúa aquí
- Que el contorno sea reconocible y se ajuste razonablemente a la referencia.
- Que intentes mantener continuidad visual:
  - tramos suaves: handles/tangentes consistentes
  - esquinas intencionadas: cambio brusco (C0) o más suaves (C1,G1)

Nota: no se busca perfección milimétrica; se busca aplicar conceptos y obtener un resultado limpio.

---

## 2.4 Refinado con De Casteljau (subdivisión)
Cuando un tramo no encaja bien, en lugar de inventarte otro tramo desde cero, puedes:

1) Subdividir un segmento cúbico en `u=0.5` (o donde necesites) con la función `subdivide_bezier`.
2) Reemplazar el segmento original por dos segmentos.
3) Ajustar solo los controles del tramo que falla.

Esto te da un flujo de trabajo real:
- empiezas con pocos tramos,
- subdivides donde falta detalle,
- ajustas localmente.

---

## 2.5 De curva a objeto 3D (extrusión / bevel / mesh)
Objetivo: convertir el contorno en un logo 3D imprimible/usable.

### Opción A (rápida): trabajar como Curve 2D y extruir
- Si construiste el contorno como **Curve**:
  - `Object Data Properties (Curve) > Geometry > Extrude`
  - `Bevel` para redondear
  - `Fill` activado

### Opción B (universal): convertir a mesh y extruir
1) Selecciona el contorno
2) `Object > Convert > Mesh`
3) En Edit Mode:
   - `E` para extruir
   - `Ctrl+B` o bevel modifier para cantos

**Recomendación de calidad**
- Aplica transformaciones (`Ctrl+A`)
- Revisa normales (recalcular si hace falta)
- No exageres resolución (evita mallas innecesariamente pesadas)

---

## 2.6 Materiales y presentación
Mínimo requerido:
- asignar un material (un color/plástico sencillo)
- una iluminación básica
- un render o captura final

Extra (sube nota):
- material con roughness/metallic razonables
- bevel limpio
- escena ordenada por colecciones (REFERENCE / CURVES / MESH_FINAL)

---

## 2.7 (Opcional) Exportación STL
Si tu modelo es sólido:
- `File > Export > STL`
- Comprueba escala/unidades según lo trabajado en la asignatura.

---

# Checklist final (antes de entregar)
- [ ] El `.blend` abre y muestra el logo final en 3D.
- [ ] La imagen de referencia está en una colección separada.
- [ ] Hay al menos dos Text blocks:
  - [ ] `P2_LIB` con funciones copiadas
  - [ ] `P2_BUILD_LOGO` con el script que genera/actualiza geometría
- [ ] El contorno se construye (total o parcialmente) con tu código (no solo “a mano”).
- [ ] El logo final tiene grosor (extrusión) y acabado básico (material/bevel).
- [ ] La escena está razonablemente limpia y ordenada.

---

# Sugerencia de organización de tiempo (~7h)
- Parte 1 (Python): 2h 30m 
- Parte 2 (Blender):
  - Setup + pipeline de prueba: 45m
  - Trazado por tramos: 2h
  - Refinado (subdivisión) + limpieza: 45m
  - Extrusión + materiales + render: 30m

---

## Notas
- Esta práctica está pensada para trabajar **conceptos**, no solo hacer un logo.
- El objetivo es que puedas justificar lo que haces y lo asocies a la teoría de clase





















1️⃣ Construcción base

Añade una curva Bézier.

Define 4 puntos de control formando un arco o perfil reconocible.

Activa la visualización del polígono de control.

SCRIPT BASE (.py)
2️⃣ Análisis de influencia

Mueve solo un punto intermedio.

Observa cómo cambia la curva.

Repite con otro punto distinto.

(El objetivo es ver que la curva no pasa por los puntos intermedios.)

3️⃣ Comparación geométrica

Duplica la curva.

Convierte la copia en B-Spline.

Repite el mismo desplazamiento de control.

(Observa la diferencia de comportamiento (más local vs más global).)

4️⃣ Generación de forma 3D

Usa la curva como base para crear un objeto con volumen:

Opciones válidas:

Perfil de un vaso o probeta (bevel)

Asa o mango ergonómico

Trayectoria de un objeto deportivo

Tubo o conducto curvo

Silueta extrusionada

⚠️ No modelar escenas completas: un único objeto principal.

5️⃣ Ajuste final

Revisa resolución de la curva (Preview U).

Ajusta continuidad visual.

Organiza la escena.
