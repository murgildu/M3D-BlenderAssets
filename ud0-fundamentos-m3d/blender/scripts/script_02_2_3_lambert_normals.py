"""
Lab 02.2.3 — Shading Lambert con normales (experimento controlado)
==================================================================

Modelo teórico
--------------
Lambert (difuso ideal):
    I = max(0, N · L)
donde:
- N es la normal unitaria de la superficie (en mundo)
- L es la dirección unitaria hacia la luz (en mundo)
- I es la intensidad difusa (0..1)

Guía UI
-------
1) Ejecutar este script:
   - elimina la escena
   - crea un plano (Plane) y un objeto "Light_dir" (Empty con ejes)
   - activa HUD y actualización en tiempo real
2) Rotar el plano (R) o rotar "Light_dir" (R).
3) Observar:
   - el plano cambia de color según I
   - el HUD muestra N, L, N·L e I


IMPORTANTE (visualización del color)
-----------------------------------
Este ejercicio cambia el color del plano usando "Object Color" (Viewport Display).

Para ver el color en el Viewport:
1) Poner el viewport en modo SOLID.
2) Abrir el menú del shading (icono de esfera arriba a la derecha).
3) En "Color", seleccionar "Object".

Si "Color" está en "Material" u otro modo, el cambio de color no se apreciará.

Convenciones usadas
-------------------
- N: normal del plano en mundo (derivada de su matriz)
- L: dirección de la luz en mundo tomada como el eje -Z local de Light_dir
  (similar a una luz direccional apuntando hacia -Z local)
"""

import bpy
import blf
from mathutils import Vector
import math

LAB_COLLECTION_NAME = "Lab02_2_3_LambertNormals"

_HANDLER_KEY = "LAB02_2_3_LAMBERT_DRAW_HANDLER"
KNOWN_HANDLER_KEYS = [
    "LAB01_1_1_TRANSLATION_DRAW_HANDLER",
    "LAB01_1_2_SCALEPIVOT_DRAW_HANDLER",
    "LAB01_1_3_NORM_NORMALIZE_DRAW_HANDLER",
    "LAB01_1_4_VECTOR_INSPECTOR_DRAW_HANDLER",
    "LAB02_2_1_DOT_ALIGNMENT_DRAW_HANDLER",
    "LAB02_2_2_ORTHO2D_DRAW_HANDLER",
    "LAB02_2_3_LAMBERT_DRAW_HANDLER",
]

EPS_NONZERO = 1e-9
_TIMER_KEY = "LAB02_2_3_TIMER_REGISTERED"


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
# Cálculos de N y L
# -----------------------------
def plane_world_normal(plane_obj: bpy.types.Object) -> Vector:
    """
    Normal del plano en mundo.
    Para el plano de Blender, la normal local por defecto apunta en +Z local.
    En mundo: N = R * (0,0,1).
    """
    n = plane_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
    if n.length < EPS_NONZERO:
        return Vector((0.0, 0.0, 1.0))
    return n.normalized()

def light_world_direction(light_empty: bpy.types.Object) -> Vector:
    """
    Dirección de la luz en mundo: eje -Z local del Empty.
    """
    z_local = Vector((0.0, 0.0, -1.0))
    l = light_empty.matrix_world.to_3x3() @ z_local
    if l.length < EPS_NONZERO:
        return Vector((0.0, 0.0, -1.0))
    return l.normalized()

def lambert_intensity(N: Vector, L: Vector) -> float:
    return max(0.0, clamp(N.dot(L), -1.0, 1.0))


# -----------------------------
# Coloreado simple en viewport
# -----------------------------
def set_object_viewport_color(obj: bpy.types.Object, intensity: float) -> None:
    """
    Mapea intensidad I en [0,1] a un gradiente azul->rojo (muy visible).
    - I = 0  -> azul
    - I = 1  -> rojo

    Se aplica una curva de contraste para que se note más en pantallas pequeñas.
    """
    I = float(clamp(intensity, 0.0, 1.0))

    # Curva de contraste (ajusta si quieres):
    # - exponent < 1  => realza diferencias cerca de 0 (más "radical" al inicio)
    # - exponent > 1  => realza diferencias cerca de 1
    exponent = 0.6
    I = I ** exponent

    # Gradiente: azul -> rojo
    r = I
    g = 0.0
    b = 1.0 - I

    obj.color = (r, g, b, 1.0)



# -----------------------------
# HUD callback
# -----------------------------
def _hud_draw_callback() -> None:
    x0, y0 = 20, 150
    line = 18

    _draw_text(x0, y0 + 6 * line, "Lab 02.2.3 — Lambert (I = max(0, N·L))", size=16)
    _draw_text(x0, y0 + 5 * line, "Acción: rotar el plano o 'Light_dir' (R)", size=13)

    plane = bpy.data.objects.get("LambertPlane")
    light = bpy.data.objects.get("Light_dir")
    if plane is None or light is None:
        _draw_text(x0, y0 + 4 * line, "Estado: objetos no encontrados (ejecutar el script).", size=13)
        return

    N = plane_world_normal(plane)
    L = light_world_direction(light)
    dot = clamp(N.dot(L), -1.0, 1.0)
    I = max(0.0, dot)

    _draw_text(x0, y0 + 4 * line, f"N (normal) = ({N.x:.3f}, {N.y:.3f}, {N.z:.3f})", size=13)
    _draw_text(x0, y0 + 3 * line, f"L (dir luz) = ({L.x:.3f}, {L.y:.3f}, {L.z:.3f})", size=13)
    _draw_text(x0, y0 + 2 * line, f"N·L = {dot:.4f}", size=13)
    _draw_text(x0, y0 + 1 * line, f"I = max(0, N·L) = {I:.4f}", size=13)
    _draw_text(x0, y0 + 0 * line, "Interpretación: 0=sin luz directa, 1=incidencia perpendicular", size=13)


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
# Timer: actualizar color continuamente
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
    plane = bpy.data.objects.get("LambertPlane")
    light = bpy.data.objects.get("Light_dir")
    if plane is None or light is None:
        return 0.1

    N = plane_world_normal(plane)
    L = light_world_direction(light)
    I = lambert_intensity(N, L)

    set_object_viewport_color(plane, I)
    _tag_redraw_all_3dviews()
    return 0.05


# -----------------------------
# Creación escena
# -----------------------------
def create_scene_demo() -> None:
    col = ensure_collection(LAB_COLLECTION_NAME)

    # Plano
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0.0, 0.0, 0.0))
    plane = bpy.context.active_object
    plane.name = "LambertPlane"
    move_object_to_collection_only(plane, col)

    # Empty dirección de luz
    light = bpy.data.objects.new("Light_dir", None)
    light.empty_display_type = "ARROWS"
    light.empty_display_size = 0.6
    light.location = Vector((3.0, 0.0, 1.5))
    # Rotación inicial: apuntar ligeramente hacia el plano
    light.rotation_euler = (math.radians(60.0), 0.0, math.radians(20.0))
    col.objects.link(light)
    move_object_to_collection_only(light, col)

    # Selección: facilitar rotación de Light_dir
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

    print("=== Lab 02.2.3 — Lambert con normales ===")
    print("La escena previa ha sido eliminada.")
    print("Objetos creados: LambertPlane, Light_dir.")
    print("Acción: rota el plano o Light_dir y observa el cambio de I (HUD) y el color del plano.")


if __name__ == "__main__":
    main()

