import bpy

def main() -> None:
    obj = bpy.data.objects.get("ParametricCircle")
    if obj is None or obj.type != "MESH":
        raise RuntimeError("No se encontró 'ParametricCircle'. Ejecuta primero el script del lab 03.3.3.")

    mesh = obj.data
    v = len(mesh.vertices)
    e = len(mesh.edges)

    print("=== Checker Lab 03.3.3 — Curva paramétrica (círculo) ===")
    print(f"Vertices: {v}")
    print(f"Edges:    {e}")

    # Esperado: polilínea cerrada con una arista por vértice
    if v >= 3 and e == v:
        print("RESULTADO: PASS")
    else:
        print("RESULTADO: FAIL")
        print("Condición esperada: vertices >= 3 y edges == vertices (polilínea cerrada).")

if __name__ == "__main__":
    main()

