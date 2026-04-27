def explain_shock(p_b, p_s, res_b, res_s, nivel="Médio"):
    blocos = []

    dY  = res_s['Y']  - res_b['Y']
    dr  = res_s['r']  - res_b['r']
    dP  = res_s['P']  - res_b['P']
    du  = res_s['u']  - res_b['u']
    dpi = res_s['pi'] - res_b['pi']
    dG  = p_s['G']    - p_b['G']
    dM  = p_s['M']    - p_b['M']
    dT  = p_s['T']    - p_b['T']
    dPe = p_s['Pe']   - p_b['Pe']

    # ── Bloco 0: Identificação do Choque ─────────────────────────────
    choques = []
    if abs(dG) > 0.01:
        choques.append(f"{'Aumento' if dG > 0 else 'Redução'} dos Gastos do Governo "
                       f"(ΔG = {dG:+.1f})")
    if abs(dM) > 0.01:
        choques.append(f"{'Expansão' if dM > 0 else 'Contração'} Monetária "
                       f"(ΔM = {dM:+.1f})")
    if abs(dT) > 0.01:
        choques.append(f"{'Aumento' if dT > 0 else 'Redução'} de Impostos "
                       f"(ΔT = {dT:+.1f})")
    if abs(dPe) > 0.001:
        choques.append(f"Choque de Oferta — variação no Preço Esperado "
                       f"(ΔPᵉ = {dPe:+.3f})")

    if not choques:
        blocos.append(("ℹ️ Nenhum Choque Detectado",
                       "Os parâmetros base e choque são idênticos. "
                       "Altere ao menos uma variável exógena para ver os efeitos."))
        return blocos

    blocos.append(("⚡ Ponto A → Choque Identificado", "\n".join(
        [f"- {c}" for c in choques] +
        ["",
         f"**Equilíbrio Inicial (A):** Y = {res_b['Y']:.2f} | "
         f"r = {res_b['r']:.4f} | P = {res_b['P']:.4f} | "
         f"u = {res_b['u']*100:.2f}% | π = {res_b['pi']*100:.2f}%"]
    )))

    # ── Bloco 1: Efeito no Mercado de Bens (IS) ───────────────────────
    if abs(dG) > 0.01 or abs(dT) > 0.01:
        mult = p_b.get('c', 0.8)
        if abs(dG) > 0.01:
            efeito_direto = dG
            tipo = "gastos do governo (G)"
            mecanismo = (
                f"Um aumento de G injeta renda diretamente na economia. "
                f"O multiplicador keynesiano amplifica esse efeito: "
                f"cada R$ 1 de G gera R$ {1/(1-mult):.2f} de renda adicional."
                if dG > 0 else
                f"Uma redução de G retira renda da economia. "
                f"O efeito contracionista é amplificado pelo multiplicador: "
                f"cada R$ 1 a menos em G reduz a renda em R$ {1/(1-mult):.2f}."
            )
        else:
            efeito_direto = -mult * dT
            tipo = "impostos (T)"
            mecanismo = (
                f"Um aumento de T reduz a renda disponível das famílias. "
                f"O consumo cai em c×ΔT = {mult:.2f} × {dT:.1f} = {mult*dT:.2f}. "
                f"O multiplicador fiscal de impostos é menor que o de gastos."
                if dT > 0 else
                f"Uma redução de T aumenta a renda disponível. "
                f"O consumo sobe em c×|ΔT| = {mult:.2f} × {abs(dT):.1f} = {mult*abs(dT):.2f}."
            )

        blocos.append(("📦 Ponto A → B: Efeito no Mercado de Bens (Curva IS)", f"""
**O que mudou:** Variação em {tipo}

**Mecanismo:**
{mecanismo}

**Resultado no Mercado de Bens:**
- A curva IS se desloca para a **{'direita' if efeito_direto > 0 else 'esquerda'}**
- Pressão de {'alta' if efeito_direto > 0 else 'baixa'} sobre a Renda (Y) e a Taxa de Juros (r)
- Efeito direto estimado: ΔY ≈ {efeito_direto * (1/(1-mult)):.2f} (antes do crowding-out)
"""))

    # ── Bloco 2: Efeito no Mercado Monetário (LM) ─────────────────────
    if abs(dM) > 0.01:
        blocos.append(("💰 Ponto A → B: Efeito no Mercado Monetário (Curva LM)", f"""
**O que mudou:** {'Expansão' if dM > 0 else 'Contração'} da Oferta de Moeda (ΔM = {dM:+.1f})

**Mecanismo:**
{'O Banco Central aumenta a oferta de moeda. Com mais moeda disponível, os juros caem para equilibrar o mercado monetário (LM). Juros menores estimulam o Investimento (I), deslocando a demanda agregada para a direita.' if dM > 0 else 'O Banco Central reduz a oferta de moeda (aperto monetário). Com menos moeda, os juros sobem para equilibrar o mercado monetário. Juros maiores inibem o Investimento (I), deslocando a demanda agregada para a esquerda.'}

**Resultado no Mercado Monetário:**
- A curva LM se desloca para a **{'direita (baixo)' if dM > 0 else 'esquerda (cima)'}**
- Taxa de juros tende a **{'cair' if dM > 0 else 'subir'}**
- Investimento tende a **{'aumentar' if dM > 0 else 'diminuir'}**
"""))

    # ── Bloco 3: Crowding-Out ─────────────────────────────────────────
    if abs(dG) > 0.01 and dG > 0:
        crowding = dr * p_b.get('b', 100)
        blocos.append(("⚠️ Efeito Crowding-Out (Expulsão do Investimento Privado)", f"""
**O que é:** Quando o governo aumenta G, a demanda por crédito sobe, pressionando os juros para cima.
Juros mais altos reduzem o Investimento privado (I), **parcialmente cancelando** o efeito expansionista.

**Quantificação:**
- Variação nos juros: Δr = {dr:+.4f}
- Redução estimada no Investimento: ΔI ≈ −b × Δr = −{p_b.get('b',100):.0f} × {dr:.4f} = {-crowding:.2f}
- Efeito líquido sobre Y: {dY:+.2f} (menor que o multiplicador puro indicaria)

**Interpretação:**
{'O crowding-out foi PARCIAL — a política fiscal ainda foi expansionista.' if dY > 0 else 'O crowding-out foi TOTAL ou DOMINANTE — a política fiscal não conseguiu expandir a renda.'}
"""))

    # ── Bloco 4: Ajuste de Preços (AD-AS) ────────────────────────────
    blocos.append(("📊 Ponto B → C: Ajuste de Preços (Modelo AD-AS)", f"""
**O que acontece:** Após o choque na demanda, o nível de preços se ajusta via Curva de Oferta Agregada.

**Equação da Oferta Agregada (AS):**
> P = Pᵉ + (Y − Yₙ) / α

**Cálculo:**
- Base: P* = {p_b['Pe']:.3f} + ({res_b['Y']:.2f} − {p_b['Yn']:.2f}) / {p_b['alpha']:.1f} = **{res_b['P']:.4f}**
- Choque: P* = {p_s['Pe']:.3f} + ({res_s['Y']:.2f} − {p_s['Yn']:.2f}) / {p_s['alpha']:.1f} = **{res_s['P']:.4f}**

**Resultado:**
- Variação no Nível de Preços: ΔP = {dP:+.4f}
- {'Pressão inflacionária: a economia opera ACIMA do produto potencial.' if res_s['Y'] > p_s['Yn'] else 'Pressão deflacionária: a economia opera ABAIXO do produto potencial.' if res_s['Y'] < p_s['Yn'] else 'Economia no produto potencial: sem pressão inflacionária.'}
"""))

    # ── Bloco 5: Phillips e Desemprego ────────────────────────────────
    blocos.append(("👥 Ponto C: Mercado de Trabalho (Okun + Phillips)", f"""
**Lei de Okun** — relaciona variação do produto com desemprego:
> u = uₙ − (Y − Yₙ) / (2 × Yₙ)

- Base: u = {res_b['u']*100:.2f}%
- Choque: u = {res_s['u']*100:.2f}%
- Variação: Δu = {du*100:+.2f} pontos percentuais

**Curva de Phillips** — relaciona desemprego com inflação:
> π = πᵉ − β × (u − uₙ)

- Base: π = {res_b['pi']*100:.2f}%
- Choque: π = {res_s['pi']*100:.2f}%
- Variação: Δπ = {dpi*100:+.2f} pontos percentuais

**Interpretação:**
{'✅ Expansão bem-sucedida: mais renda, menos desemprego, inflação controlada.' if dY > 0 and du < 0 and abs(dpi) < 0.02 else '⚠️ Expansão com custo inflacionário: crescimento veio acompanhado de pressão de preços.' if dY > 0 and dpi > 0 else '📉 Contração: renda caiu, desemprego subiu.' if dY < 0 and du > 0 else '🔄 Efeitos mistos — analise os valores acima com atenção.'}
"""))

    # ── Bloco 6: Resumo Final ─────────────────────────────────────────
    blocos.append(("✅ Equilíbrio Final (C) — Resumo Completo", f"""
| Variável | Base (A) | Final (C) | Variação |
|---|---|---|---|
| Renda Y | {res_b['Y']:.2f} | {res_s['Y']:.2f} | {dY:+.2f} |
| Juros r | {res_b['r']:.4f} | {res_s['r']:.4f} | {dr:+.4f} |
| Preços P | {res_b['P']:.4f} | {res_s['P']:.4f} | {dP:+.4f} |
| Desemprego u | {res_b['u']*100:.2f}% | {res_s['u']*100:.2f}% | {du*100:+.2f}pp |
| Inflação π | {res_b['pi']*100:.2f}% | {res_s['pi']*100:.2f}% | {dpi*100:+.2f}pp |

**Diagnóstico Final:**
- Gap do Produto: Y − Yₙ = {res_s['Y'] - p_s['Yn']:+.2f} ({'acima' if res_s['Y'] > p_s['Yn'] else 'abaixo'} do potencial)
- Regime de Política: {'Expansionista' if dY > 0 else 'Contracionista'}
- Pressão de Preços: {'Alta' if dP > 0.01 else 'Baixa' if dP < -0.01 else 'Neutra'}
"""))

    if nivel == "Básico":
        blocos = [blocos[0], blocos[-1]]

    return blocos


def render_theory_comparison():
    import streamlit as st

    st.markdown("""
    > Cada escola interpreta o mesmo choque de forma diferente.
    > Abaixo, veja como cada teoria responderia ao cenário simulado.
    """)

    teorias = [
        {
            "nome": "🏛️ Escola Clássica",
            "cor": "#1a1a2e",
            "foco": "Longo Prazo — Lado da Oferta",
            "moeda": "**Neutra no longo prazo.** Variações em M afetam apenas o nível de preços, não a renda real. (Teoria Quantitativa da Moeda: MV = PY)",
            "precos": "**Totalmente flexíveis.** O mercado se ajusta instantaneamente. Não há desemprego involuntário persistente.",
            "politica_fiscal": "**Ineficaz.** O aumento de G desloca completamente o investimento privado (crowding-out total). A curva AS é vertical.",
            "politica_monetaria": "**Ineficaz para o produto.** Só gera inflação. O Banco Central deve manter regras fixas de crescimento monetário.",
            "curva_as": "**Vertical** no produto potencial (Yₙ). A economia sempre retorna ao pleno emprego.",
            "phillips": "**Não existe trade-off** de longo prazo entre inflação e desemprego. A curva de Phillips é vertical na taxa natural.",
            "autores": "Adam Smith, David Ricardo, Jean-Baptiste Say"
        },
        {
            "nome": "📘 Escola Keynesiana",
            "cor": "#003366",
            "foco": "Curto Prazo — Lado da Demanda",
            "moeda": "**Não neutra no curto prazo.** Pode estimular a economia quando há recursos ociosos. Armadilha da liquidez possível.",
            "precos": "**Rígidos para baixo** (especialmente salários). O ajuste é lento. Desemprego involuntário é possível e persistente.",
            "politica_fiscal": "**Muito eficaz.** O multiplicador keynesiano amplifica o efeito de G. Em recessão, o Estado deve intervir ativamente.",
            "politica_monetaria": "**Menos eficaz** que a fiscal, especialmente em armadilha da liquidez (quando r ≈ 0).",
            "curva_as": "**Horizontal** (curto prazo) ou com inclinação positiva. Há espaço para expandir Y sem inflação quando há ociosidade.",
            "phillips": "**Trade-off existe no curto prazo.** Menos desemprego custa mais inflação. Política pode explorar essa relação.",
            "autores": "John Maynard Keynes, Alvin Hansen, Paul Samuelson"
        },
        {
            "nome": "🔴 Escola Monetarista",
            "cor": "#7b0000",
            "foco": "Longo Prazo — Regras vs. Discrição",
            "moeda": "**Neutra no longo prazo, não neutra no curto.** Surpresas monetárias afetam Y temporariamente. Regra de Friedman: crescimento fixo de M.",
            "precos": "**Flexíveis no longo prazo.** No curto prazo, expectativas adaptativas causam defasagens.",
            "politica_fiscal": "**Ineficaz no longo prazo** (crowding-out). Pode ter efeito temporário, mas gera déficit e inflação.",
            "politica_monetaria": "**Perigosa se discricionária.** Defasagens longas e variáveis tornam a política ativa desestabilizadora.",
            "curva_as": "**Vertical no longo prazo.** No curto prazo, inclinada positivamente (expectativas adaptativas).",
            "phillips": "**Curva de Phillips acelerada.** Qualquer tentativa de manter u < uₙ gera inflação crescente. Existe taxa natural de desemprego.",
            "autores": "Milton Friedman, Edmund Phelps, Anna Schwartz"
        },
        {
            "nome": "🟣 Escola Pós-Keynesiana",
            "cor": "#4a0072",
            "foco": "Incerteza Fundamental — Instabilidade Financeira",
            "moeda": "**Endógena.** Os bancos criam moeda ao conceder crédito. O Banco Central acomoda a demanda. M não é exógeno.",
            "precos": "**Determinados por Markup** (custos + margem de lucro). Não são determinados pela interação oferta-demanda clássica.",
            "politica_fiscal": "**Fundamental e permanente.** O Estado deve garantir pleno emprego via gasto público contínuo (Princípio da Demanda Efetiva).",
            "politica_monetaria": "**Limitada.** Taxa de juros afeta distribuição de renda e fluxo de caixa das firmas, não apenas investimento.",
            "curva_as": "**Rejeitada como formulada.** Preferem modelos de preços por custos e conflito distributivo.",
            "phillips": "**Relação instável.** Inflação é resultado de conflito distributivo (salários vs. lucros), não apenas de demanda.",
            "autores": "Hyman Minsky, Nicholas Kaldor, Paul Davidson, Michal Kalecki"
        },
    ]

    import streamlit as st

    for t in teorias:
        with st.expander(f"{t['nome']} — {t['foco']}", expanded=False):
            st.markdown(f"**Autores de Referência:** {t['autores']}")
            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 💵 Papel da Moeda")
                st.markdown(t['moeda'])
                st.markdown("#### 🏷️ Comportamento dos Preços")
                st.markdown(t['precos'])
                st.markdown("#### 📈 Curva de Oferta Agregada (AS)")
                st.markdown(t['curva_as'])

            with col2:
                st.markdown("#### 🏛️ Política Fiscal")
                st.markdown(t['politica_fiscal'])
                st.markdown("#### 🏦 Política Monetária")
                st.markdown(t['politica_monetaria'])
                st.markdown("#### 📉 Curva de Phillips")
                st.markdown(t['phillips'])