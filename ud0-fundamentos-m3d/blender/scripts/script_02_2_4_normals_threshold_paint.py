"""
Lab 02.2.4 — Normales y shading: pintar por umbral usando N·L
=============================================================

Objetivo
--------
Aplicar el producto escalar a un caso típico de shading:
- Para cada cara (polígono) de una malla, calcular N·L.
- Marcar/pintar aquellas caras con N·L > threshold.

Modelo teórico
--------------
- N: normal unitaria de la cara (en mundo)
- L: dirección unitaria hacia la luz (en mundo)
- dot = N·L = cos(theta)
- Condición de iluminación "fuerte": N·L > threshold

Guía UI
-------
1) Ejecutar este script (elimina la escena y crea el laboratorio).
2) Rotar "Light_dir" (R) para cambiar la dirección de la luz.
3) Observar cómo cambia qué caras se pintan.

IMPORTANTE (visualización de colores por atributo)
--------------------------------------------------
Este ejercicio usa un "Color Attribute" (atributo de color en la malla).

Para verlo en el Viewport:
1) Modo SOLID.
2) Menú del shading (esfera arriba derecha).
3) En "Color", seleccionar "Attribute".
4) En "Attribute", elegir el atributo "lambert_mask" si aparece un selector,
   o en versiones recientes se toma automáticamente el activo.

Si se deja "Color" en "Material" u otro modo, no se apreciará el coloreado.

Salida
------
- Caras con N·L > threshold -> rojo
- Resto -> azul
"""

import bpy
import blf
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab02_2_4_NormalsThreshold"

# Umbral del ejercicio
THRESHOLD = 0.5

# HUD / timers
_HANDLER_KEY = "LAB02_2_4_THRESHOLD_DRAW_HANDLER"
_TIMER_KEY = "LAB02_2_4_TIMER_REGISTERED"

KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
    "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER",
    "LAB01_1_4_VECTOR_INSPECTOR_DRAW_HANDLER",
    "LAB02_2_1_DOT_ALIGNMENT_DRAW_HANDLER",
    "LAB02_2_2_ORTHO2D_DRAW_HANDLER",
    "LAB02_2_3_LAMBERT_DRAW_HANDLER",
    "LAB02_2_4_THRESHOLD_DRAW_HANDLER",
]

EPS_NONZERO = 1e-9


# -----------------------------
# Limpieza HUD persistente
# -----------------------------
def remove_handler_by_key(key: str) -> None:
    ns = bpy.app.driver_namespace
    handler = ns.get(key)
    if handler is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(handler, "WINDOW")
        except Exception:
            pass
        ns.pop(key, None)

def remove_all_known_lab_handlers() -> None:
    for k in KNOWN_HANDLER_KEYS:
        remove_handler_by_key(k)


# -----------------------------
# Limpieza escena
# -----------------------------
def wipe_scene() -> None:
    try:
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False, confirm=False)

    master = bpy.context.scene.collection
    for child in list(master.children):
        master.children.unlink(child)
        try:
            bpy.data.collections.remove(child)
        except Exception:
            pass

    for datablock in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.images, bpy.data.objects, bpy.data.lights):
        for block in list(datablock):
            if block.users == 0:
                try:
                    datablock.remove(block)
                except Exception:
                    pass


# -----------------------------
# Colecciones
# -----------------------------
def ensure_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

def move_object_to_collection_only(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target.objects.link(obj)


# -----------------------------
# HUD
# -----------------------------
def _draw_text(x: int, y: int, text: str, size: int = 14) -> None:
    font_id = 0
    ui_scale = bpy.context.preferences.system.ui_scale
    blf.size(font_id, int(size * ui_scale))
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# -----------------------------
# Direcciones N y L
# -----------------------------
def light_world_direction(light_empty: bpy.types.Object) -> Vector:
    # Eje -Z local en mundo
    l = light_empty.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))
    return l.normalized() if l.length > EPS_NONZERO else Vector((0.0, 0.0, -1.0))


# -----------------------------
# Color Attributes (por esquina / face-corner)
# -----------------------------
def ensure_color_attribute(mesh: bpy.types.Mesh, name: str = "lambert_mask") -> bpy.types.Attribute:
    """
    Crea o recupera un atributo de color.
    Usamos dominio CORNER para poder colorear caras sin interpolación rara.
    """
    attr = mesh.attributes.get(name)
    if attr is None:
        attr = mesh.attributes.new(name=name, type='FLOAT_COLOR', domain='CORNER')
    mesh.attributes.active = attr
    return attr


def paint_mesh_by_threshold(obj: bpy.types.Object, L: Vector, threshold: float) -> tuple[int, int]:
    """
    Colorea cada cara en rojo si N·L > threshold, en azul si no.
    Devuelve: (num_rojas, num_total)
    """
    mesh = obj.data
    attr = ensure_color_attribute(mesh, "lambert_mask")
    colors = attr.data  # longitud = num_loops (corners)

    # Precomputar normales de polígonos en mundo:
    # poly.normal es local; a mundo: R * normal
    R = obj.matrix_world.to_3x3()
    red = (1.0, 0.0, 0.0, 1.0)
    blue = (0.0, 0.0, 1.0, 1.0)

    count_red = 0
    total = len(mesh.polygons)

    for poly in mesh.polygons:
        Nw = (R @ poly.normal)
        if Nw.length > EPS_NONZERO:
            Nw.normalize()
        dot = clamp(Nw.dot(L), -1.0, 1.0)

        col = red if dot > threshold else blue
        if dot > threshold:
            count_red += 1

        # Pintar todos los corners (loops) de esta cara con el mismo color
        for li in poly.loop_indices:
            colors[li].color = col

    return count_red, total


def _hud_draw_callback() -> None:
    x0, y0 = 20, 150
    line = 18

    _draw_text(x0, y0 + 5 * line, "Lab 02.2.4 — Pintar caras por umbral N·L", size=16)
    _draw_text(x0, y0 + 4 * line, "Acción: rotar 'Light_dir' (R) y observar qué caras pasan el umbral", size=13)
    _draw_text(x0, y0 + 3 * line, f"Umbral: N·L > {THRESHOLD:.2f}  -> rojo (si no, azul)", size=13)

    obj = bpy.data.objects.get("MaskMesh")
    light = bpy.data.objects.get("Light_dir")
    if obj is None or light is None:
        _draw_text(x0, y0 + 2 * line, "Estado: objetos no encontrados (ejecutar el script).", size=13)
        return

    L = light_world_direction(light)
    # stats calculadas por el timer (si existen)
    stats = bpy.app.driver_namespace.get("LAB02_2_4_STATS", None)
    if stats is not None:
        count_red, total = stats
        _draw_text(x0, y0 + 2 * line, f"Caras rojas: {count_red}/{total}", size=13)

    _draw_text(x0, y0 + 1 * line, f"L (dir luz) = ({L.x:.3f}, {L.y:.3f}, {L.z:.3f})", size=13)
    _draw_text(x0, y0 + 0 * line, "Viewport: Solid -> Color: Attribute (ver nota al inicio)", size=13)


def _install_hud_handler() -> None:
    remove_all_known_lab_handlers()
    handler = bpy.types.SpaceView3D.draw_handler_add(_hud_draw_callback, (), "WINDOW", "POST_PIXEL")
    bpy.app.driver_namespace[_HANDLER_KEY] = handler


def _tag_redraw_all_3dviews() -> None:
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


# -----------------------------
# Timer
# -----------------------------
def _unregister_timer_if_needed():
    ns = bpy.app.driver_namespace
    if ns.get(_TIMER_KEY, False):
        if bpy.app.timers.is_registered(_update_scene):
            try:
                bpy.app.timers.unregister(_update_scene)
            except Exception:
                pass
        ns[_TIMER_KEY] = False


def _update_scene():
    obj = bpy.data.objects.get("MaskMesh")
    light = bpy.data.objects.get("Light_dir")
    if obj is None or light is None:
        return 0.1

    L = light_world_direction(light)
    stats = paint_mesh_by_threshold(obj, L, THRESHOLD)
    bpy.app.driver_namespace["LAB02_2_4_STATS"] = stats

    _tag_redraw_all_3dviews()
    return 0.10  # no hace falta 20fps; 10Hz suficiente


# -----------------------------
# Creación escena
# -----------------------------
def create_scene_demo() -> None:
    col = ensure_collection(LAB_COLLECTION_NAME)

    # Malla: icosfera para tener muchas caras
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=(0.0, 0.0, 0.0))
    obj = bpy.context.active_object
    obj.name = "MaskMesh"
    move_object_to_collection_only(obj, col)

    # Empty dirección de luz
    light = bpy.data.objects.new("Light_dir", None)
    light.empty_display_type = "ARROWS"
    light.empty_display_size = 0.7
    light.location = Vector((3.0, 0.0, 2.0))
    light.rotation_euler = (math.radians(65.0), 0.0, math.radians(30.0))
    col.objects.link(light)
    move_object_to_collection_only(light, col)

    # Selección: facilitar rotación de la luz
    bpy.ops.object.select_all(action="DESELECT")
    light.select_set(True)
    bpy.context.view_layer.objects.active = light


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    remove_all_known_lab_handlers()
    _unregister_timer_if_needed()
    wipe_scene()
    create_scene_demo()

    _install_hud_handler()
    _tag_redraw_all_3dviews()

    bpy.app.timers.register(_update_scene)
    bpy.app.driver_namespace[_TIMER_KEY] = True

    print("=== Lab 02.2.4 — Pintar caras por umbral N·L ===")
    print("La escena previa ha sido eliminada.")
    print("Objetos creados: MaskMesh (icosphere), Light_dir (rotar).")
    print("Para ver colores: Solid -> Color: Attribute (ver nota en el script).")
    print(f"Umbral: N·L > {THRESHOLD:.2f} -> rojo, si no azul.")


if __name__ == "__main__":
    main()

