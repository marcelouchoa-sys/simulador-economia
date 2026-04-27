import numpy as np

def resolver_consumo(Y_grid, c0, c1, T, escola="Keynesiana"):
    """
    Keynesiana : C = c0 + c1*(Y - T)
    Clássica   : C = (1 - s)*(Y - T), onde s é determinada pela taxa de juros real
                 (aqui s fixo = 1 - c1 para manter consistência com o sistema)
    Retorna C e a equação em string.
    """
    Yd = Y_grid - T
    if escola == "Keynesiana":
        C = c0 + c1 * Yd
        eq = f"C = {c0:.0f} + {c1:.2f}·(Y − {T:.0f})"
    else:
        # Clássico: consumo determinado pela renda permanente, sem autônomo
        C = c1 * Yd
        eq = f"C = {c1:.2f}·(Y − {T:.0f})  [sem componente autônomo]"
    return C, eq


def resolver_poupanca(Y_grid, c0, c1, T, escola="Keynesiana"):
    """
    S ≡ Y - T - C  (identidade contábil — não é comportamental)
    """
    C, _ = resolver_consumo(Y_grid, c0, c1, T, escola)
    S = Y_grid - T - C
    return S


def multiplicador_fiscal(c1):
    """
    Multiplicador keynesiano simples: 1 / (1 - c1)
    """
    return 1.0 / max(1e-9, 1.0 - c1)


def multiplicador_imposto(c1):
    """
    Multiplicador de impostos: -c1 / (1 - c1)
    """
    return -c1 / max(1e-9, 1.0 - c1)