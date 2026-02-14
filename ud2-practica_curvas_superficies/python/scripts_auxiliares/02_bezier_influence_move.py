# -*- coding: utf-8 -*-
"""
02_bezier_influence_move.py
===========================

Objetivo
--------
1) Implementar evaluación de una Bézier por fórmula (Bernstein).
2) Mostrar el efecto de mover un punto de control:
      q(u) - p(u)  ≈  B_{idx,n}(u) * v

Dependencias
-----------
- math
- numpy
- matplotlib

Ejecución
---------
python 02_bezier_influence_move.py

Qué extraer para Blender
------------------------
- bernstein(n, i, u)
- bezier_point(P, u)
- influence_of_control_move(P, idx, v, u)
"""

import math
import numpy as np
import matplotlib.pyplot as plt


def bernstein(n: int, i: int, u: float) -> float:
    """B_{i,n}(u) = C(n,i) u^i (1-u)^(n-i)."""
    return math.comb(n, i) * (u ** i) * ((1.0 - u) ** (n - i))


def bezier_point(P: np.ndarray, u: float) -> np.ndarray:
    """
    Evalúa una curva de Bézier definida por puntos de control P (shape: (n+1, dim))
    usando la fórmula explícita con Bernstein.

    P:
      - array con n+1 puntos de control
      - dim=2 ó dim=3 (o más)
    """
    n = len(P) - 1
    out = np.zeros(P.shape[1], dtype=float)
    for i in range(n + 1):
        out += bernstein(n, i, u) * P[i]
    return out


def bezier_curve(P: np.ndarray, num_samples: int = 200) -> np.ndarray:
    """Muestrea la curva Bézier en 'num_samples' valores de u entre 0 y 1."""
    u_values = np.linspace(0.0, 1.0, num_samples)
    curve = np.array([bezier_point(P, u) for u in u_values], dtype=float)
    return curve


def influence_of_control_move(P: np.ndarray, idx_moved: int, v: np.ndarray, u: float):
    """
    Mueve el punto de control P[idx_moved] por el vector v y compara:

    - p(u) = Bézier(P, u)
    - q(u) = Bézier(P_mod, u) donde P_mod[idx]+=v
    - desplazamiento real: q(u)-p(u)
    - desplazamiento esperado: B_{idx,n}(u) * v

    Devuelve diccionario con resultados numéricos.
    """
    n = len(P) - 1
    p_u = bezier_point(P, u)

    P_mod = P.copy()
    P_mod[idx_moved] = P_mod[idx_moved] + v
    q_u = bezier_point(P_mod, u)

    coeff = bernstein(n, idx_moved, u)
    expected = coeff * v
    real = q_u - p_u

    return {
        "p_u": p_u,
        "q_u": q_u,
        "coeff": coeff,
        "expected": expected,
        "real": real,
        "dist_real": float(np.linalg.norm(real)),
        "dist_control": float(np.linalg.norm(v)),
        "P_mod": P_mod,
    }


def main():
    # Curva cúbica (4 puntos) en 2D
    P = np.array([
        [0.0, 0.0],    # P0
        [1.0, 3.0],    # P1
        [4.0, 3.0],    # P2
        [5.0, 0.0]     # P3
    ], dtype=float)

    u = 0.5
    idx_moved = 2
    v = np.array([0.0, 2.0], dtype=float)

    r = influence_of_control_move(P, idx_moved, v, u)

    print("[Influence] Curva Bézier cúbica")
    print("  u =", u)
    print("  idx moved =", idx_moved)
    print("  p(u) =", r["p_u"])
    print("  q(u) =", r["q_u"])
    print("  coeff B_idx,n(u) =", r["coeff"])
    print("  real displacement =", r["real"])
    print("  expected coeff*v  =", r["expected"])
    if r["dist_control"] > 1e-12:
        print("  % movement =", 100.0 * r["dist_real"] / r["dist_control"])

    # Curvas completa (antes/después)
    curve_original = bezier_curve(P, 200)
    curve_mod = bezier_curve(r["P_mod"], 200)

    # Dibujo
    plt.figure(figsize=(10, 6))
    plt.plot(curve_original[:, 0], curve_original[:, 1], lw=2, label="Curva original")
    plt.plot(curve_mod[:, 0], curve_mod[:, 1], "--", lw=2, label="Curva tras mover control")

    # Polígonos de control
    plt.plot(P[:, 0], P[:, 1], "o-", label="Controles originales")
    plt.plot(r["P_mod"][:, 0], r["P_mod"][:, 1], "o--", label="Controles modificados")

    # Puntos especiales p(u) y q(u)
    plt.plot(r["p_u"][0], r["p_u"][1], "ko", ms=8, label=f"p({u})")
    plt.plot(r["q_u"][0], r["q_u"][1], "go", ms=8, label=f"q({u})")

    # Vector esperado desde p(u)
    # (no dibujamos el vector v completo, sino el escalado por el peso Bernstein)
    exp = r["expected"]
    plt.arrow(r["p_u"][0], r["p_u"][1], exp[0], exp[1],
              head_width=0.12, head_length=0.2, length_includes_head=True)

    plt.axis("equal")
    plt.grid(True, alpha=0.3)
    plt.title("Efecto de mover un punto de control (Bézier cúbica)")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

