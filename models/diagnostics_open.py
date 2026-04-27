# models/diagnostics_open.py
"""
Diagnóstico automático de choques em economia aberta.
Identifica o tipo de choque, regime cambial e explica
o mecanismo de transmissão passo a passo.
"""


def diagnosticar_choque_aberto(base, choque, params_b, params_c):
    """
    Compara dois equilíbrios e gera diagnóstico econômico completo.
    """
    dY  = choque["Y"]  - base["Y"]
    dr  = choque["r"]  - base["r"]
    de  = choque["e"]  - base["e"]
    dNX = choque["NX"] - base["NX"]
    dCF = choque["CF"] - base["CF"]
    dBP = choque["BP"] - base["BP"]

    dG = params_c["G"] - params_b["G"]
    dT = params_c["T"] - params_b["T"]
    dM = params_c["M"] - params_b["M"]
    dr_star = params_c["r_star"] - params_b["r_star"]
    dY_star = params_c["Y_star"] - params_b["Y_star"]

    regime = params_c.get("regime", "flex")
    kf     = params_c["kf"]

    # ── Tipo de choque ────────────────────────────────────────
    choques = []
    if abs(dG) > 0.1:
        choques.append(f"Fiscal: ΔG = {dG:+.1f}")
    if abs(dT) > 0.1:
        choques.append(f"Fiscal: ΔT = {dT:+.1f}")
    if abs(dM) > 0.1:
        choques.append(f"Monetário: ΔM = {dM:+.1f}")
    if abs(dr_star) > 0.001:
        choques.append(f"Externo: Δr* = {dr_star*100:+.2f}pp")
    if abs(dY_star) > 0.1:
        choques.append(f"Externo: ΔY* = {dY_star:+.1f}")
    if not choques:
        choques = ["Nenhum choque identificado"]

    # ── Mobilidade de capital ─────────────────────────────────
    if kf > 1e5:
        mob = "Perfeita (r = r*)"
    elif kf > 500:
        mob = "Alta (BP quase horizontal)"
    elif kf > 100:
        mob = "Moderada"
    else:
        mob = "Baixa (BP íngreme)"

    # ── Mecanismo de transmissão ──────────────────────────────
    mecanismo = []

    if abs(dG) > 0.1 and dG > 0:
        mecanismo.append("1. ↑G → IS desloca direita → ↑Y, ↑r")
        if regime == "flex":
            if kf > 500:
                mecanismo.append("2. ↑r > r* → entrada de capital (CF > 0)")
                mecanismo.append("3. Entrada de capital → apreciação cambial (↓e)")
                mecanismo.append("4. ↓e → ↓X, ↑Imp → ↓NX (crowding-out externo)")
                mecanismo.append("5. ↓NX → IS recua → Y cai de volta")
                mecanismo.append("⚠️ Alta mobilidade + câmbio flex: política fiscal INEFICAZ (Mundell-Fleming)")
            else:
                mecanismo.append("2. ↑r → alguma entrada de capital")
                mecanismo.append("3. Apreciação parcial → ↓NX parcial")
                mecanismo.append("4. Efeito líquido: ↑Y (parcial)")
        else:  # fixo
            mecanismo.append("2. ↑r > r* → entrada de capital")
            mecanismo.append("3. BC compra divisas → ↑M (endógeno)")
            mecanismo.append("4. ↑M → LM desloca direita → ↑Y adicional")
            mecanismo.append("✅ Alta mobilidade + câmbio fixo: política fiscal EFICAZ")

    if abs(dM) > 0.1 and dM > 0:
        mecanismo.append("1. ↑M → LM desloca direita → ↓r, ↑Y")
        if regime == "flex":
            if kf > 500:
                mecanismo.append("2. ↓r < r* → saída de capital (CF < 0)")
                mecanismo.append("3. Saída de capital → depreciação (↑e)")
                mecanismo.append("4. ↑e → ↑X, ↓Imp → ↑NX")
                mecanismo.append("5. ↑NX → IS desloca direita → ↑Y adicional")
                mecanismo.append("✅ Alta mobilidade + câmbio flex: política monetária EFICAZ")
            else:
                mecanismo.append("2. ↓r → saída parcial de capital")
                mecanismo.append("3. Depreciação parcial → ↑NX parcial")
        else:  # fixo
            mecanismo.append("2. ↓r < r* → saída de capital")
            mecanismo.append("3. BC vende divisas → ↓M (esterilização)")
            mecanismo.append("4. LM retorna à posição original")
            mecanismo.append("⚠️ Câmbio fixo: política monetária INEFICAZ")

    if abs(dr_star) > 0.001 and dr_star > 0:
        mecanismo.append("1. ↑r* → saída de capital (CF < 0)")
        if regime == "flex":
            mecanismo.append("2. Saída de capital → depreciação (↑e)")
            mecanismo.append("3. ↑e → ↑NX → IS desloca direita")
            mecanismo.append("4. Efeito ambíguo sobre Y (depende de kf)")
        else:
            mecanismo.append("2. BC vende reservas para manter e")
            mecanismo.append("3. ↓M → LM desloca esquerda → ↓Y, ↑r")
            mecanismo.append("4. r sobe até r = r* novamente")

    if not mecanismo:
        mecanismo = ["Sem choque identificado para análise de transmissão."]

    # ── Multiplicadores ───────────────────────────────────────
    mult_fiscal   = dY / dG   if abs(dG) > 0.1   else None
    mult_monetario = dY / dM  if abs(dM) > 0.1   else None

    return dict(
        choques=choques,
        regime=regime,
        mobilidade=mob,
        mecanismo=mecanismo,
        dY=dY, dr=dr, de=de,
        dNX=dNX, dCF=dCF, dBP=dBP,
        mult_fiscal=mult_fiscal,
        mult_monetario=mult_monetario,
    )