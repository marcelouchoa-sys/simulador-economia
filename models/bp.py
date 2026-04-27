import numpy as np

def curva_bp(Y_grid, r_world, kf, m, X=100.0):
    """
    BP: equilíbrio no Balanço de Pagamentos.

    BC = X - m*Y  (balança comercial)
    KA = kf*(r - r_world)  (conta capital)

    BP = 0  →  X - m*Y + kf*(r - r_world) = 0
    →  r = r_world + (m*Y - X) / kf

    kf → ∞ : BP horizontal (perfeita mobilidade — Mundell-Fleming)
    kf → 0 : BP vertical (imobilidade de capitais)
    """
    if kf > 1e6:
        r_bp = np.full_like(Y_grid, r_world)
    else:
        r_bp = r_world + (m * Y_grid - X) / max(kf, 1e-9)
    return r_bp


def solve_bp(Y_eq, r_eq, r_world, kf, m, X=100.0):
    """
    Diagnóstico do BP no equilíbrio IS-LM.
    """
    BC = X - m * Y_eq
    KA = kf * (r_eq - r_world)
    BP = BC + KA

    if abs(BP) < 1.0:
        status = "Equilíbrio externo"
    elif BP > 0:
        status = "Superávit BP (pressão de apreciação)"
    else:
        status = "Déficit BP (pressão de depreciação)"

    return dict(BC=BC, KA=KA, BP=BP, status=status)