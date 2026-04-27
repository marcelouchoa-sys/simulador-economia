import numpy as np

def resolver_demanda_moeda(Y_grid, r_grid, k, h, P, escola="Keynesiana"):
    """
    Keynesiana (Preferência pela Liquidez):
        Md/P = k*Y - h*r
        Três motivos: transação, precaução, especulação

    Clássica (Teoria Quantitativa):
        Md = (1/V)*P*Y  →  Md/P = (1/V)*Y
        Velocidade V constante, sem motivo especulação
    """
    if escola == "Keynesiana":
        Md_real = k * Y_grid - h * r_grid
        eq = f"Md/P = {k:.2f}·Y − {h:.0f}·r"
    else:
        V = k * 2.0  # velocidade implícita
        Md_real = (1.0 / V) * Y_grid
        eq = f"Md/P = (1/V)·Y = {1/V:.3f}·Y  [TQM, V={V:.2f}]"
    return Md_real, eq


def resolver_lm(Y_grid, k, h, M, P):
    """
    Equilíbrio no mercado monetário:
        M/P = k*Y - h*r  →  r = (k*Y - M/P) / h
    """
    MP = M / max(P, 1e-9)
    r = (k * Y_grid - MP) / max(h, 1e-9)
    return r