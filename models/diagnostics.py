def diagnosticar_choque(base, choque, params_base, params_choque):
    """
    Compara dois equilíbrios e gera diagnóstico econômico completo.
    """
    dY = choque["Y"] - base["Y"]
    dr = choque["r"] - base["r"]
    dC = choque["C"] - base["C"]
    dI = choque["I"] - base["I"]

    dG = params_choque["G"] - params_base["G"]
    dT = params_choque["T"] - params_base["T"]
    dM = params_choque["M"] - params_base["M"]

    linhas = []

    # Tipo de choque
    if dG != 0:
        linhas.append(f"**Choque Fiscal:** ΔG = {dG:+.0f}")
        linhas.append(f"- Multiplicador realizado: ΔY/ΔG = {dY/dG:.3f}" if dG != 0 else "")
        linhas.append(f"- Multiplicador teórico: {base['mult']:.3f}")
        if dG > 0 and dr > 0:
            linhas.append(f"- **Crowding-out:** ↑G → ↑r → ↓I (ΔI = {dI:+.1f})")
        linhas.append(f"- Transmissão: ↑G → ↑DA → IS desloca direita → ↑Y, ↑r")

    if dT != 0:
        mult_t = -params_base["c1"] / max(1 - params_base["c1"], 1e-9)
        linhas.append(f"**Choque Fiscal (Impostos):** ΔT = {dT:+.0f}")
        linhas.append(f"- Multiplicador realizado: ΔY/ΔT = {dY/dT:.3f}" if dT != 0 else "")
        linhas.append(f"- Multiplicador teórico: {mult_t:.3f}")
        linhas.append(f"- Transmissão: ↑T → ↓Yd → ↓C → IS desloca esquerda → ↓Y, ↓r")

    if dM != 0:
        linhas.append(f"**Choque Monetário:** ΔM = {dM:+.0f}")
        linhas.append(f"- Transmissão: ↑M → ↑M/P → LM desloca direita → ↓r → ↑I → ↑Y")
        linhas.append(f"- ΔI = {dI:+.1f} (canal de transmissão monetária)")

    # Hiato
    Yn = params_base["Yn"]
    hiato_base   = base["Y"]   - Yn
    hiato_choque = choque["Y"] - Yn
    linhas.append(f"\n**Hiato do Produto:**")
    linhas.append(f"- Base: {hiato_base:+.1f} | Choque: {hiato_choque:+.1f}")
    if hiato_choque > 0:
        linhas.append("- Economia **acima do potencial** → pressão inflacionária")
    elif hiato_choque < 0:
        linhas.append("- Economia **abaixo do potencial** → pressão deflacionária / desemprego")
    else:
        linhas.append("- Economia **no produto potencial**")

    return "\n".join(linhas)