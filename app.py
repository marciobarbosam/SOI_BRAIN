import streamlit as st
import requests
import base64
import time
from datetime import datetime

# --- CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="C.IA Command Center V3.9", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DE COMPETÊNCIAS (Ajustável pelos Sócios) ---
COMPETENCIAS = ["Lógica/Rigor", "Visão de Negócio", "Inovação Técnica", "Gestão de Risco", "Sintese/Objetividade"]

# --- CARREGAMENTO DE SECRETS ---
secret_token = st.secrets.get("GITHUB_TOKEN", "")
secret_user = st.secrets.get("GITHUB_USER", "")
secret_repo = st.secrets.get("GITHUB_REPO", "")

st.sidebar.title("⚙️ Configurações MAB_Master")

# Diagnóstico de Cofre
if secret_token and secret_user and secret_repo:
    st.sidebar.success("✅ Segredos Carregados do Cofre")
else:
    st.sidebar.warning("⚠️ Usando Configuração Manual (Cofre Vazio)")

github_token = st.sidebar.text_input("GitHub Token", value=secret_token, type="password")
repo_owner = st.sidebar.text_input("Usuário GitHub", value=secret_user)
repo_name = st.sidebar.text_input("Nome do Repo", value=secret_repo)

file_path = "MEMORIA.md"
catalog_path = "CATALOGO_ANEXOS.md"
guardians_path = "GUARDIANS.txt"
performance_path = "PERFORMANCE_C_IA.md"
verdicts_path = "VEREDITOS_FINAIS.md"
folder_anexos = "anexos"

st.title("🧠 Centro de Comando da C.IA")
st.subheader("Orquestração, Meritocracia e Auditoria de Competências")

# --- FUNÇÕES GITHUB ---

def get_github_content(path, default_content="# Novo Arquivo\n"):
    if not github_token or not repo_owner: return ""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    if 'content' in res:
        return base64.b64decode(res['content']).decode('utf-8')
    if res.get('message') == "Not Found":
        save_github_content(path, default_content)
        return default_content
    return ""

def save_github_content(path, content):
    if not github_token or not repo_owner: return
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    data = {"message": "Update SOI Knowledge", "content": encoded}
    if sha: data["sha"] = sha
    requests.put(url, headers=headers, json=data)

def upload_file_to_github(uploaded_file):
    if not github_token or not repo_owner: return False
    uploaded_file.seek(0)
    path = f"{folder_anexos}/{uploaded_file.name}"
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"}
    res_check = requests.get(url, headers=headers).json()
    sha = res_check.get('sha')
    content_encoded = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    data = {"message": f"Upload anexo: {uploaded_file.name}", "content": content_encoded}
    if sha: data["sha"] = sha
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in [200, 201]

def list_attachments():
    if not github_token or not repo_owner: return []
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_anexos}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    if isinstance(res, list): return [item['name'] for item in res]
    return []

def get_guardians_list():
    content = get_github_content(guardians_path, "Claude\nGemini\nChatGPT\nJEV IA")
    return [line.strip() for line in content.split("\n") if line.strip()]

def update_performance(ia_name, scores_dict):
    perf_content = get_github_content(performance_path, "# Performance C.IA\n")
    lines = perf_content.split("\n")
    found = False
    new_lines = []
    for line in lines:
        if f"IA: {ia_name}" in line:
            parts = line.split("|")
            try:
                count = int(parts[1].split(":")[1].strip())
                updated_scores = []
                for comp in COMPETENCIAS:
                    current_val = float(parts[2 + COMPETENCIAS.index(comp)].split(":")[1].strip())
                    new_val = (current_val * count + scores_dict[comp]) / (count + 1)
                    updated_scores.append(f"{comp}: {new_val:.2f}")
                new_line = f"IA: {ia_name} | Count: {count + 1} | " + " | ".join(updated_scores)
                new_lines.append(new_line)
                found = True
            except: new_lines.append(line)
        else:
            new_lines.append(line)
    if not found:
        scores_str = " | ".join([f"{comp}: {scores_dict[comp]:.2f}" for comp in COMPETENCIAS])
        new_lines.append(f"IA: {ia_name} | Count: 1 | {scores_//_str if False else scores_str}")
        # Correção para evitar erro de sintaxe:
        new_lines[-1] = f"IA: {ia_name} | Count: 1 | {scores_str}"
    save_github_content(performance_path, "\n".join(new_lines))

# --- INTERFACE*
