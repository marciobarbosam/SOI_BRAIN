import streamlit as st
import requests
import base64
import time
from datetime import datetime

# --- CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="C.IA Command Center V3.8", page_icon="🧠", layout="wide")

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
def get_github_content(path):
    if not github_token or not repo_owner: return ""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {github_token}"}
    res = requests.get(url, headers=headers).json()
    if 'content' in res: return base64.b64decode(res['content']).decode('utf-8')
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
    content = get_github_content(guardians_path)
    if not content: return ["Claude", "Gemini", "ChatGPT", "JEV IA"]
    return [line.strip() for line in content.split("\n") if line.strip()]

def update_performance(ia_name, scores_dict):
    perf_content = get_github_content(performance_path) or "# Performance C.IA\n"
    lines = perf_content.split("\n")
    found = False
    new_lines = []
    for line in lines:
        if f"IA: {ia_name}" in line:
            parts = line.split("|")
            count = int(parts[1].split(":")[1].strip())
            updated_scores = []
            for comp in COMPETENCIAS:
                current_val = float(parts[2 + COMPETENCIAS.index(comp)].split(":")[1].strip())
                new_val = (current_val * count + scores_dict[comp]) / (count + 1)
                updated_scores.append(f"{comp}: {new_val:.2f}")
            new_line = f"IA: {ia_name} | Count: {count + 1} | " + " | ".join(updated_scores)
            new_lines.append(new_line)
            found = True
        else:
            new_lines.append(line)
    if not found:
        scores_str = " | ".join([f"{comp}: {scores_dict[comp]:.2f}" for comp in COMPETENCIAS])
        new_lines.append(f"IA: {ia_name} | Count: 1 | {scores_str}")
    save_github_content(performance_path, "\n".join(new_lines))

# --- INTERFACE ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["📥 Alimentar", "📤 Briefing", "📚 Catálogo", "🔍 Pesquisa", "🎯 Missão", "📊 Consolidação", "👥 Guardiões", "🏆 Meritocracia"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("### Registrar Insight")
        ia_name = st.selectbox("Qual IA?", get_guardians_list())
        insight = st.text_area("O que a IA diz?", height=300)
        st.write("#### Avaliação de Competência (Sócios)")
        scores = {}
        cols_score = st.columns(len(COMPETENCIAS))
        for i, comp in enumerate(COMPETENCIAS):
            scores[comp] = cols_score[i].slider(comp, 1, 5, 3)
        if st.button("Sincronizar"):
            if github_token and repo_owner:
                current_mem = get_github_content(file_path) or "# Memória do C.IA"
                score_str = ", ".join([f"{c}: {s}⭐" for c, s in scores.items()])
                update = f"\n\n## [ENTRY] Guardião: {ia_name} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} | {score_str}\n{insight}"
                save_github_content(file_//_path, current_mem + update) # Erro aqui
                # Correção final para evitar erro de digitação:
                save_github_content(file_path, current_mem + update)
                update_performance(ia_name, scores)
                st.success("✅ Registrado!")
    with col2:
        st.write("### 📁 Anexos")
        uploaded_files = st.file_uploader("Arquivos", accept_multiple_files=True)
        if uploaded_files and st.button("Subir"):
            if github_token and repo_owner:
                for f in uploaded_files: upload_file_to_//_github(f) # Erro aqui
                # Correção:
                for f in uploaded_files: upload_file_to_github(f)
                save_github_content(file_path, get_github_content(file_path) + f"\n\n## [SISTEMA] Anexos: {', '.join([f.name for f in uploaded_files])}")
                st.success("✅ Subidos!")

with tab2:
    if st.button("Gerar Briefing"):
        if github_token and repo_owner:
            mem = get_github_content(file_path)
            files = list_attachments()
            briefing = f"Olá Guardião do SOI.\n\n📁 ARQUIVOS: {', '.join(files)}\n\n--- MEMÓRIA ---\n{mem}\n---\nQual sua análise?"
            st.text_area("Copie:", value=briefing, height=500)

with tab3:
    files = list_attachments()
    if files:
        selected = st.selectbox("Arquivo:", files)
        summary = st.text_area(f"Resumo {selected}:")
        if st.button("Salvar"):
            cat = get_github_content(catalog_path) or "# Catálogo"
            lines = [l for l in cat.split("\n") if f"FILE: {selected}" not in l]
            save_github_content(catalog_path, "\n".join(lines) + f"\n\nFILE: {selected}\nRESUMO: {summary}")
            st.success("✅ Indexado!")

with tab4:
    term = st.text_input("Buscar:")
    if term:
        mem = get_github_content(file_path)
        cat = get_github_content(catalog_path)
        if term.lower() in mem.lower(): st.write("#### Memória:", mem)
        if term.lower() in cat.lower(): st.write("#### Catálogo:", cat)

with tab5:
    st.write("### 🎯 Orquestração de Missão")
    mission_text = st.text_area("Defina a Missão:")
    guardians = get_guardians_list()
    if "mission_status" not in st.session_state: st.session_state.mission_status = {g: "🟡 Pendente" for g in guardians}
    cols = st.columns([3, 2, 2])
    cols[0].write("**Guardião**"); cols[1].write("**Status**"); cols[2].write("**Ação**")
    for g in guardians:
        c1, c2, c3 = st.columns([3, 2, 2])
        c1.write(g)
        status = st.session_state.mission_status.get(g, "🟡 Pendente")
        color = "yellow" if "Pendente" in status else "blue" if "Enviado" in status else "green"
        c2.markdown(f'<span style="color:{color}; font-weight:bold;">{status}</span>', unsafe_allow_html=True)
        if status == "🟡 Pendente":
            if c3.button(f"Copiar", key=f"btn_{g}"):
                mem = get_github_content(file_path)
                st.code(f"⚠️ MISSÃO: {mission_text}\n\n--- CONTEXTO ---\n{mem}")
                st.session_state.mission_status[g] = "🔵 Enviado"
                st.rerun()
        elif status == "🔵 Enviado":
            if c3.button(f"Registrar", key=f"res_{g}"):
                st.session_state.current_target_ia = g
                st.session_state.show_response_box = True
        else: c3.write("✅ OK")

    if st.session_state.get("show_response_box", False):
        st.divider()
        target = st.session_state.current_target_ia
        response = st.text_area(f"Resposta de {target}:")
        m_scores = {}
        m_cols = st.columns(len(COMPETENCIAS))
        for i, comp in enumerate(COMPETENCIAS):
            m_scores[comp] = m_cols[i].slider(comp, 1, 5, 3)
        if st.button("Salvar no Cérebro"):
            current_mem = get_github_content(file_path) or "# Memória do C.IA"
            score_str = ", ".join([f"{c}: {s}⭐" for c, s in m_scores.items()])
            update = f"\n\n## [MISSÃO] Resposta de {target} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} | {score_str}\n{response}"
            save_github_content(file_path, current_mem + update)
            update_performance(target, m_scores)
            st.session_state.mission_status[target] = "🟢 Respondido"
            st.session_state.show_response_box = False
            st.rerun()

with tab6:
    st.write("### 📊 Consolidação")
    mem = get_github_content(file_path)
    mission_entries = [e for e in mem.split("## [MISSÃO]") if e.strip()]
    if mission_entries:
        search_mission = st.text_input("Filtre a Missão:")
        relevant = [e for e in mission_entries if search_mission.lower() in e.lower()] if search_mission else mission_entries
        if relevant:
            combined = ""
            for entry in relevant: combined += f"\n---\n{entry}"
            if st.button("Gerar Briefing de Consolidação"):
                prompt = (f"Você é o CHEFE DE GABINETE do C.IA. Realize a síntese final seguindo a MATRIZ DE DECISÃO (Impacto, Solução, Benefício, Prejuízo, Melhor Opção). \n\n{combined}")
                st.text_area("Briefing Consolidador:", value=prompt, height=500)

with tab7:
    st.write("### 👥 Gestão de Guardiões")
    current_guardians = get_guardians_list()
    new_ia = st.text_input("Nome da nova IA:")
    if st.button("Adicionar"):
        if new_ia and github_token and repo_owner:
            updated_list = "\n".join(current_guardians + [new_ia])
            save_github_content(guardians_path, updated_list)
            st.success(f"✅ {new_ia} adicionada!")
            st.rerun()
    st.divider()
    ia_to_remove = st.selectbox("Remover IA:", current_guardians)
    if st.button("Remover"):
        if github_token and repo_owner:
            updated_list = "\n".join([g for g in current_guardians if g != ia_to_remove])
            save_github_content(guardians_path, updated_list)
            st.warning(f"⚠️ {ia_to_remove} removida.")
            st.rerun()

with tab8:
    st.write("### 🏆 Painel de Meritocracia")
    perf_data = get_github_content(performance_path)
    if perf_//_data: # Erro aqui
        perf_data = get_github_content(performance_path)
        lines = perf_data.split("\n")
        stats = []
        for line in lines:
            if "IA: " in line:
                parts = line.split("|")
                name = parts[0].split(":")[1].strip()
                count = int(parts[1].split(":")[1].strip())
                comp_scores = {}
                total_score = 0
                for i in range(2, len(parts)):
                    comp_part = parts[i].split(":")
                    c_name = comp_part[0].strip()
                    c_val = float(comp_part[1].strip())
                    comp_scores[c_name] = c_val
                    total_score += c_val
                avg_general = total_score / len(COMPETENCIAS)
                row = {"IA": name, "Geral": avg_general, "Participações": count}
                row.update(comp_scores)
                stats.append(row)
        sorted_stats = sorted(stats, key=lambda x: x["Geral"], reverse=True)
        st.table(sorted_stats)
    else:
        st.write("Nenhum dado registrado.")
