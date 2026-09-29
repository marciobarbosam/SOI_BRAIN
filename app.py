import streamlit as st
import requests
import base64
from datetime import datetime

# --- CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="C.IA Command Center V2.9", page_icon="🧠", layout="wide")

# --- CARREGAMENTO DE SECRETS ---
secret_token = st.secrets.get("GITHUB_TOKEN", "")
secret_user = st.secrets.get("GITHUB_USER", "")
secret_repo = st.secrets.get("GITHUB_REPO", "")

st.sidebar.title("⚙️ Configurações MAB_Master")
github_token = st.sidebar.text_input("GitHub Token", value=secret_token, type="password")
repo_owner = st.sidebar.text_input("Usuário GitHub", value=secret_user)
repo_name = st.sidebar.text_input("Nome do Repo", value=secret_repo)

file_path = "MEMORIA.md"

st.title("🧠 Centro de Comando da C.IA")
st.subheader("Modo de Resgate e Diagnóstico")

# --- FUNÇÕES SIMPLIFICADAS ---

def test_write_simple():
    """Tenta criar um arquivo simples na raiz para testar a escrita"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/teste_conexao.txt"
    headers = {"Authorization": f"token {github_token}"}
    content = base64.b64encode("Teste de escrita C.IA".encode('utf-8')).decode('utf-8')
    
    # Tenta pegar o SHA caso já exista
    res_check = requests.get(url, headers=headers).json()
    sha = res_check.get('sha')
    
    data = {"message": "Teste de escrita", "content": content}
    if sha: data["sha"] = sha
    
    res = requests.put(url, headers=headers, json=data)
    return res.status_code, res.text, url

def upload_to_root(uploaded_file):
    """Sobe o arquivo na RAIZ do repo, sem pastas"""
    # URL DIRETA NA RAIZ
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{uploaded_file.name}"
    headers = {"Authorization": f"token {github_token}"}
    
    res_check = requests.get(url, headers=headers).json()
    sha = res_check.get('sha')
    
    content_encoded = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    data = {"message": f"Upload raiz: {uploaded_file.name}", "content": content_encoded}
    if sha: data["sha"] = sha
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code, response.text, url

# --- INTERFACE ---
tab1, tab2 = st.tabs(["🛠️ Diagnóstico de Escrita", "📤 Upload Raiz"])

with tab1:
    st.write("### Teste de Permissão de Escrita")
    st.info("Este botão tenta criar um arquivo chamado 'teste_conexao.txt' na raiz do seu GitHub.")
    
    if st.button("Executar Teste de Escrita"):
        if github_token and repo_owner:
            status, texto, url = test_write_simple()
            st.write(f"**URL acessada:** `{url}`")
            if status in [200, 201]:
                st.success("✅ SUCESSO! O app consegue escrever no seu GitHub.")
            else:
                st.error(f"❌ FALHA! Erro {status}. Resposta do GitHub: {texto}")
        else:
            st.error("Preencha as configurações na barra lateral!")

with tab2:
    st.write("### Upload Direto na Raiz")
    st.warning("Nesta versão, os arquivos NÃO vão para a pasta /anexos. Eles vão para a página principal do seu GitHub.")
    
    uploaded_file = st.file_uploader("Escolha UM arquivo", type=["pdf", "docx", "txt", "png", "jpg"])
    
    if uploaded_file is not None:
        if st.button("Subir para Raiz"):
            if github_token and repo_owner:
                status, texto, url = upload_to_root(uploaded_file)
                st.write(f"**URL de Upload:** `{url}`")
                if status in [200, 201]:
                    st.success(f"✅ {uploaded_file.name} subido com sucesso para a raiz!")
                else:
                    st.error(f"❌ Erro {status}. Resposta: {texto}")
            else:
                st.error("Preencha as configurações na barra lateral!")
