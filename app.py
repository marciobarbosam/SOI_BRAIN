import streamlit as st
import requests
import base64
from datetime import datetime


# ============================================================
# CONFIGURAÇÃO DA APLICAÇÃO
# ============================================================

st.set_page_config(
    page_title="C.IA Command Center V5.0",
    page_icon="🧠",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }

    .stTextArea textarea {
        font-size: 14px !important;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONSTANTES
# ============================================================

COMPETENCIAS = [
    "Lógica/Rigor",
    "Visão de Negócio",
    "Inovação Técnica",
    "Gestão de Risco",
    "Sintese/Objetividade"
]

MEMORIA_PATH = "MEMORIA.md"
CATALOGO_PATH = "CATALOGO_ANEXOS.md"
GUARDIANS_PATH = "GUARDIANS.txt"
PERFORMANCE_PATH = "PERFORMANCE_C_IA.md"
VEREDICTOS_PATH = "VEREDITOS_FINAIS.md"
ANEXOS_PATH = "anexos"


# ============================================================
# CONFIGURAÇÃO DO GITHUB
# ============================================================

secret_token = st.secrets.get("GITHUB_TOKEN", "")
secret_user = st.secrets.get("GITHUB_USER", "")
secret_repo = st.secrets.get("GITHUB_REPO", "")

st.sidebar.title("⚙️ Configurações MAB_Master")

if secret_token and secret_user and secret_repo:
    st.sidebar.success("Segredos carregados")
else:
    st.sidebar.warning("Configuração manual")


github_token = st.sidebar.text_input(
    "GitHub Token",
    value=secret_token,
    type="password"
)

repo_owner = st.sidebar.text_input(
    "Usuário GitHub",
    value=secret_user
)

repo_name = st.sidebar.text_input(
    "Nome do Repositório",
    value=secret_repo
)


# ==========
