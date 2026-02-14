
# -*- coding: utf-8 -*-
"""
04_casteljau_levels_subdivision.py
==================================

Objetivo
--------
1) Implementar De Casteljau (niveles) de forma iterativa.
2) Verificar que coincide con la fórmula Bernstein.
3) Visualizar niveles para un u concreto.
4) Subdividir la curva en dos subcurvas equivalentes en u (usando la diagonal).

Dependencias
-----------
- numpy
- math
- matplotlib

Ejecución
---------
python 04_casteljau_levels_subdivision.py

Qué extraer para Blender
------------------------
- de_casteljau_levels(P, u)
- de_casteljau_point(P, u)
- subdivide_bezier(P, u)
"""

import math
import numpy as np
import matplotlib.pyplot as plt


def bernstein(n: int, i: int, u: float) -> float:
    return math.comb(n, i) * (u ** i) * ((1.0 - u) ** (n - i))


def bezier_point_bernstein(P: np.ndarray, u: float) -> np.ndarray:
    """
    Evaluación por fórmula explícita (Bernstein), para comparar.
    """
    n = len(P) - 1
    out = np.zeros(P.shape[1], dtype=float)
    for i in range(n + 1):
        out += bernstein(n, i, u) * P[i]
    return out


def de_casteljau_levels(P: np.ndarray, u: float):
    """
    Algoritmo de De Casteljau (iterativo), devolviendo todos los niveles.

    Intuición:
    - Nivel 0: puntos de control originales.
    - Nivel 1: interpolaciones lineales entre puntos consecutivos.
    - Nivel 2: interpolaciones entre puntos del nivel 1.
    - ...
    - Último nivel: un único punto = p(u) en la curva.

    Fórmula de interpolación:
        LERP(A,B,u) = (1-u)A + uB
    """
    levels = [P.copy()]
    current = P.copy()

    while len(current) > 1:
        next_level = []
        for i in range(len(current) - 1):
            pt = (1.0 - u) * current[i] + u * current[i + 1]
            next_level.append(pt)
        current = np.array(next_level, dtype=float)
        levels.append(current.copy())

    return levels


def de_casteljau_point(P: np.ndarray, u: float) -> np.ndarray:
    """Devuelve el punto final p(u) (último nivel, único punto)."""
    return de_casteljau_levels(P, u)[-1][0]


def subdivide_bezier(P: np.ndarray, u: float):
    """
    Subdivisión en u usando la diagonal de los niveles:

    - left controls:  primer elemento de cada nivel
    - right controls: último elemento de cada nivel (en orden inverso)

    Resultado:
      left  define la subcurva de u∈[0,u0]
      right define la subcurva de u∈[u0,1]
    """
    levels = de_casteljau_levels(P, u)

    left = [lvl[0] for lvl in levels]
    right = [lvl[-1] for lvl in levels][::-1]
    return np.array(left, dtype=float), np.array(right, dtype=float)


def bezier_curve_casteljau(P: np.ndarray, num_samples: int = 200) -> np.ndarray:
    """Muestrea usando De Casteljau (más estable numéricamente)."""
    u_values = np.linspace(0.0, 1.0, num_samples)
    return np.array([de_casteljau_point(P, u) for u in u_values], dtype=float)


def main():
    # Ejemplo grado 4 (5 puntos) en 2D
    P = np.array([
        [0.0,  0.0],
        [2.0,  5.0],
        [5.0,  6.5],
        [7.0,  6.0],
        [10.0, 0.0]
    ], dtype=float)

    u0 = 0.5

    # Comparación Casteljau vs Bernstein
    test_us = [0.25, 0.5, 0.8]
    max_err = 0.0
    for u in test_us:
        a = bezier_point_bernstein(P, u)
        b = de_casteljau_point(P, u)
        max_err = max(max_err, float(np.linalg.norm(a - b)))
    print("[Casteljau vs Bernstein] max error =", max_err)

    # Niveles para u0
    levels = de_casteljau_levels(P, u0)
    print(f"\nNiveles para u={u0}")
    for k, lvl in enumerate(levels):
        print(f" Level {k} ({len(lvl)} puntos):")
        for i, pt in enumerate(lvl):
            print(f"   {i}: ({pt[0]:.4f}, {pt[1]:.4f})")

    # Subdivisión
    L, R = subdivide_bezier(P, u0)
    mid = de_casteljau_point(P, u0)
    print("\n[Subdivisión]")
    print(" mid =", mid)
    print(" left controls shape =", L.shape)
    print(" right controls shape =", R.shape)

    # Visualización
    curve = bezier_curve_casteljau(P, 300)

    plt.figure(figsize=(11, 6))
    plt.plot(curve[:, 0], curve[:, 1], "k-", lw=2.5, label="Curva Bézier (Casteljau)")
    plt.plot(P[:, 0], P[:, 1], "bo-", markerfacecolor="white", label="Polígono de control")

    # Dibujar niveles (polígonos intermedios) para u0
    for k, lvl in enumerate(levels[1:], start=1):
        plt.plot(lvl[:, 0], lvl[:, 1], "--o", markerfacecolor="white", lw=1.5, label=f"Nivel {k}")

    # Punto mid
    plt.plot(mid[0], mid[1], "ro", ms=10, label=f"p({u0})")

    plt.axis("equal")
    plt.grid(True, alpha=0.3)
    plt.title("De Casteljau (niveles) + subdivisión")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
