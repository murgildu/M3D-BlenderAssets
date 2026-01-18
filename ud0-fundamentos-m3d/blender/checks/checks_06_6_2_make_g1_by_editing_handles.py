import bpy
from mathutils import Vector
import math

ANGLE_EPS_DEG = 3.0
EPS = 1e-12

def tangent_left_at_join(spline) -> Vector:
    bp1 = spline.bezier_points[1]
    return 3.0 * (bp1.co - bp1.handle_left)

def tangent_right_at_join(spline) -> Vector:
    bp1 = spline.bezier_points[1]
    return 3.0 * (bp1.handle_right - bp1.co)

def angle_between(u: Vector, v: Vector) -> float:
    if u.length < EPS or v.length < EPS:
        return 0.0
    d = max(-1.0, min(1.0, u.normalized().dot(v.normalized())))
    return math.degrees(math.acos(d))

def main() -> None:
    obj = bpy.data.objects.get("SplineG1Task")
    if obj is None or obj.type != "CURVE":
        raise RuntimeError("No se encontró 'SplineG1Task'. Ejecuta primero el lab 06.6.2.")

    spline = obj.data.splines[0]
    TL = tangent_left_at_join(spline)
    TR = tangent_right_at_join(spline)

    ang = angle_between(TL, TR)

    print("=== Checker Lab 06.6.2 — G1 por edición de handles ===")
    print(f"angle(T_left, T_right) = {ang:.6f} deg")
    print(f"umbral = {ANGLE_EPS_DEG:.3f} deg")

    if ang < ANGLE_EPS_DEG:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        print("Sugerencia: en Edit Mode, alinear handles del punto central (misma dirección).")

if __name__ == "__main__":
    main()

