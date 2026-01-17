import bpy
from mathutils import Vector
import math

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def world_local_y_axis(obj: bpy.types.Object) -> Vector:
    return (obj.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()

def main() -> None:
    U = bpy.data.objects.get("U_ref")
    V = bpy.data.objects.get("V_dir")
    if U is None or V is None:
        raise RuntimeError("No se encontraron 'U_ref' y 'V_dir'. Ejecuta primero el script del lab 02.2.1.")

    u = world_local_y_axis(U)
    v = world_local_y_axis(V)

    dot = clamp(u.dot(v), -1.0, 1.0)
    ang_deg = math.degrees(math.acos(dot))

    print("=== Checker Lab 02.2.1 — Dot product (alineamiento) ===")
    print(f"dot(u,v) = {dot:.6f}")
    print(f"angle(u,v) = {ang_deg:.3f} deg")
    print("RESULTADO: PASS (checker informativo).")

if __name__ == "__main__":
    main()

