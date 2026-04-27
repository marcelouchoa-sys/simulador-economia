import numpy as np

def resolver_investimento(r_grid, I0, b, escola="Keynesiana"):
    """
    Keynesiana : I = I0 - b*r  (animal spirits + sensibilidade a juros)
    Clássica   : I = S(r) — investimento determinado pela poupança de equilíbrio
                 Aqui representado como I = I0 - b*r mas com b maior (mais elástico)
    """
    if escola == "Keynesiana":
        I = I0 - b * r_grid
        eq = f"I = {I0:.0f} − {b:.0f}·r"
    else:
        # Clássico: mercado de fundos emprestáveis — I muito sensível a r
        b_classico = b * 2.0
        I = I0 - b_classico * r_grid
        eq = f"I = {I0:.0f} − {b_classico:.0f}·r  [fundos emprestáveis, b dobrado]"
    return I, eq


def efeito_crowding_out(r_base, r_choque, b):
    """
    Calcula a perda de investimento privado pelo aumento de juros.
    ΔI = -b * Δr
    """
    delta_r = r_choque - r_base
    delta_I = -b * delta_r
    return delta_I