import bpy
from mathutils import Vector
import math

EPS_NONZERO = 1e-9

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def plane_world_normal(plane_obj: bpy.types.Object) -> Vector:
    n = plane_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))
    return n.normalized() if n.length > EPS_NONZERO else Vector((0.0, 0.0, 1.0))

def light_world_direction(light_empty: bpy.types.Object) -> Vector:
    l = light_empty.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))
    return l.normalized() if l.length > EPS_NONZERO else Vector((0.0, 0.0, -1.0))

def main() -> None:
    plane = bpy.data.objects.get("LambertPlane")
    light = bpy.data.objects.get("Light_dir")
    if plane is None or light is None:
        raise RuntimeError("No se encontraron 'LambertPlane' y 'Light_dir'. Ejecuta primero el script del lab 02.2.3.")

    N = plane_world_normal(plane)
    L = light_world_direction(light)
    dot = clamp(N.dot(L), -1.0, 1.0)
    I = max(0.0, dot)

    print("=== Checker Lab 02.2.3 — Lambert con normales ===")
    print(f"N = {tuple(N)}")
    print(f"L = {tuple(L)}")
    print(f"N·L = {dot:.6f}")
    print(f"I = max(0, N·L) = {I:.6f}")
    print("RESULTADO: PASS (checker informativo).")

if __name__ == "__main__":
    main()

