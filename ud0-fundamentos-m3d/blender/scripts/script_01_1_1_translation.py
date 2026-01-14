"""
Lab 01.1.1 — Traslación como suma de vectores
=============================================

Objetivo
--------
Visualizar y verificar en Blender que una traslación es una suma vectorial:
    P' = P + t

Guía UI (parte manual)
----------------------
1) Ejecutar este script. Al iniciarse:
   - eliminará todos los objetos existentes en la escena (incluidos los objetos por defecto)
   - creará una colección "Lab01_1_1_Translation" con:
       P         : punto de referencia (Empty)
       P_target  : objetivo (Empty) en la posición P + t
       P_user    : punto editable por el usuario (Empty), inicialmente en P
       t_vector  : flecha que representa el vector t aplicado desde P

2) Seleccionar "P_user" y moverlo (G) hasta coincidir con "P_target".

3) Ejecutar el checker:
   - check_01_1_1_translation.py
   Valida: dist(P_user, P_target) < EPS

Mini-diagrama ASCII
-------------------
P_user  ---- mover ---->   P_target
  |
  |  t (vector)
  v
P  + t

Notas técnicas
--------------
- Este script garantiza que cada objeto pertenece únicamente a la colección del laboratorio.
- Para asegurar reproducibilidad, se elimina el contenido previo del viewport al iniciar.
"""

import bpy
from mathutils import Vector

LAB_COLLECTION_NAME = "Lab01_1_1_Translation"

P_LOC = Vector((0.0, 0.0, 0.0))
T_VEC = Vector((2.0, 1.0, 0.0))

ARROW_SHAFT_RADIUS = 0.03
ARROW_HEAD_RADIUS = 0.08
ARROW_HEAD_LENGTH = 0.25


# -----------------------------
# Utilidades de limpieza total
# -----------------------------
def wipe_scene() -> None:
    """
    Elimina todos los objetos existentes en la escena activa.
    También limpia colecciones auxiliares vacías y datos huérfanos básicos.
    """
    # Asegurar modo OBJECT para poder borrar
    try:
        if bpy.context.object and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass

    # Seleccionar y borrar todos los objetos
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False, confirm=False)

    # Eliminar colecciones hijas de la colección de la escena (si quedaran vacías)
    master = bpy.context.scene.collection
    for child in list(master.children):
        master.children.unlink(child)
        try:
            bpy.data.collections.remove(child)
        except Exception:
            pass

    # Limpieza de datablocks comunes (por si queda algo suelto)
    for datablock in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.images, bpy.data.objects):
        for block in list(datablock):
            if block.users == 0:
                try:
                    datablock.remove(block)
                except Exception:
                    pass


# -----------------------------
# Colecciones y creación segura
# -----------------------------
def ensure_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def move_object_to_collection_only(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    """
    Asegura que 'obj' está linkado únicamente a 'target' (una sola colección).
    Esto evita duplicados en el Outliner.
    """
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target.objects.link(obj)


def create_empty_in_collection(
    col: bpy.types.Collection,
    name: str,
    location: Vector,
    display: str = "SPHERE",
    size: float = 0.25,
) -> bpy.types.Object:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = display
    empty.empty_display_size = size
    empty.location = location
    col.objects.link(empty)
    return empty


def create_cylinder(name: str, radius: float, depth: float) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    return obj


def create_cone(name: str, radius: float, depth: float) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=0.0, depth=depth, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    return obj


def orient_object_from_z_axis(obj: bpy.types.Object, direction: Vector) -> None:
    d = direction.normalized()
    z_axis = Vector((0.0, 0.0, 1.0))
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = z_axis.rotation_difference(d)


def create_vector_arrow(col: bpy.types.Collection, name: str, start: Vector, vec: Vector) -> bpy.types.Object:
    length = vec.length
    if length < 1e-9:
        return create_empty_in_collection(col, name, start, display="ARROWS", size=0.4)

    arrow_root = bpy.data.objects.new(name, None)
    arrow_root.empty_display_type = "PLAIN_AXES"
    arrow_root.location = start
    col.objects.link(arrow_root)

    shaft_len = max(0.0, length - ARROW_HEAD_LENGTH)
    head_len = min(ARROW_HEAD_LENGTH, length)

    shaft = create_cylinder(f"{name}_shaft", ARROW_SHAFT_RADIUS, shaft_len)
    head = create_cone(f"{name}_head", ARROW_HEAD_RADIUS, head_len)

    # Evitar duplicación en colecciones: mover solo al lab
    move_object_to_collection_only(shaft, col)
    move_object_to_collection_only(head, col)

    shaft.location = Vector((0.0, 0.0, shaft_len / 2.0))
    head.location = Vector((0.0, 0.0, shaft_len + head_len / 2.0))

    shaft.parent = arrow_root
    head.parent = arrow_root

    orient_object_from_z_axis(arrow_root, vec)
    return arrow_root


def main() -> None:
    # 1) Limpiar escena completa para reproducibilidad
    wipe_scene()

    # 2) Crear colección del laboratorio
    col = ensure_collection(LAB_COLLECTION_NAME)

    # 3) Crear objetos del ejercicio
    create_empty_in_collection(col, "P", P_LOC, display="SPHERE", size=0.22)
    create_empty_in_collection(col, "P_target", P_LOC + T_VEC, display="CUBE", size=0.22)
    create_empty_in_collection(col, "P_user", P_LOC, display="SPHERE", size=0.26)
    create_vector_arrow(col, "t_vector", P_LOC, T_VEC)

    print("=== Lab 01.1.1 — Traslación como suma de vectores ===")
    print("La escena previa ha sido eliminada.")
    print(f"P      = {tuple(P_LOC)}")
    print(f"t      = {tuple(T_VEC)}")
    print(f"P+t    = {tuple(P_LOC + T_VEC)}")
    print("Acción: mueve 'P_user' hasta coincidir con 'P_target' y ejecuta el checker.")
    print("Colección creada:", LAB_COLLECTION_NAME)


if __name__ == "__main__":
    main()

