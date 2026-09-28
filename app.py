import streamlit as st
import requests
import base64
from datetime import datetime

# --- CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="C.IA Command Center V2.2", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { font-size: 14px !important; }
    .file-card { padding: 10px; border: 1px solid #444; border-radius: 5px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar para configurações secretas
st.sidebar.title("⚙️ Configurações MAB_Master")
github_token = st.sidebar.text_input("GitHub Token", type="password")
repo_owner = st.sidebar.text_input("Usuário GitHub")
repo_name = st.sidebar.text_input("Nome do Repo (SOI_BRAIN)")
file_path = "MEMORIA.md"
catalog_path = "CATALOGO_ANEXOS.md"
folder_anexos = "anexos"

st.title("🧠 Centro de Comando da C.IA")
st.subheader("Orquestração de Guardiões do SOI")

# --- FUNÇÕES DE CONEXÃO GITHUB ---

def get_github_content(path):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    if 'content' in res:
        return base64.b64decode(res['content']).decode('utf-8')
    return ""

def save_github_content(path, content):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    data = {"message": "Update SOI Knowledge", "content": encoded}
    if sha: data["sha"] = sha
    requests.put(url, headers=headers, json=data)

def upload_file_to_github(uploaded_file):
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
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_anexos}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    if isinstance(res, list):
        return [item['name'] for item in res]
    return []

# --- INTERFACE PRINCIPAL ---
tab1, tab2, tab3, tab4 = st.tabs(["📥 Alimentar C.IA", "📤 Extrair Briefing", "📚 Catálogo de Anexos", "🔍 Pesquisar Memória"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("### Registrar Insight de Guardião")
        ia_name = st.selectbox("Qual IA?", ["Claude", "Gemini", "ChatGPT", "Copilot", "Meta", "Perplexity", "Dola", "Grok", "DeepSeek", "Qwen", "Zapia", "Cursor", "Outra"])
        insight = st.text_area("O que a IA diz?", height=300)
        st.caption(f"Tamanho do texto: {len(insight)} caracteres")
        if st.button("Sincronizar com GitHub"):
            if github_token and repo_owner:
                current_mem = get_github_content(file_path) or "# Memória do C.IA"
                date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                update = f"\n\n## [ENTRY] Guardião: {ia_name} | Data: {date_str}\n{insight}"
                save_github_content(file_path, current_mem + update)
                st.success("✅ Insight registrado!")
            else: st.error("Preencha as configurações na barra lateral!")

    with col2:
        st.write("### 📁 Upload de Anexos")
        uploaded_files = st.file_uploader("Arquivos", type=["pdf", "docx", "txt", "png", "jpg"], accept_multiple_files=True)
        if uploaded_files and st.button("Subir todos os arquivos"):
            if github_token and repo_owner:
                for file in uploaded_files: upload_file_to_github(file)
                current_mem = get_github_content(file_path) or "# Memória do C.IA"
                names = ", ".join([f.name for f in uploaded_files])
                save_github_content(file_path, current_mem + f"\n\n## [SISTEMA] Anexos Adicionados: {names}")
                st.success(f"✅ {len(uploaded_files)} arquivos subidos!")
            else: st.error("Preencha as configurações na barra lateral!")

with tab2:
    st.write("### Gerar Briefing para Nova IA")
    if st.button("Gerar Briefing Atualizado"):
        if github_token and repo_owner:
            mem = get_github_content(file_path)
            catalog = get_github_content(catalog_path)
            files = list_attachments()
            files_str = ", ".join(files) if files else "Nenhum anexo."
            briefing = (f"Olá, você é um Guardião do C.IA no projeto SOI.\n\n"
                       f"📁 ARQUIVOS NO REPOSITÓRIO: {files_str}\n"
                       f"📖 RESUMOS DO CATÁLAGO:\n{catalog}\n\n"
                       f"--- MEMÓRIA ATUAL ---\n{mem}\n---\n\nQual sua análise?")
            st.text_area("Copie e cole na IA:", value=briefing, height=500)
        else: st.error("Preencha as configurações na barra lateral!")

with tab3:
    st.write("### 📚 Indexador de Documentos")
    st.info("Use as IAs para resumir os arquivos e cole o resumo aqui para indexar a busca.")
    files = list_attachments()
    if files:
        selected_file = st.selectbox("Selecione o arquivo para indexar:", files)
        summary = st.text_area(f"Resumo do arquivo {selected_file}:", height=150)
        if st.button("Salvar no Catálogo"):
            if github_token and repo_owner:
                catalog = get_github_content(catalog_path) or "# Catálogo de Anexos"
                # Remove resumo antigo do mesmo arquivo se existir
                lines = catalog.split("\n")
                new_lines = [l for l in lines if f"FILE: {selected_file}" not in l]
                updated_catalog = "\n".join(new_lines) + f"\n\nFILE: {selected_file}\nRESUMO: {summary}"
                save_github_content(catalog_path, updated_catalog)
                st.success("✅ Arquivo indexado com sucesso!")
            else: st.error("Preencha as configurações na barra lateral!")
    else:
        st.write("Nenhum anexo encontrado para indexar.")

with tab4:
    st.write("### 🔍 Pesquisa Global (Memória + Catálogo)")
    search_term = st.text_input("O que deseja buscar?")
    if search_term:
        if github_token and repo_owner:
            mem = get_github_content(file_path)
            cat = get_github_content(catalog_path)
            
            st.write("#### 📝 Na Memória:")
            if search_term.lower() in mem.lower():
                for entry in mem.split("## [ENTRY]"):
                    if search_term.lower() in entry.lower(): st.markdown(f"--- \n## [ENTRY]{entry}")
            else: st.write("Nada encontrado na memória.")
            
            st.write("#### 📁 Nos Arquivos (Catálogo):")
            if search_term.lower() in cat.lower():
                for item in cat.split("FILE: "):
                    if search_term.lower() in item.lower(): st.markdown(f"--- \n**FILE:** {item}")
            else: st.write("Nada encontrado no catálogo.")
        else: st.error("Preencha as configurações na barra lateral!")
