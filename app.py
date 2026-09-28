import streamlit as st
import requests
import base64

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="C.IA Command Center", page_icon="🧠")

# Sidebar para configurações secretas
st.sidebar.title("⚙️ Configurações MAB_Master")
github_token = st.sidebar.text_input("GitHub Token", type="password")
repo_owner = st.sidebar.text_input("Usuário GitHub")
repo_name = st.sidebar.text_input("Nome do Repo (SOI_BRAIN)")
file_path = "MEMORIA.md"

st.title("🧠 C.IA Command Center")
st.subheader("Orquestração de Guardiões do SOI")

# Funções de conexão com GitHub
def get_memory():
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    if 'content' in res:
        return base64.b64decode(res['content']).decode('utf-8')
    return "Memória vazia."

def save_memory(new_content):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    encoded = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
    data = {"message": "Update C.IA", "content": encoded, "sha": sha}
    requests.put(url, headers=headers, json=data)

# --- INTERFACE PRINCIPAL ---
tab1, tab2 = st.tabs(["📥 Alimentar C.IA", "📤 Extrair Briefing"])

with tab1:
    st.write("### Registrar Insight de Guardião")
    ia_name = st.selectbox("Qual IA?", ["Claude", "Gemini", "ChatGPT", "Copilot", "Meta", "Perplexity", "Dola", "Grok", "DeepSeek", "Qwen", "Zapia", "Cursor", "Outra"])
    insight = st.text_area("O que a IA contribuiu?")
    
    if st.button("Sincronizar com GitHub"):
        if github_token and repo_owner:
            current_mem = get_memory()
            update = f"\n\n## [ENTRY] Guardião: {ia_name}\n{insight}"
            save_memory(current_mem + update)
            st.success("✅ Informação enviada ao Cérebro do SOI!")
        else:
            st.error("Preencha as configurações na barra lateral!")

with tab2:
    st.write("### Gerar Briefing para Nova IA")
    if st.button("Gerar Briefing Atualizado"):
        if github_token and repo_owner:
            mem = get_memory()
            briefing = f"Olá, você é um Guardião do C.IA no projeto SOI (Sistema Operativo e Intelligenza).\n\nSua missão é atuar como especialista multidisciplinar. Abaixo está a MEMÓRIA ATUALIZADA do projeto. Leia, absorva e prepare-se para contribuir:\n\n---\n{mem}\n---\n\nCom base nisso, qual sua análise?"
            st.text_area("Copie e cole na IA:", value=briefing, height=400)
        else:
            st.error("Preencha as configurações na barra lateral!")
