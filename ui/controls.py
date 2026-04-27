import streamlit as st
from core.parameters import DEFAULT_PARAMS


def render_mode_selector():
    st.sidebar.markdown("## 🎓 Nível do Modelo")
    nivel = st.sidebar.radio(
        "Selecione o nível:",
        ["Básico", "Médio", "Avançado"],
        index=0,
        help=(
            "Básico: controles qualitativos, sem parâmetros técnicos.\n"
            "Médio: cenários prontos + números principais.\n"
            "Avançado: todos os parâmetros estruturais expostos."
        )
    )
    return nivel


def render_regime_selector():
    st.sidebar.markdown("## 🌐 Regime Cambial")
    regime = st.sidebar.radio(
        "Regime cambial:",
        ["Câmbio Fixo", "Câmbio Flexível"],
        index=1,
        help=(
            "Câmbio Fixo: Banco Central intervém para manter a taxa.\n"
            "Câmbio Flexível: taxa determinada pelo mercado."
        )
    )
    return regime


def render_shock_selector():
    st.sidebar.markdown("## ⚡ Tipo de Choque")
    tipo = st.sidebar.selectbox(
        "Selecione o choque:",
        [
            "Nenhum (equilíbrio base)",
            "Expansão Fiscal (↑G)",
            "Contração Fiscal (↓G)",
            "Expansão Monetária (↑M)",
            "Contração Monetária (↓M)",
            "Aumento de Impostos (↑T)",
            "Redução de Impostos (↓T)",
            "Choque de Oferta Negativo (↑Pe)",
            "Choque de Oferta Positivo (↓Pe)",
            "Personalizado",
        ]
    )
    return tipo


def render_basic_controls(tipo_choque):
    st.sidebar.markdown("## 🔧 Intensidade do Choque")

    intensidade = st.sidebar.select_slider(
        "Intensidade:",
        options=["Fraca", "Moderada", "Forte"],
        value="Moderada"
    )

    mapa = {"Fraca": 0.05, "Moderada": 0.15, "Forte": 0.30}
    fator = mapa[intensidade]

    p = DEFAULT_PARAMS.copy()
    delta = {}

    if tipo_choque == "Expansão Fiscal (↑G)":
        delta["G"] = p["G"] * fator
    elif tipo_choque == "Contração Fiscal (↓G)":
        delta["G"] = -p["G"] * fator
    elif tipo_choque == "Expansão Monetária (↑M)":
        delta["M"] = p["M"] * fator
    elif tipo_choque == "Contração Monetária (↓M)":
        delta["M"] = -p["M"] * fator
    elif tipo_choque == "Aumento de Impostos (↑T)":
        delta["T"] = p["T"] * fator
    elif tipo_choque == "Redução de Impostos (↓T)":
        delta["T"] = -p["T"] * fator
    elif tipo_choque == "Choque de Oferta Negativo (↑Pe)":
        delta["Pe"] = p["Pe"] * fator
    elif tipo_choque == "Choque de Oferta Positivo (↓Pe)":
        delta["Pe"] = -p["Pe"] * fator

    p_base = DEFAULT_PARAMS.copy()
    p_shock = DEFAULT_PARAMS.copy()

    for k, v in delta.items():
        p_shock[k] = p_shock[k] + v

    return p_base, p_shock, intensidade, delta


def render_medium_controls(tipo_choque):
    st.sidebar.markdown("## 📊 Parâmetros Principais")

    p_base = DEFAULT_PARAMS.copy()

    cenario = st.sidebar.selectbox(
        "Cenário pré-definido:",
        [
            "Personalizado",
            "Crise de Demanda",
            "Boom Fiscal",
            "Aperto Monetário",
            "Choque de Petróleo",
            "Fuga de Capitais",
        ]
    )

    presets = {
        "Crise de Demanda":   {"G": p_base["G"] * 0.85, "M": p_base["M"]},
        "Boom Fiscal":        {"G": p_base["G"] * 1.30, "T": p_base["T"] * 0.90},
        "Aperto Monetário":   {"M": p_base["M"] * 0.80},
        "Choque de Petróleo": {"Pe": p_base["Pe"] * 1.40},
        "Fuga de Capitais":   {"M": p_base["M"] * 0.85, "Pe": p_base["Pe"] * 1.20},
    }

    p_shock = DEFAULT_PARAMS.copy()

    if cenario != "Personalizado":
        for k, v in presets[cenario].items():
            p_shock[k] = v
    else:
        p_shock["M"] = st.sidebar.number_input(
            "M — Oferta de Moeda", 100.0, 5000.0,
            float(DEFAULT_PARAMS["M"]), 50.0
        )
        p_shock["G"] = st.sidebar.number_input(
            "G — Gastos do Governo", 0.0, 1500.0,
            float(DEFAULT_PARAMS["G"]), 10.0
        )
        p_shock["T"] = st.sidebar.number_input(
            "T — Impostos", 0.0, 1000.0,
            float(DEFAULT_PARAMS["T"]), 10.0
        )
        p_shock["Pe"] = st.sidebar.number_input(
            "Pᵉ — Preço Esperado", 0.1, 5.0,
            float(DEFAULT_PARAMS["Pe"]), 0.05
        )

    return p_base, p_shock, cenario


def render_advanced_controls():
    st.sidebar.markdown("## ⚙️ Parâmetros Completos")

    st.sidebar.subheader("📌 Cenário Base")
    M_b = st.sidebar.number_input(
        "M", 100.0, 5000.0, float(DEFAULT_PARAMS["M"]), 50.0
    )
    G_b = st.sidebar.number_input(
        "G", 0.0, 1500.0, float(DEFAULT_PARAMS["G"]), 10.0
    )
    T_b = st.sidebar.number_input(
        "T", 0.0, 1000.0, float(DEFAULT_PARAMS["T"]), 10.0
    )
    Pe_b = st.sidebar.number_input(
        "Pᵉ", 0.1, 5.0, float(DEFAULT_PARAMS["Pe"]), 0.05
    )
    pie_b = st.sidebar.number_input(
        "πᵉ (%)", 0.0, 20.0, float(DEFAULT_PARAMS["pie"]) * 100, 0.1
    ) / 100

    st.sidebar.divider()
    st.sidebar.subheader("⚡ Cenário Choque")
    M_s = st.sidebar.number_input(
        "M¹", 100.0, 5000.0, float(DEFAULT_PARAMS["M"]), 50.0, key="Ms"
    )
    G_s = st.sidebar.number_input(
        "G¹", 0.0, 1500.0, float(DEFAULT_PARAMS["G"]), 10.0, key="Gs"
    )
    T_s = st.sidebar.number_input(
        "T¹", 0.0, 1000.0, float(DEFAULT_PARAMS["T"]), 10.0, key="Ts"
    )
    Pe_s = st.sidebar.number_input(
        "Pᵉ¹", 0.1, 5.0, float(DEFAULT_PARAMS["Pe"]), 0.05, key="Pes"
    )
    pie_s = st.sidebar.number_input(
        "πᵉ¹ (%)", 0.0, 20.0, float(DEFAULT_PARAMS["pie"]) * 100, 0.1, key="pies"
    ) / 100

    st.sidebar.divider()
    st.sidebar.subheader("🔧 Parâmetros Estruturais")

    with st.sidebar.expander("Setor Real (IS)"):
        c0 = st.sidebar.slider("c₀", 0.0,   500.0,  float(DEFAULT_PARAMS["c0"]), 10.0)
        c  = st.sidebar.slider("c",  0.01,  0.99,   float(DEFAULT_PARAMS["c"]),  0.01)
        I0 = st.sidebar.slider("I₀", 0.0,   1000.0, float(DEFAULT_PARAMS["I0"]), 10.0)
        b  = st.sidebar.slider("b",  1.0,   300.0,  float(DEFAULT_PARAMS["b"]),  1.0)

    with st.sidebar.expander("Mercado Monetário (LM)"):
        k = st.sidebar.slider("k", 0.05, 3.0,   float(DEFAULT_PARAMS["k"]), 0.05)
        h = st.sidebar.slider("h", 10.0, 800.0, float(DEFAULT_PARAMS["h"]), 10.0)

    with st.sidebar.expander("Oferta Agregada & Phillips"):
        Yn    = st.sidebar.slider("Yₙ", 200.0, 5000.0, float(DEFAULT_PARAMS["Yn"]),    50.0)
        alpha = st.sidebar.slider("α",  10.0,  2000.0, float(DEFAULT_PARAMS["alpha"]), 10.0)
        un    = st.sidebar.slider(
            "uₙ", 1.0, 20.0, float(DEFAULT_PARAMS["un"]) * 100, 0.5
        ) / 100
        beta  = st.sidebar.slider("β", 0.05, 3.0, float(DEFAULT_PARAMS["beta"]), 0.05)

    shared = dict(
        c0=c0, c=c, I0=I0, b=b,
        k=k, h=h,
        Yn=Yn, alpha=alpha, un=un, beta=beta
    )

    p_base = {
        **shared,
        "M": M_b, "G": G_b, "T": T_b,
        "Pe": Pe_b, "pie": pie_b, "P": Pe_b
    }
    p_shock = {
        **shared,
        "M": M_s, "G": G_s, "T": T_s,
        "Pe": Pe_s, "pie": pie_s, "P": Pe_s
    }

    return p_base, p_shock