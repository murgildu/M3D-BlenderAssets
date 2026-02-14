import bpy

MIN_POINTS = 50  # umbral suave; depende de GRID_RES y EPS

def main() -> None:
    obj = bpy.data.objects.get("ImplicitCirclePoints")
    if obj is None or obj.type != "MESH":
        raise RuntimeError("No se encontró 'ImplicitCirclePoints'. Ejecuta primero el script del lab 03.3.2.")

    n = len(obj.data.vertices)

    print("=== Checker Lab 03.3.2 — Curva implícita (círculo) ===")
    print(f"Vertices (puntos) = {n}")

    if n >= MIN_POINTS:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        print("Pocos puntos detectados. Sugerencia: aumentar GRID_RES o EPS.")

if __name__ == "__main__":
    main()

