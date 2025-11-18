st.markdown("""
<style>

    /* GLOBAL ----------------------------*/
    html, body, [class*="block-container"] {
        font-family: "Inter", sans-serif !important;
        background: #0d1117;
        color: #e5e7eb;
    }

    h1, h2, h3, h4 {
        font-family: "Inter", sans-serif !important;
        font-weight: 600 !important;
        color: #f8f9fc !important;
    }

    /* SIDEBAR ----------------------------*/
    section[data-testid="stSidebar"] {
        background: #111622 !important;
        padding-top: 20px;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    /* CARDS / EXPANDERS ----------------------------*/
    .streamlit-expanderHeader {
        font-size: 1.1rem;
        font-weight: 500;
        color: #f1f5f9 !important;
    }

    .streamlit-expander {
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px);
    }

    /* INPUT FIELDS ----------------------------*/
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stDateInput>div>div>input {
        background: #1a1f2d !important;
        border-radius: 8px !important;
        border: 1px solid #2c3143 !important;
        color: #e5e7eb !important;
    }

    /* BUTTONS ----------------------------*/
    .stButton>button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: 0.2s ease-in-out;
        box-shadow: 0 4px 10px rgba(0,0,0,0.25);
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.35);
    }

    /* REMOVAL BUTTONS ----------------------------*/
    .stButton>button[kind="secondary"] {
        background: #dc2626 !important;
    }

    /* CANVAS FRAME ----------------------------*/
    iframe {
        border-radius: 14px !important;
        box-shadow: 0 0 20px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* SPACING CLEANUP ----------------------------*/
    .css-1kyxreq {
        padding-top: 0 !important;
    }

</style>
""", unsafe_allow_html=True)
