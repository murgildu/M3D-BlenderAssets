import bpy

EXPECTED_MIN_POINTS = 50  # umbral suave (depende del script, pero debe ser alto)

def main() -> None:
    obj = bpy.data.objects.get("HelixCurve")
    if obj is None or obj.type != "CURVE":
        raise RuntimeError("No se encontró el objeto Curve 'HelixCurve'. Ejecuta primero el script del lab 03.3.4.")

    curve = obj.data
    if not curve.splines:
        print("=== Checker Lab 03.3.4 — Hélice paramétrica ===")
        print("RESULTADO: FAIL (no hay splines en la curva).")
        return

    spline = curve.splines[0]
    n = len(spline.points)

    print("=== Checker Lab 03.3.4 — Hélice paramétrica (Curve object) ===")
    print(f"Spline type: {spline.type}")
    print(f"Puntos en spline: {n}")

    if n >= EXPECTED_MIN_POINTS:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        print("Pocos puntos detectados. Recomendación: aumentar N_SAMPLES.")

if __name__ == "__main__":
    main()

