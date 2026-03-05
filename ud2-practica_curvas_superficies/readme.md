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
- `import math` , `import numpy as np`
- importa funciones de Bernstein, Bezier, De Casteljau, ... mencionadas anteriormente y/o que consideres relevantes. 

Así conseguimos que nuestro `.blend` sea autosuficiente y no depender de archivos externos al entregar.

---

## 2.2 Primer paso del logo: una curva Bézier que puedas muestrear (una prueba de kick off)
Objetivo: validar que tu código dentro de Blender funciona, antes de dibujar el logo real.

1) Crea otro texto: `P2_BUILD_LOGO`
2) En ese texto:
   - define 4 puntos de control (una cúbica simple),
   - muestrea puntos con `bezier_point`,
   - crea una polilínea (mesh) con esos puntos.

Puedes utilizar este código auxiliar para definir los puntos:

```
from mathutils import Vector

# Puntos de control (editables)
P0 = Vector((0.0, 0.0, 0.0))
P1 = Vector((1.5, 2.0, 0.0))
P2 = Vector((3.0, -2.0, 0.0))
P3 = Vector((4.5, 0.0, 0.0))
```

Puedes utilizar el cursor 3D para posicionar puntos relevantes y encontrar la posición (x,y,z) fácilmente mirando en la barra lateral la **location** del 3DCursor.

### Resultado esperado
- En la escena aparece una curva de prueba como polilínea.
- Puedes cambiar P0..P3 y re-ejecutar el script para ver cambios.

Si este paso falla, NO sigas al logo: arregla primero el pipeline (código → geometría).


Aquí tienes código helper para convertir los puntos en mesh de blender, si quieres puedes definir otra librería para estos helpers:

```
import bpy
from mathutils import Vector
import numpy as np

# Ejecuta el texto "P2_LIB"
lib_text = bpy.data.texts["P2_LIB"]
exec(lib_text.as_string(), globals())

# -----------------------------
# Helpers: polilínea mesh
# -----------------------------
def build_polyline_mesh(name: str, points_xyz, close: bool = False):
    """
    Crea un objeto Mesh con una polilínea:
      - points_xyz: iterable de puntos (x,y,z) o numpy array (N,3)
      - close: si True, cierra la curva uniendo último con primero
    """
    # Convertimos a lista de tuplas (x,y,z)
    verts = [tuple(map(float, p)) for p in points_xyz]
    if len(verts) < 2:
        raise ValueError("Se necesitan al menos 2 puntos para una polilínea")

    edges = [(i, i + 1) for i in range(len(verts) - 1)]
    if close:
        edges.append((len(verts) - 1, 0))

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, edges, [])
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


También puedes convertir estos puntos a curvas Bézier, igual que hicimos en los ejemplos del tema 2.

# -----------------------------
# Puntos de control (editables)
# -----------------------------
P0 = Vector((-3.8199, 0, -1.68171))
P1 = Vector((-2.8199, 0, -1.68171))
P2 = Vector((-1.8199, 0, -1.68171))
P3 = Vector(( 0.8199, 0, -1.68171))

P = np.array([P0[:], P1[:], P2[:], P3[:]], dtype=float)

# -----------------------------
# Muestreo + creación de mesh
# -----------------------------
pts = bezier_curve(P, num_samples=40)   # <- esto debería devolver (40,3)
curve_obj = build_polyline_mesh("BezierPolyline1", pts, close=False)

# (Opcional) seleccionar el objeto para verlo fácil
bpy.ops.object.select_all(action="DESELECT")
curve_obj.select_set(True)
bpy.context.view_layer.objects.active = curve_obj
```
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

3) Muestras cada segmento con tu función `bezier_point` / `bezier_curve` y esta los cose en una sola polilínea.

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
## 2.5 Refinado y Unificación: De Segmentos Bézier a B-Spline Global

Tras haber trazado el logo mediante segmentos cúbicos de Bézier independientes, el resultado puede presentar discontinuidades en las uniones. Para profesionalizar el acabado, evolucionamos el diseño utilizando los puntos de control definidos en la fase anterior para alimentar una estructura de **B-Spline**.

### A) Extracción y "Cosido" de Puntos de Control
El primer paso consiste en recopilar los puntos de control ($P_0, P_1, P_2, P_3$) de cada segmento Bézier correlativo.

* **Lógica de unión:** Para que la transición sea fluida, eliminamos los puntos duplicados en las juntas (donde el $P_3$ de un tramo coincide con el $P_0$ del siguiente) y creamos una lista única de puntos de control.
* **Ventaja:** Al pasar esta lista a la función `bspline_curve`, la matemática de la B-Spline se encarga de promediar la curvatura, eliminando cualquier "pico" visual indeseado en las uniones.



### B) Implementación de la B-Spline Global
Utilizando la función `bspline_curve` de nuestra `P2_LIB`, generamos una sola polilínea para todo el contorno (ej. el casco o las gafas).

* **Grado 3 (Cúbica):** Mantenemos el grado 3 para asegurar una **continuidad de curvatura $C^2$**. Esto significa que no solo la posición y la tangente coinciden, sino que la "suavidad" de la curva es constante en todo el trayecto.
* **Control Local:** A pesar de ser una curva única, gracias al algoritmo de **De Boor**, podemos reajustar un punto de control específico del logo sin que se deforme el resto del trazado.



### C) Tratamiento de Esquinas y Precisión (NURBS)
No todas las partes del logo deben ser infinitamente suaves; algunas requieren precisión geométrica o ángulos marcados.

* **Esquinas afiladas:** Si el logo tiene un ángulo marcado, colocamos **tres puntos de control en la misma ubicación**. Esto reduce la continuidad localmente y "fuerza" a la B-Spline a pasar exactamente por ese vértice.
* **Uso de Pesos ($w$):** Si una zona requiere una curvatura que no se ajusta con puntos normales (como un arco de circunferencia exacto), transformamos el tramo en **NURBS** aumentando el peso del punto de control. Un peso $w > 1$ "tensa" la curva hacia el punto, permitiendo ajustar el diseño con precisión milimétrica sin necesidad de añadir más geometría compleja.


## 2.6 De curva a objeto 3D (extrusión / bevel / mesh)
Objetivo: convertir el contorno en un logo 3D imprimible/usable.

### Opción A (rápida): trabajar como Curve 2D y extruir
- Si construiste el contorno como **Curve**:
  - `Object Data Properties (Curve) > Geometry > Extrude`
  - `Bevel` para redondear
  - `Fill` activado

- También puedes exportar a mesh y extruir desde ahí

1) Selecciona el contorno
2) `Object > Convert > Mesh`
3) En Edit Mode:
   - `E` para extruir
   - `Ctrl+B` o bevel modifier para cantos


### Opción B (universal): Si construiste un mesh

Primero tendrás que cerrar la polilínea, p.e., con extrusión, merge de puntos, fill o construyendo el mesh con close=True y entonces podrás dar volumen con un modificador (Solidify)

**Recomendación de calidad**
- Aplica transformaciones (`Ctrl+A`)
- Revisa normales (recalcular si hace falta)
- No exageres resolución (evita mallas innecesariamente pesadas)

---

## 2.7 Materiales y presentación
Mínimo requerido:
- asignar un material (un color/plástico sencillo)
- una iluminación básica
- un render o captura final

Extra (sube nota):
- material con roughness/metallic razonables
- bevel limpio
- escena ordenada por colecciones (REFERENCE / CURVES / MESH_FINAL)

---

## 2.8 (Opcional) Exportación STL
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
- [ ] Un contorno construido (total o parcialmente) con tu código (no solo “a mano”).
- [ ] Un contorno hecho con una BSpline única (puede ser de todo el logo o de una parte).
- [ ] El logo final tiene grosor (extrusión) y acabado básico (material/bevel).
- [ ] La escena está razonablemente limpia y ordenada.

---

# Sugerencia de organización de tiempo (~8h)
- Parte 1 (Python): 2h 30m 
- Parte 2 (Blender):
  - Setup + pipeline de prueba: 45m
  - Trazado por tramos: 2h
  - Refinado (subdivisión) + limpieza: 45m
  - Refinado y Unificación con Bsplines 45m
  - Tratamiento esquinas Nurbs: 45m
  - Extrusión + materiales + render: 30m

---

## Notas
- Esta práctica está pensada para trabajar **conceptos**, no solo hacer un logo.
- El objetivo es que puedas justificar lo que haces y lo asocies a la teoría de clase
