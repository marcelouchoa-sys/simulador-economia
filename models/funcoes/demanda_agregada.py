import numpy as np

def resolver_da(P_grid, c0, c1, T, I0, b, G, k, h, M):
    """
    DA derivada analiticamente do sistema IS-LM.
    Não é uma curva ad-hoc — é o locus de equilíbrios IS-LM
    para cada nível de P.

    IS: Y = A/(1-c1) - b/(1-c1) * r
    LM: r = (kY - M/P) / h

    Substituindo LM na IS:
        Y* = [mult*A + mult*b*M/(h*P)] / [1 + mult*b*k/h]

    onde mult = 1/(1-c1), A = c0 - c1*T + I0 + G
    """
    c = c1
    mult = 1.0 / max(1e-9, 1.0 - c)
    A = c0 - c * T + I0 + G
    denom = 1.0 + mult * b * k / max(h, 1e-9)

    Y_vals = []
    for P in P_grid:
        P_eff = max(P, 1e-9)
        Y = (mult * A + mult * b * M / (h * P_eff)) / denom
        Y_vals.append(Y)

    return np.array(Y_vals)