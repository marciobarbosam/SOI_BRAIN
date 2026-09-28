import streamlit as st
import requests
import base64
from datetime import datetime

# --- CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="C.IA Command Center V2", page_icon="🧠", layout="wide")

# Estilização para melhorar o visual
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar para configurações secretas
st.sidebar.title("⚙️ Configurações MAB_Master")
github_token = st.sidebar.text_input("GitHub Token", type="password")
repo_owner = st.sidebar.text_input("Usuário GitHub")
repo_name = st.sidebar.text_input("Nome do Repo (SOI_BRAIN)")
file_path = "MEMORIA.md"
folder_anexos = "anexos"

st.title("🧠 Centro de Comando da C.IA")
st.subheader("Orquestração de Guardiões do SOI")

# --- FUNÇÕES DE CONEXÃO GITHUB ---

def get_memory():
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    if 'content' in res:
        return base64.b64decode(res['content']).decode('utf-8')
    return "# Memória do C.IA\nIniciando registros..."

def save_memory(new_content):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    encoded = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
    data = {"message": "Update Memória C.IA", "content": encoded, "sha": sha}
    requests.put(url, headers=headers, json=data)

def upload_file_to_github(uploaded_file):
    # Caminho do arquivo dentro da pasta anexos
    path = f"{folder_anexos}/{uploaded_file.name}"
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"}
    
    # Verifica se o arquivo já existe para pegar o SHA
    res_check = requests.get(url, headers=headers).json()
    sha = res_check.get('sha')
    
    content_encoded = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    data = {"message": f"Upload anexo: {uploaded_file.name}", "content": content_encoded}
    if sha: data["sha"] = sha
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in [200, 201]

def list_attachments():
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_anexos}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    if isinstance(res, list):
        return [item['name'] for item in res]
    return []

# --- INTERFACE PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["📥 Alimentar C.IA", "📤 Extrair Briefing", "🔍 Pesquisar Memória"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### Registrar Insight de Guardião")
        ia_name = st.selectbox("Qual IA?", ["Claude", "Gemini", "ChatGPT", "Copilot", "Meta", "Perplexity", "Dola", "Grok", "DeepSeek", "Qwen", "Zapia", "Cursor", "Outra"])
        
        # Campo de texto com contador
        insight = st.text_area("O que a IA diz?", height=300, placeholder="Cole aqui a decisão ou insight da IA...")
        
        # Contador de caracteres
        st.caption(f"Tamanho do texto: {len(insight)} caracteres")
        
        if st.button("Sincronizar com GitHub"):
            if github_token and repo_owner:
                current_mem = get_memory()
                date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                update = f"\n\n## [ENTRY] Guardião: {ia_name} | Data: {date_str}\n{insight}"
                save_memory(current_mem + update)
                st.success("✅ Insight registrado no Cérebro do SOI!")
            else:
                st.error("Preencha as configurações na barra lateral!")

    with col2:
        st.write("### 📁 Upload de Anexos")
        uploaded_file = st.file_uploader("Escolha um arquivo", type=["pdf", "docx", "txt", "png", "jpg"])
        if uploaded_file is not None:
            if st.button("Subir Arquivo para o GitHub"):
                if github_token and repo_owner:
                    if upload_file_to_github(uploaded_file):
                        st.success(f"✅ Arquivo {uploaded_file.name} salvo em /anexos!")
                    else:
                        st.error("Erro ao subir arquivo. Verifique o Token.")
                else:
                    st.error("Preencha as configurações na barra lateral!")

with tab2:
    st.write("### Gerar Briefing para Nova IA")
    if st.button("Gerar Briefing Atualizado"):
        if github_token and repo_owner:
            mem = get_memory()
            files = list_attachments()
            files_str = ", ".join(files) if files else "Nenhum anexo disponível."
            
            briefing = (
                f"Olá, você é um Guardião do C.IA no projeto SOI (Sistema Operativo e Intelligenza).\n\n"
                f"Sua missão é atuar como especialista multidisciplinar. Abaixo está a MEMÓRIA ATUALIZADA do projeto.\n\n"
                f"📁 ARQUIVOS DISPONÍVEIS NO REPOSITÓRIO: {files_str}\n\n"
                f"--- MEMÓRIA ATUAL ---\n{mem}\n---\n\n"
                f"Com base nisso, qual sua análise?"
            )
            st.text_area("Copie e cole na IA:", value=briefing, height=500)
        else:
            st.error("Preencha as configurações na barra lateral!")

with tab3:
    st.write("### Buscar na Memória do SOI")
    search_term = st.text_input("Digite a palavra-chave (ex: 'Multi-tenant' ou 'Pizzas')")
    if search_term:
        if github_token and repo_owner:
            mem = get_memory()
            if search_term.lower() in mem.lower():
                st.success(f"Encontrado(s) menção(ões) a '{search_term}'!")
                # Divide a memória por entradas para mostrar apenas a parte relevante
                entries = mem.split("## [ENTRY]")
                found_entries = [e for e in entries if search_term.lower() in e.lower()]
                for entry in found_entries:
                    st.markdown(f"--- \n## [ENTRY]{entry}")
            else:
                st.warning("Nenhuma menção encontrada na memória atual.")
        else:
            st.error("Preencha as configurações na barra lateral!")
