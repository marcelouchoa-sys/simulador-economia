def resolver_oferta_moeda(M, P, regime="Exógena"):
    """
    Exógena (Keynesiana/Banco Central controla M):
        Ms/P = M/P  — linha vertical no espaço (r, Md)

    Endógena (Pós-Keynesiana / Clássica moderna):
        Ms responde à demanda de crédito — aqui representado como
        Ms = M0 + phi*r  (oferta cresce com juros)
    """
    MP = M / max(P, 1e-9)
    if regime == "Exógena":
        eq = f"Ms/P = {MP:.2f}  [exógena, vertical]"
        return MP, eq
    else:
        phi = 50.0
        eq = f"Ms/P = {MP:.2f} + {phi}·r  [endógena]"
        return MP, eq