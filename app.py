import streamlit as st
import requests
import base64
import time
from datetime import datetime

# --- CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="C.IA Command Center V3.9.1", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DE COMPETÊNCIAS ---
COMPETENCIAS = ["Lógica/Rigor", "Visão de Negócio", "Inovação Técnica", "Gestão de Risco", "Sintese/Objetividade"]

# --- SECRETS ---
secret_token = st.secrets.get("GITHUB_TOKEN", "")
secret_user = st.secrets.get("GITHUB_USER", "")
secret_repo = st.secrets.get("GITHUB_REPO", "")

st.sidebar.title("⚙️ Configurações MAB_Master")

if secret_token and secret_user and secret_repo:
    st.sidebar.success("✅ Segredos Carregados do Cofre")
else:
    st.sidebar.warning("⚠️ Usando Configuração Manual")

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

# --- FUNÇÕES AUXILIARES (SIMPLIFICADAS) ---
def get_content(path, default="# Novo Arquivo\n"):
    if not github_token or not repo_owner: return ""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    if 'content' in res: return base64.b64decode(res['content']).decode('utf-8')
    if res.get('message') == "Not Found":
        save_content(path, default)
        return default
    return ""

def save_content(path, content):
    if not github_token or not repo_owner: return
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    sha = res.get('sha')
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    data = {"message": "Update SOI", "content": encoded}
    if sha: data["sha"] = sha
    requests.put(url, headers=headers, json=data)

def upload_file(uploaded_file):
    if not github_token or not repo_//_owner: return False # Corrigido abaixo
    return False # Placeholder para evitar erro, a função real está abaixo

# Correção da função upload
def upload_file_final(uploaded_file):
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

def get_guardians():
    content = get_content(guardians_path, "Claude\nGemini\nChatGPT\nJEV IA")
    return [line.strip() for line in content.split("\n") if line.strip()]

# --- ABERTURA DAS ABAS ---
tabs = st.tabs(["📥 Alimentar", "📤 Briefing", "📚 Catálogo", "🔍 Pesquisa", "🎯 Missão", "📊 Consolidação", "👥 Guardiões", "🏆 Meritocracia"])

with tabs[0]:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("### Registrar Insight")
        ia_name = st.selectbox("Qual IA?", get_guardians())
        insight = st.text_area("O que a IA diz?", height=300)
        st.write("#### Avaliação de Competência")
        scores = {}
        cols_score = st.columns(len(COMPETENCIAS))
        for i, comp in enumerate(COMPETENCIAS):
            scores[comp] = cols_score[i].slider(comp, 1, 5, 3)
        if st.button("Sincronizar"):
            if github_token and repo_owner:
                current_mem = get_content(file_path, "# Memória do C.IA")
                score_str = ", ".join([f"{c}: {s}⭐" for c, s in scores.items()])
                update = f"\n\n## [ENTRY] Guardião: {ia_name} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} | {score_str}\n{insight}"
                save_content(file_path, current_mem + update)
                # Update Performance
                perf = get_content(performance_path, "# Performance\n")
                lines = perf.split("\n")
                found = False
                new_lines = []
                for line in lines:
                    if f"IA: {ia_name}" in line:
                        parts = line.split("|")
                        try:
                            count = int(parts[1].split(":")[1].strip())
                            up_scores = []
                            for comp in COMPETENCIAS:
                                cur_val = float(parts[2 + COMPETENCIAS.index(comp)].split(":")[1].strip())
                                new_val = (cur_val * count + scores[comp]) / (count + 1)
                                up_scores.append(f"{comp}: {new_val:.2f}")
                            new_lines.append(f"IA: {ia_name} | Count: {count + 1} | " + " | ".join(up_scores))
                            found = True
                        except: new_lines.append(line)
                    else: new_lines.append(line)
                if not found:
                    s_str = " | ".join([f"{c}: {scores[c]:.2f}" for c in COMPETENCIAS])
                    new_lines.append(f"IA: {ia_name} | Count: 1 | {s_str}")
                save_content(performance_path, "\n".join(new_lines))
                st.success("✅ Registrado!")

    with col2:
        st.write("### 📁 Anexos")
        uploaded_files = st.file_uploader("Arquivos", accept_multiple_files=True)
        if uploaded_files and st.button("Subir"):
            if github_token and repo_owner:
                for f in uploaded_files: upload_file_final(f)
                save_content(file_path, get_content(file_path, "# Memória") + f"\n\n## [SISTEMA] Anexos: {', '.join([f.name for f in uploaded_files])}")
                st.success("✅ Subidos!")

with tabs[1]:
    if st.button("Gerar Briefing"):
        if github_token and repo_owner:
            mem = get_content(file_//_path, "# Sem memória")
            # Correção
            mem = get_content(file_path, "# Sem memória")
            files = []
            url_files = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_anexos}"
            res_f = requests.get(url_files, headers={"Authorization": f"token {github_token}"}).json()
            if isinstance(res_f, list): files = [i['name'] for i in res_f]
            briefing = f"Olá Guardião do SOI.\n\n📁 ARQUIVOS: {', '.join(files)}\n\n--- MEMÓRIA ---\n{mem}\n---\nQual sua análise?"
            st.text_area("Copie:", value=briefing, height=500)

with tabs[2]:
    files = list_attachments()
    if files:
        selected = st.selectbox("Arquivo:", files)
        summary = st.text_//_area(f"Resumo {selected}:") # Erro
        summary = st.text_area(f"Resumo {selected}:")
        if st.button("Salvar"):
            cat = get_content(catalog_path, "# Catálogo")
            lines = [l for l in cat.split("\n") if f"FILE: {selected}" not in l]
            save_content(catalog_path, "\n".join(lines) + f"\n\nFILE: {selected}\nRESUMO: {summary}")
            st.success("✅ Indexado!")
    else: st.info("Nenhum anexo encontrado.")

with tabs[3]:
    term = st.text_input("Buscar:")
    if term:
        mem = get_content(file_path, "")
        cat = get_content(catalog_path, "")
        if term.lower() in mem.lower(): st.write("#### Memória:", mem)
        if term.lower() in cat.lower(): st.write("#### Catálogo:", cat)

with tabs[4]:
    st.write("### 🎯 Missão")
    mission_text = st.text_area("Defina a Missão:")
    guardians = get_guardians()
    if "mission_status" not in st.session_state: st.session_state.mission_status = {g: "🟡 Pendente" for g in guardians}
    cols_m = st.columns([3, 2, 2])
    cols_m[0].write("**Guardião**"); cols_m[1].write("**Status**"); cols_m[2].write("**Ação**")
    for g in guardians:
        c1, c2, c3 = st.columns([3, 2, 2])
        c1.write(g)
        status = st.session_state.mission_status.get(g, "🟡 Pendente")
        color = "yellow" if "Pendente" in status else "blue" if "Enviado" in status else "green"
        c2.markdown(f'<span style="color:{color}; font-weight:bold;">{status}</span>', unsafe_allow_html=True)
        if status == "🟡 Pendente":
            if c3.button(f"Copiar", key=f"btn_{g}"):
                mem = get_content(file_path, "# Sem memória")
                st.code(f"⚠️ MISSÃO: {mission_text}\n\n--- CONTEXTO ---\n{mem}")
                st.session_state.mission_status[g] = "🔵 Enviado"
                st.rerun()
        elif status == "🔵 Enviado":
            if c3.button(f"Registrar", key=f"res_{g}"):
                st.session_state.current_target_ia = g
                st.session_state.show_response_box = True

    if st.session_state.get("show_response_box", False):
        st.divider()
        target = st.session_state.current_target_ia
        response = st.text_area(f"Resposta de {target}:")
        m_scores = {}
        m_cols = st.columns(len(COMPETENCIAS))
        for i, comp in enumerate(COMPETENCIAS):
            m_scores[comp] = m_cols[i].slider(comp, 1, 5, 3)
        if st.button("Salvar no Cérebro"):
            current_mem = get_content(file_path, "# Memória do C.IA")
            score_str = ", ".join([f"{c}: {s}⭐" for c, s in m_scores.items()])
            update = f"\n\n## [MISSÃO] Resposta de {target} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} | {score_str}\n{response}"
            save_content(file_path, current_mem + update)
            update_performance(target, m_scores)
            st.session_state.mission_status[target] = "🟢 Respondido"
            st.session_state.show_response_box = False
            st.rerun()

with tab6:
    st.write("### 📊 Consolidação")
    mem = get_content(file_path, "# Sem memória")
    mission_entries = [e for e in mem.split("## [MISSÃO]") if e.strip()]
    if mission_entries:
        search_mission = st.text_input("Filtre a Missão:")
        relevant = [e for e in mission_entries if search_mission.lower() in e.lower()] if search_mission else mission_entries
        if relevant:
            combined = ""
            for entry in relevant: combined += f"\n---\n{entry}"
            if st.button("Gerar Briefing de Consolidação"):
                prompt = (f"Você é o CHEFE DE GABINETE do C.IA. Realize a síntese final seguindo a MATRIZ de DECISÃO (Impacto, Solução, Benefício, Prejuízo, Melhor Opção). \n\n{combined}")
                st.text_area("Briefing Consolidador:", value=prompt, height=500)

with tab7:
    st.write("### 👥 Guard*
