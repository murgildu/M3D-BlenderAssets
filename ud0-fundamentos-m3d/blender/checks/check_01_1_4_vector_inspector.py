import bpy
from mathutils import Vector
import math

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def world_local_y_axis(obj: bpy.types.Object) -> Vector:
    return (obj.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()

def main() -> None:
    A = bpy.data.objects.get("A")
    B = bpy.data.objects.get("B")
    if A is None or B is None:
        raise RuntimeError("No se encontraron objetos 'A' y 'B'. Ejecuta primero el script del lab 01.1.4.")

    a_loc = Vector(A.location)
    b_loc = Vector(B.location)
    d = b_loc - a_loc
    dist = d.length

    YA = world_local_y_axis(A)
    YB = world_local_y_axis(B)

    dot = clamp(YA.dot(YB), -1.0, 1.0)
    ang_deg = math.degrees(math.acos(dot))

    print("=== Checker Lab 01.1.4 — Inspector de Vectores ===")
    print(f"d = B - A = {tuple(d)}")
    print(f"|d| = {dist:.6f}")
    print(f"dot(YA,YB) = {dot:.6f}")
    print(f"angle(YA,YB) = {ang_deg:.3f} deg")
    print("RESULTADO: PASS (checker informativo).")

if __name__ == "__main__":
    main()

