# Modelado 3D en Blender - Repaso de Fundamentos Matemáticos

Este repositorio acompaña a la parte teórica vista en clase sobre los fundamentos algebraicos para el Modelado 3D en Blender.
La teoría introduce los conceptos matemáticos mínimos (álgebra vectorial, producto escalar, curvas paramétricas, Bézier/Bernstein, splines y continuidad) y las prácticas los trasladan a Blender mediante:

- ejercicios reproducibles en escena,
- scripts en Python (API de Blender),
- verificadores (*checkers*) para validación objetiva.

El objetivo del repositorio es que el alumnado pueda **ver, medir y comprobar** en Blender los conceptos que aparecen en el documento teórico.

---

## Estructura de los ejercicios

```
/
├─ README.md
├─ blender/
│ ├─ scripts/ # Scripts de cada ejercicio (generación de escena)
│ ├─ checks/ # Scripts de verificación por ejercicio
│ ├─ assets/ # Recursos opcionales (texturas, .blend base, etc.)
│ └─ templates/ # Plantillas utilitarias (helpers, utilidades)
└─ LICENSE
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
- tolerancia usada (\(\varepsilon\)),
- recomendaciones mínimas si falla.

---

## Convenciones y tolerancias numéricas

En geometría computacional y escenas 3D es normal trabajar con tolerancias.
Los ejercicios utilizarán un \(\varepsilon\) configurable para comparaciones aproximadas, por ejemplo:

- distancias: \(|d - d_{\text{esperado}}| < \varepsilon\)
- ángulos: \(|\theta - \theta_{\text{esperado}}| < \varepsilon\)
- sumas de pesos: \(\max(|\sum B_i - 1|) < \varepsilon\)

---

## Guía visual de la relación teoría/práctica

Cada bloque está diseñado para que el alumnado:

1) construya el objeto/escena,
2) visualice el concepto,
3) mida el resultado,
4) lo valide con el checker.


---

# Organización de ejercicios

## Bloque 1 - Vectores y transformaciones

### 1.1 - Traslación como suma de vectores
- **Interfaz (UI):** mover un vértice u objeto aplicando un vector de traslación dado.
- **Python:** crear un punto \(P\), un vector \(t\) y calcular \(P' = P + t\).
- **Visualización:** flechas de \(P\), \(t\) y \(P'\).
- **Verificación (checker):** distancia entre \(P'\) y \(P+t\) menor que \(\varepsilon\).

### 1.2 - Escalado respecto a un pivote
- **Interfaz (UI):** escalar un conjunto de vértices respecto al *3D Cursor* (pivote).
- **Python:** implementar \(P' = C + k(P-C)\) y comparar con la transformación de Blender.
- **Visualización:** antes/después y líneas al pivote \(C\).
- **Verificación (checker):** cociente de distancias al pivote aproximadamente \(k\) (tolerancia \(\varepsilon\)).

### 1.3 - Norma (módulo) y normalización
- **Interfaz (UI):** medir distancias y compararlas con la longitud de un vector.
- **Python:** normalizar \(\hat v = v/\|v\|\) y verificar \(\|\hat v\| = 1\).
- **Visualización:** flecha original y flecha normalizada.
- **Verificación (checker):** \(\lvert\|\hat v\|-1\rvert < \varepsilon\).

### 1.4 - Inspector de vectores (álgebra lineal con `mathutils`)
- **Objetivo:** validar posiciones, distancias y ángulos entre objetos usando `mathutils`.
- **Tarea:** script con dos objetos seleccionados (`bpy.context.selected_objects`) que calcule:
  - vector diferencia y distancia relativa,
  - producto escalar entre ejes Y locales (vectores frontales),
  - ángulo en grados entre esos vectores.
- **Conexión teórica:** producto escalar cercano a 1 si orientaciones coinciden; cercano a 0 si son perpendiculares.

---

## Bloque 2 - Producto escalar: ángulo, ortogonalidad y sombreado

### 2.1 - Producto escalar como medida de alineamiento
- **Interfaz (UI):** rotar un objeto/flecha y observar el cambio angular.
- **Python:** calcular \(u\cdot v\), \(\cos(\theta)\) y \(\theta\); mostrar resultados.
- **Visualización:** etiqueta o indicador con dot y ángulo.

### 2.2 - Ortogonalidad: construcción de un vector perpendicular
- **Interfaz (UI):** construir una dirección perpendicular en el plano XY y comprobarlo.
- **Python:** generar \(u=(a,b)\), \(v=(-b,a)\) y verificar \(u\cdot v=0\).
- **Verificación (checker):** \(u\cdot v \approx 0\) con tolerancia \(\varepsilon\).

### 2.3 - Sombreado difuso tipo Lambert con normales
- **Interfaz (UI):** plano + luz direccional; rotación del plano y observación del brillo.
- **Python:** leer normal \(N\) y dirección a luz \(L\), calcular \(\max(0, N\cdot L)\) y mapear a material/color.
- **Visualización:** cambio de color según \(N\cdot L\).
- **Verificación (checker):** ortogonal ≈ 0; alineado ≈ máximo.

### 2.4 - Normales y sombreado por umbral (producto escalar)
- **Objetivo:** colorear caras según umbral de iluminación.
- **Tarea:** iterar polígonos y colorear si \(\vec{n}\cdot\vec{L} > 0.5\).
- **Conexión teórica:** uso directo de \(\vec{u}\cdot\vec{v}=\|\vec{u}\|\,\|\vec{v}\|\cos(\theta)\).

---

## Bloque 3 - Curvas: representación explícita, implícita y paramétrica

### 3.1 - Curva explícita: muestreo de \(y=f(x)\)
- **Python:** muestrear \(x\) y crear vértices \((x, f(x), 0)\) conectados.
- **Objetivo:** evaluación directa; limitación para curvas cerradas completas.

### 3.2 - Curva implícita: circunferencia como condición \(F(x,y)=0\)
- **Python:** muestrear rejilla y seleccionar puntos con \(\lvert x^2+y^2-R^2\rvert < \varepsilon\).
- **Objetivo:** test de pertenencia y dificultad de recorrido ordenado.

### 3.3 - Curva paramétrica: circunferencia como \(\vec{P}(u)\)
- **Python:** muestrear \(u\) y construir \(\vec{P}(u)\); comparar con la forma implícita.
- **Objetivo:** recorrido secuencial natural.
- **Verificación (checker):** ordenación paramétrica, resolución, longitud aproximada.

### 3.4 - Generador de curvas paramétricas
- **Objetivo:** crear geometría a partir de ecuaciones paramétricas.
- **Tarea:** generar hélice o curva en “S” mediante muestreo de \(u\) y creación de un objeto `Curve`.
- **Fórmulas:**

  \[
  x(u)=a\cos(u)
  \]
  \[
  y(u)=a\sin(u)
  \]
  \[
  z(u)=bu
  \]
- **Conexión teórica:** efecto de la discretización de \(u\) en la resolución.

---

## Bloque 4 - Tangente y recta tangente en curvas paramétricas

### 4.1 - Tangente como derivada numérica
- **Python:** aproximar

  \[
  \vec{P}'(u_0)\approx\frac{\vec{P}(u_0+h)-\vec{P}(u_0-h)}{2h}
  \]
- **Visualización:** flecha tangente en \(\vec{P}(u_0)\).

### 4.2 - Recta tangente \(\vec{Q}(t)\)
- **Python:** construir y dibujar

  \[
  \vec{Q}(t)=\vec{P}(u_0)+t\,\vec{P}'(u_0)
  \]
- **Interfaz (UI):** variar \(u_0\) con un control y observar el desplazamiento.

---

## Bloque 5 - Polinomios de Bernstein y curvas Bézier

### 5.1 - Bernstein cúbico: evaluación y propiedad de suma
- **Python:** evaluar \(B_{0,3}(u)\dots B_{3,3}(u)\) para \(u\in[0,1]\) y representarlos.
- **Visualización:** cuatro gráficas y una quinta para la suma.
- **Verificación (checker):**

  \[
  \max\left(\left| (B_{0,3}+B_{1,3}+B_{2,3}+B_{3,3})-1\right|\right)<\varepsilon
  \]

### 5.2 - Bézier cúbica por formulación de Bernstein
- **Python:** construir

  \[
  \vec{P}(u)=\sum_{i=0}^{3}\vec{P}_i\,B_{i,3}(u)
  \]
- **Comparación:** superponer con una curva Bézier creada con controles equivalentes en Blender.
- **Objetivo:** equivalencia entre implementación Bernstein y curva Bézier en Blender.

### 5.3 - Tangentes en extremos y relación con handles
- **Python:** verificar

  \[
  \vec{P}'(0)=3(\vec{P}_1-\vec{P}_0)
  \]
  \[
  \vec{P}'(1)=3(\vec{P}_3-\vec{P}_2)
  \]
- **Visualización:** flechas tangentes y handles.
- **Verificación (checker):** diferencia angular menor que \(\varepsilon\).

---

## Bloque 6 - Splines y continuidad: \(C^0\), \(G^1\) y aproximación de \(C^1\)

### 6.1 - Unión de dos tramos: \(C^0\) y aparición de quiebro
- **Interfaz (UI):** unir tramos con punto común y handles desalineados; observar discontinuidad.
- **Python:** medir tangentes a izquierda y derecha del empalme.

### 6.2 - Continuidad geométrica \(G^1\) en Blender
- **Interfaz (UI):** alinear handles en la unión (misma dirección tangente).
- **Python:** comprobar proporcionalidad (ángulo cercano a 0).
- **Verificación (checker):** \(\angle(T_{left},T_{right})<\varepsilon\).

### 6.3 - Aproximación de continuidad \(C^1\)
- **Interfaz (UI):** ajustar longitudes de handles para aproximar igualdad de tangentes.
- **Python:** comprobar igualdad aproximada.
- **Verificación (checker):** \(\|T_{left}-T_{right}\|<\varepsilon\).

### 6.4 - Test de continuidad (splines y derivadas)
- **Objetivo:** manipular tangentes para comprender suavidad \(G^1\) y aproximación de \(C^1\).
- **Tarea:** modificar el vector tangente del segundo tramo para que sea proporcional al del primero.
- **Conexión teórica:** continuidad geométrica \(G^1\) como criterio suficiente para suavidad perceptual.

---

## Licencia y contribuciones
- La licencia del repositorio se especifica en `LICENSE`.
- Se aceptan contribuciones mediante *pull requests* siguiendo el estilo de carpetas y nomenclatura establecida.


