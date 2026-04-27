import numpy as np
from models.islm import solve_islm

def solve_adas(c0, c1, T, I0, b, G, k, h, M, Pe, Yn, alpha):
    """
    Equilíbrio AD-AS completo.

    DA: derivada do sistema IS-LM para cada P
        Y_DA(P) = [mult*A*h + mult*b*M/P] / [h + mult*b*k]

    OA CP: P = Pe + (Y - Yn) / alpha
    OA LP: Y = Yn (vertical)

    Solução simultânea DA ∩ OA CP:
    Substituindo OA na DA e resolvendo para Y*:

        Y_DA = N / (D + mult*b*k/h)
        onde N = mult*A + mult*b*M/(h*P)

    Iteração numérica para encontrar P* e Y* consistentes.
    """
    mult = 1.0 / max(1e-9, 1.0 - c1)
    A    = c0 - c1*T + I0 + G

    # Iteração: começa com P = Pe, converge para equilíbrio
    P_iter = Pe
    for _ in range(500):
        MP     = M / max(P_iter, 1e-9)
        denom  = h + mult * b * k
        Y_iter = (mult * A * h + mult * b * MP) / max(denom, 1e-9)
        P_new  = Pe + (Y_iter - Yn) / max(alpha, 1e-9)
        if abs(P_new - P_iter) < 1e-8:
            break
        P_iter = P_new

    P_eq = P_iter
    Y_eq = Y_iter

    # Recalcula IS-LM no P* encontrado
    islm = solve_islm(c0, c1, T, I0, b, G, k, h, M, P_eq)

    return dict(
        Y=Y_eq,
        P=P_eq,
        r=islm["r"],
        C=islm["C"],
        I=islm["I"],
        S=islm["S"],
        hiato=Y_eq - Yn
    )


def curva_da(P_grid, c0, c1, T, I0, b, G, k, h, M):
    """
    DA(P): locus de equilíbrios IS-LM para cada nível de P.
    Derivada analiticamente — não é curva ad-hoc.
    """
    mult  = 1.0 / max(1e-9, 1.0 - c1)
    A     = c0 - c1*T + I0 + G
    denom = h + mult * b * k

    Y_vals = []
    for P in P_grid:
        MP = M / max(P, 1e-9)
        Y  = (mult * A * h + mult * b * MP) / max(denom, 1e-9)
        Y_vals.append(Y)
    return np.array(Y_vals)


def curva_oa_cp(Y_grid, Pe, Yn, alpha):
    """
    OA Curto Prazo: P = Pe + (Y - Yn) / alpha
    Firmas ofertam mais apenas se P > Pe (surpresa nominal).
    """
    return Pe + (Y_grid - Yn) / max(alpha, 1e-9)


def curva_oa_lp(P_grid, Yn):
    """
    OA Longo Prazo: Y = Yn para qualquer P (vertical).
    """
    return np.full_like(P_grid, Yn)