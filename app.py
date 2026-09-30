```python
import streamlit as st
import requests
import base64
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="C.IA Command Center V4.9.3",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
.stTextArea textarea {
    font-size: 14px !important;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)


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
PASTA_ANEXOS = "anexos"

# ============================================================
# SEGREDOS / CONFIGURAÇÃO GITHUB
# ============================================================

secret_token = st.secrets.get("GITHUB_TOKEN", "")
secret_user = st.secrets.get("GITHUB_USER", "")
secret_repo = st.secrets.get("GITHUB_REPO", "")

st.sidebar.title("Configurações MAB_Master")

if secret_token and secret_user and secret_repo:
    st.sidebar.success("Segredos carregados")
else:
    st.sidebar.warning("Usando configuração manual")

github_token = st.sidebar.text_input(
    "GitHub Token",
    value=secret_token,
    type="password",
    key="sb_token"
)

repo_owner = st.sidebar.text_input(
    "Usuário GitHub",
    value=secret_user,
    key="sb_user"
)

repo_name = st.sidebar.text_input(
    "Nome do Repo",
    value=secret_repo,
    key="sb_repo"
)


# ============================================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# ============================================================

def github_configured():
    return bool(github_token and repo_owner and repo_name)


# ============================================================
# GITHUB — LEITURA
# ============================================================

def get_github_content(path, default_content=""):
    """
    Lê um arquivo do GitHub.

    Se o arquivo não existir, cria automaticamente usando
    save_github_content().
    """

    if not github_configured():
        return ""

    url = (
        f"https://api.github.com/repos/"
        f"{repo_owner}/{repo_name}/contents/{path}"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()

            if "content" in data:
                return base64.b64decode(
                    data["content"]
                ).decode("utf-8")

        elif response.status_code == 404:
            save_github_content(path, default_content)
            return default_content

        else:
            st.error(
                f"Erro ao ler {path}: "
                f"{response.status_code} — {response.text}"
            )

    except requests.RequestException as exc:
        st.error(f"Erro de conexão com GitHub: {exc}")

    return ""


# ============================================================
# GITHUB — ESCRITA
# ============================================================

def save_github_content(path, content):
    """
    Cria ou atualiza um arquivo no GitHub.
    """

    if not github_configured():
        return False

    url = (
        f"https://api.github.com/repos/"
        f"{repo_owner}/{repo_name}/contents/{path}"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    try:
        # Primeiro verifica se o arquivo já existe
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        sha = None

        if response.status_code == 200:
            sha = response.json().get("sha")

        elif response.status_code != 404:
            st.error(
                f"Erro ao verificar {path}: "
                f"{response.status_code} — {response.text}"
            )
            return False

        encoded = base64.b64encode(
            content.encode("utf-8")
        ).decode("utf-8")

        data = {
            "message": "Update SOI / C.IA",
            "content": encoded
        }

        if sha:
            data["sha"] = sha

        response = requests.put(
            url,
            headers=headers,
            json=data,
            timeout=20
        )

        if response.status_code in (200, 201):
            return True

        st.error(
            f"Erro ao salvar {path}: "
            f"{response.status_code} — {response.text}"
        )

    except requests.RequestException as exc:
        st.error(f"Erro de conexão com GitHub: {exc}")

    return False


# ============================================================
# ANEXOS
# ============================================================

def upload_file_to_github(uploaded_file):
    if not github_configured():
        return False

    uploaded_file.seek(0)

    path = f"{PASTA_ANEXOS}/{uploaded_file.name}"

    url = (
        f"https://api.github.com/repos/"
        f"{repo_owner}/{repo_name}/contents/{path}"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    try:
        # Verifica se já existe
        check = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        sha = None

        if check.status_code == 200:
            sha = check.json().get("sha")

        elif check.status_code != 404:
            return False

        content_encoded = base64.b64encode(
            uploaded_file.getvalue()
        ).decode("utf-8")

        data = {
            "message": f"Upload: {uploaded_file.name}",
            "content": content_encoded
        }

        if sha:
            data["sha"] = sha

        response = requests.put(
            url,
            headers=headers,
            json=data,
            timeout=30
        )

        return response.status_code in (200, 201)

    except requests.RequestException:
        return False


def list_attachments():
    if not github_configured():
        return []

    url = (
        f"https://api.github.com/repos/"
        f"{repo_owner}/{repo_name}/contents/{PASTA_ANEXOS}"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, list):
                return [
                    item["name"]
                    for item in data
                    if item.get("type") == "file"
                ]

    except requests.RequestException:
        pass

    return []


# ============================================================
# GUARDIÕES
# ============================================================

def get_guardians_list():
    default = "Claude\nGemini\nChatGPT\nJEV IA"

    content = get_github_content(
        GUARDIANS_PATH,
        default
    )

    return [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]


# ============================================================
# PERFORMANCE
# ============================================================

def update_performance(ia_name, scores_dict):
    """
    Atualiza a média histórica de uma IA.

    Formato:
    IA: Nome | Count: 3 | Lógica/Rigor: 4.00 | ...
    """

    perf_content = get_github_content(
        PERFORMANCE_PATH,
        "# Performance C.IA\n"
    )

    lines = perf_content.splitlines()

    found = False
    new_lines = []

    for line in lines:

        if not line.startswith(f"IA: {ia_name} |"):
            new_lines.append(line)
            continue

        parts = [p.strip() for p in line.split("|")]

        try:
            count = int(
                parts[1].split(":", 1)[1].strip()
            )

            old_scores = {}

            for part in parts[2:]:
                if ":" not in part:
                    continue

                name, value = part.split(":", 1)

                if name.strip() in COMPETENCIAS:
                    old_scores[name.strip()] = float(
                        value.strip()
                    )

            updated_scores = {}

            for comp in COMPETENCIAS:
                current_value = old_scores.get(comp, 0.0)
                new_value = (
                    (current_value * count)
                    + scores_dict[comp]
                ) / (count + 1)

                updated_scores[comp] = new_value

            score_text = " | ".join(
                f"{comp}: {updated_scores[comp]:.2f}"
                for comp in COMPETENCIAS
            )

            new_lines.append(
                f"IA: {ia_name} | "
                f"Count: {count + 1} | "
                f"{score_text}"
            )

            found = True

        except (ValueError, IndexError):
            new_lines.append(line)

    if not found:

        score_text = " | ".join(
            f"{comp}: {scores_dict[comp]:.2f}"
            for comp in COMPETENCIAS
        )

        new_lines.append(
            f"IA: {ia_name} | Count: 1 | {score_text}"
        )

    save_github_content(
        PERFORMANCE_PATH,
        "\n".join(new_lines)
    )


# ============================================================
# CABEÇALHO
# ============================================================

st.title("Centro de Comando da C.IA")
st.subheader(
    "Orquestração, Meritocracia e Auditoria de Competências"
)


# ============================================================
# ABAS
# ============================================================

(
    tab1,
    tab2,
    tab3,
    tab4,
    tab5,
    tab6,
    tab7,
    tab8
) = st.tabs([
    "Alimentar",
    "Briefing",
    "Catálogo",
    "Pesquisa",
    "Missão",
    "Consolidação",
    "Guardiões",
    "Meritocracia"
])


# ============================================================
# TAB 1 — ALIMENTAR
# ============================================================

with tab1:

    st.write("### Registrar Insight")

    col_main, col_side = st.columns([2, 1])

    with col_main:

        ia_name = st.selectbox(
            "Qual IA?",
            get_guardians_list(),
            key="sel_ia_1"
        )

        insight = st.text_area(
            "Parecer da IA",
            height=300,
            key="txt_insight_1"
        )

        st.write("#### Avaliação de Competência")

        scores = {}

        cols_score = st.columns(
            len(COMPETENCIAS)
        )

        for i, comp in enumerate(COMPETENCIAS):

            scores[comp] = cols_score[i].slider(
                comp,
                1,
                5,
                3,
                key=f"sl_{i}_1"
            )

    with col_side:

        st.write("### Anexos")

        uploaded_files = st.file_uploader(
            "Arquivos",
            accept_multiple_files=True,
            key="up_files_1"
        )

        if uploaded_files and st.button(
            "Subir",
            key="btn_up_1"
        ):

            if not github_configured():

                st.error(
                    "Configure o GitHub na barra lateral."
                )

            else:

                success = 0

                for file in uploaded_files:

                    if upload_file_to_github(file):
                        success += 1

                current_mem = get_github_content(
                    MEMORIA_PATH,
                    "# Memoria do C.IA"
                )

                names = ", ".join(
                    f.name for f in uploaded_files
                )

                update = (
                    f"\n\n## [SISTEMA] Anexos: {names}"
                )

                save_github_content(
                    MEMORIA_PATH,
                    current_mem + update
                )

                st.success(
                    f"{success} arquivo(s) enviado(s)."
                )

        st.divider()

        if st.button(
            "Sincronizar",
            key="btn_sync_1",
            use_container_width=True
        ):

            if not github_configured():

                st.error(
                    "Preencha as configurações do GitHub "
                    "na barra lateral."
                )

            elif not insight.strip():

                st.error(
                    "Digite o parecer da IA."
                )

            else:

                # Validação corrigida
                insight_lower = insight.lower()

                has_self_evaluation = (
                    "autoavaliação" in insight_lower
                    or "autoavaliacao" in insight_lower
                    or "auto-avaliação" in insight_lower
                    or "auto-avaliacao" in insight_lower
                )

                if not has_self_evaluation:

                    st.error(
                        "O parecer deve conter a "
                        "AUTOAVALIAÇÃO da IA."
                    )

                else:

                    current_mem = get_github_content(
                        MEMORIA_PATH,
                        "# Memoria do C.IA"
                    )

                    score_str = ", ".join(
                        f"{c}: {s}S"
                        for c, s in scores.items()
                    )

                    update = (
                        f"\n\n## [ENTRY] Guardiao: {ia_name} | "
                        f"Data: "
                        f"{datetime.now().strftime('%d/%m/%Y %H:%M')} | "
                        f"{score_str}\n"
                        f"{insight}"
                    )

                    if save_github_content(
                        MEMORIA_PATH,
                        current_mem + update
                    ):

                        update_performance(
                            ia_name,
                            scores
                        )

                        st.success(
                            "Registro sincronizado com sucesso."
                        )


# ============================================================
# TAB 2 — BRIEFING
# ============================================================

with tab2:

    if st.button(
        "Gerar Briefing",
        key="btn_gen_brief"
    ):

        if not github_configured():

            st.error(
                "Configure o GitHub na barra lateral."
            )

        else:

            mem = get_github_content(
                MEMORIA_PATH,
                "# Sem memoria"
            )

            files = list_attachments()

            briefing = (
                "Olá Guardião do SOI.\n\n"
                f"ARQUIVOS: {', '.join(files) or 'Nenhum'}\n\n"
                "--- MEMÓRIA ---\n"
                f"{mem}\n"
                "---\n"
                "Qual sua análise?"
            )

            st.text_area(
                "Copie:",
                value=briefing,
                height=500,
                key="txt_briefing"
            )


# ============================================================
# TAB 3 — CATÁLOGO
# ============================================================

with tab3:

    files = list_attachments()

    if files:

        selected = st.selectbox(
            "Arquivo:",
            files,
            key="sel_file_cat"
        )

        summary = st.text_area(
            "Resumo do arquivo:",
            key="txt_sum_cat"
        )

        if st.button(
            "Salvar",
            key="btn_save_cat"
        ):

            cat = get_github_content(
                CATALOGO_PATH,
                "# Catalogo"
            )

            lines = [
                line
                for line in cat.splitlines()
                if f"FILE: {selected}" not in line
            ]

            new_content = (
                "\n".join(lines)
                + f"\n\nFILE: {selected}"
                + f"\nRESUMO: {summary}"
            )

            save_github_content(
                CATALOGO_PATH,
                new_content
            )

            st.success("Arquivo indexado.")

    else:

        st.info("Nenhum anexo.")


# ============================================================
# TAB 4 — PESQUISA
# ============================================================

with tab4:

    term = st.text_input(
        "Buscar:",
        key="search_term"
    )

    if term:

        mem = get_github_content(
            MEMORIA_PATH,
            ""
        )

        cat = get_github_content(
            CATALOGO_PATH,
            ""
        )

        found = False

        if term.lower() in mem.lower():

            st.write("#### Memória")
            st.text_area(
                "Resultado",
                value=mem,
                height=400,
                key="search_mem_result"
            )

            found = True

        if term.lower() in cat.lower():

            st.write("#### Catálogo")
            st.text_area(
                "Resultado",
                value=cat,
                height=300,
                key="search_cat_result"
            )

            found = True

        if not found:

            st.info(
                "Nenhum resultado encontrado."
            )


# ============================================================
# TAB 5 — MISSÃO
# ============================================================

with tab5:

    st.write("### Missão")

    mission_text = st.text_area(
        "Defina a Missão:",
        key="txt_mission"
    )

    guardians = get_guardians_list()

    if "mission_status" not in st.session_state:

        st.session_state.mission_status = {
            g: "Pendente"
            for g in guardians
        }

    # Garante novos guardiões
    for g in guardians:

        if g not in st.session_state.mission_status:

            st.session
```
