import bpy
from mathutils import Vector

THRESHOLD = 0.5
EPS_NONZERO = 1e-9

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def light_world_direction(light_empty: bpy.types.Object) -> Vector:
    l = light_empty.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))
    return l.normalized() if l.length > EPS_NONZERO else Vector((0.0, 0.0, -1.0))

def main() -> None:
    obj = bpy.data.objects.get("MaskMesh")
    light = bpy.data.objects.get("Light_dir")
    if obj is None or light is None:
        raise RuntimeError("No se encontraron 'MaskMesh' y 'Light_dir'. Ejecuta primero el script del lab 02.2.4.")

    mesh = obj.data
    R = obj.matrix_world.to_3x3()
    L = light_world_direction(light)

    count = 0
    for poly in mesh.polygons:
        Nw = R @ poly.normal
        if Nw.length > EPS_NONZERO:
            Nw.normalize()
        dot = clamp(Nw.dot(L), -1.0, 1.0)
        if dot > THRESHOLD:
            count += 1

    print("=== Checker Lab 02.2.4 — Pintar caras por umbral N·L ===")
    print(f"Umbral = {THRESHOLD}")
    print(f"Caras con N·L > umbral: {count}/{len(mesh.polygons)}")
    print("RESULTADO: PASS (checker informativo).")

if __name__ == "__main__":
    main()

