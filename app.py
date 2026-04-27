import streamlit as st
from core.parameters import DEFAULT_PARAMS

st.set_page_config(
    page_title="MacroSimulator Pro",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZAÇÃO DO ESTADO GLOBAL ---
if "params" not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()

if "settings" not in st.session_state:
    st.session_state.settings = {
        "nivel": "Médio",  # Básico, Médio, Avançado
        "detalhe_causal": True,
        "show_grid": True,
        "color_base": "#1565c0", # Azul
        "color_shock": "#c62828", # Vermelho
        "color_final": "#2e7d32"  # Verde
    }

# --- SIDEBAR GLOBAL DE CUSTOMIZAÇÃO ---
with st.sidebar:
    st.header("🎨 Customização & Didática")
    
    st.session_state.settings["nivel"] = st.select_slider(
        "Nível do Modelo:",
        options=["Básico", "Médio", "Avançado"],
        value=st.session_state.settings["nivel"],
        help="Básico: Foco qualitativo. Médio: Números e choques. Avançado: Equações completas."
    )
    
    with st.expander("Estética das Curvas"):
        st.session_state.settings["color_base"] = st.color_picker("Curva Base", st.session_state.settings["color_base"])
        st.session_state.settings["color_shock"] = st.color_picker("Curva Choque", st.session_state.settings["color_shock"])
        st.session_state.settings["show_grid"] = st.checkbox("Mostrar Grid", value=True)

    if st.button("Resetar Simulador", type="primary"):
        st.session_state.params = DEFAULT_PARAMS.copy()
        st.rerun()

# --- CONTEÚDO DA HOME ---
st.title("🏦 MacroSimulator: Plataforma Didática de Rigor Econômico")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    ### Bem-vindo ao simulador de nível **{st.session_state.settings['nivel']}**
    
    Este sistema não é apenas visual; ele resolve numericamente equilíbrios de modelos 
    macroeconômicos contemporâneos através de sistemas de equações interdependentes.
    
    #### O que você pode explorar:
    1. **Modelo IS-LM:** Equilíbrio nos mercados de bens e monetário.
    2. **Modelo AD-AS:** A determinação do nível de preços e produto no curto e longo prazo.
    3. **Curva de Phillips:** O trade-off entre inflação e desemprego sob diferentes expectativas.
    
    #### Camadas de Rigor:
    - **Causalidade:** Toda variação em $G$ ou $M$ recalcula a demanda agregada via sistema IS-LM.
    - **Consistência:** O produto $Y$ determinado no AD-AS alimenta a Lei de Okun para gerar o desemprego $u$.
    """)
    
    if st.session_state.settings["nivel"] == "Avançado":
        st.info("🔬 **Modo Avançado Ativo:** O simulador exibirá as Reduções de Forma e Jacobianos das iterações numéricas.")

with col2:
    st.image("https://placehold.co/400x300/1565c0/white?text=Macro+Dynamics+AI", use_container_width=True)
    st.success(f"Sistema Pronto. Navegue pelas etapas no menu à esquerda.")

st.divider()
st.caption("Desenvolvido para Engenharia de Software e Macroeconomia Aplicada.")