import math
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# FUNCIONES PARA B-SPLINES (BIBLIOTECA)
# ==========================================

def create_knot_vector(n, p, clamped=True):
    """
    Crea un vector de nudos uniforme.
    n: número de puntos de control - 1
    p: grado de la curva
    """
    if clamped:
        # Nudos repetidos al inicio y al final (la curva toca los extremos)
        kv = [0] * p + list(range(n - p + 2)) + [n - p + 1] * p
    else:
        # Nudos uniformes (la curva no suele tocar los extremos)
        kv = list(range(n + p + 2))
    return np.array(kv, dtype=float)

def de_boor(k, x, t, c, p):
    """
    Algoritmo de De Boor para evaluar un punto en una B-Spline.
    k: índice del intervalo del nudo
    x: valor del parámetro u
    t: vector de nudos
    c: puntos de control
    p: grado
    """
    # Inicializar puntos temporales
    d = [np.array(c[j + k - p]) for j in range(p + 1)]
    
    for r in range(1, p + 1):
        for j in range(p, r - 1, -1):
            denom = t[j + k + 1 - r] - t[j + k - p]
            if denom == 0:
                alpha = 0
            else:
                alpha = (x - t[j + k - p]) / denom
            d[j] = (1.0 - alpha) * d[j - 1] + alpha * d[j]
    return d[p]

def bspline_curve(P, p=3, num_samples=100):
    """
    Genera los puntos de la curva B-Spline.
    P: lista/array de puntos de control
    p: grado (típicamente 3 para cúbicas)
    """
    n = len(P) - 1
    kv = create_knot_vector(n, p)
    
    # El rango válido para evaluar es entre kv[p] y kv[n+1]
    u_min, u_max = kv[p], kv[n + 1]
    u_steps = np.linspace(u_min, u_max, num_samples)
    
    curve_pts = []
    for u in u_steps:
        # Encontrar el índice k tal que kv[k] <= u < kv[k+1]
        k = min(np.searchsorted(kv, u, side='right') - 1, n)
        pt = de_boor(k, u, kv, P, p)
        curve_pts.append(pt)
        
    return np.array(curve_pts)

# ==========================================
# BLOQUE PRINCIPAL (MAIN)
# ==========================================

def main():
    # 1. Definir puntos de control (ejemplo para un contorno)
    # Puedes añadir tantos puntos como quieras, la B-Spline los gestionará
    puntos_control = np.array([
        [0, 0],
        [1, 3],
        [4, 4],
        [6, 1],
        [8, 4],
        [10, 0]
    ])

    # 2. Calcular la curva B-Spline de grado 3
    p = 3
    puntos_curva = bspline_curve(puntos_control, p=p, num_samples=150)

    # 3. Visualización con Matplotlib
    plt.figure(figsize=(10, 6))
    
    # Dibujar el polígono de control (línea discontinua)
    plt.plot(puntos_control[:, 0], puntos_control[:, 1], 'ko--', alpha=0.4, label="Polígono de Control")
    
    # Dibujar los puntos de control
    plt.scatter(puntos_control[:, 0], puntos_control[:, 1], color='red')
    for i, (x, y) in enumerate(puntos_control):
        plt.text(x, y + 0.2, f'P{i}', fontsize=10, ha='center')

    # Dibujar la B-Spline resultante
    plt.plot(puntos_curva[:, 0], puntos_curva[:, 1], 'b-', linewidth=2.5, label=f"B-Spline (Grado {p})")

    plt.title("Visualización de B-Spline en Google Colab")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.axis('equal')
    plt.show()

if __name__ == "__main__":
    main()ontainer.objects.link(empty)