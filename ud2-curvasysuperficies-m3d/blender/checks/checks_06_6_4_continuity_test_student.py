import bpy
from mathutils import Vector
import math

ANGLE_EPS_DEG = 3.0
MAG_REL_EPS = 0.08
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

def rel_mag_diff(a: float, b: float) -> float:
    return abs(a - b) / max(EPS, 0.5 * (a + b))

def main() -> None:
    ctrl = bpy.data.objects.get("ContinuityControl")
    obj = bpy.data.objects.get("SplineContinuityTest")
    if ctrl is None or obj is None or obj.type != "CURVE":
        raise RuntimeError("No se encontró el setup del lab 06.6.4. Ejecuta primero el script del ejercicio.")

    mode = int(ctrl.get("mode", 0))
    mode = max(0, min(2, mode))

    spline = obj.data.splines[0]
    TL = tangent_left_at_join(spline)
    TR = tangent_right_at_join(spline)

    ang = angle_between(TL, TR)
    rel = rel_mag_diff(TL.length, TR.length)

    print("=== Checker Lab 06.6.4 — Test de continuidad ===")
    print(f"mode = {mode}")
    print(f"angle(T_left, T_right) = {ang:.6f} deg (umbral {ANGLE_EPS_DEG:.3f})")
    print(f"rel_mag_diff = {rel:.6f} (umbral {MAG_REL_EPS:.3f} para C1)")

    if mode == 0:
        print("RESULTADO: FAIL")
        print("Selecciona mode=1 (G1) o mode=2 (C1) en ContinuityControl.")
        return

    ok_angle = ang < ANGLE_EPS_DEG
    if mode == 1:
        if ok_angle:
            print("RESULTADO: PASS (G1)")
        else:
            print("RESULTADO: FAIL (G1)")
            print("Se requiere alinear tangentes (ángulo pequeño).")
        return

    # mode == 2
    ok_mag = rel < MAG_REL_EPS
    if ok_angle and ok_mag:
        print("RESULTADO: PASS (C1)")
    else:
        print("RESULTADO: FAIL (C1)")
        if not ok_angle:
            print("- Ajuste: alinear direcciones (G1).")
        if not ok_mag:
            print("- Ajuste: igualar magnitudes (C1).")

if __name__ == "__main__":
    main()

