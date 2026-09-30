import streamlit as st
import requests
import base64
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="C.IA Command Center V4.9.4",
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
# CONFIGURAÇÃO GITHUB
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
# VALIDAÇÃO
# ============================================================

def github_configured():
    return bool(
        github_token
        and repo_owner
        and repo_name
    )


# ============================================================
# GITHUB — LEITURA
# ============================================================

def get_github_content(path, default_content=""):
    """
    Lê um arquivo do GitHub.

    Não cria automaticamente arquivos ausentes.
    Isso evita mascarar erros de caminho ou configuração.
    """

    if not github_configured():
        st.error(
            "GitHub não está configurado."
        )
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

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        # ----------------------------------------------------
        # ARQUIVO ENCONTRADO
        # ----------------------------------------------------

        if response.status_code == 200:

            data = response.json()

            if data.get("type") != "file":

                st.error(
                    f"O caminho '{path}' não aponta para um arquivo."
                )

                return ""

            encoded_content = data.get(
                "content",
                ""
            )

            if not encoded_content:

                st.warning(
                    f"O arquivo '{path}' foi encontrado, "
                    "mas não possui conteúdo retornado pela API."
                )

                return ""

            # A API do GitHub pode retornar Base64
            # com quebras de linha.
            encoded_content = encoded_content.replace(
                "\n",
                ""
            )

            try:

                decoded = base64.b64decode(
                    encoded_content
                ).decode("utf-8")

                return decoded

            except Exception as decode_error:

                st.error(
                    f"Erro ao decodificar '{path}': "
                    f"{decode_error}"
                )

                return ""

        # ----------------------------------------------------
        # ARQUIVO NÃO ENCONTRADO
        # ----------------------------------------------------

        elif response.status_code == 404:

            st.warning(
                f"Arquivo '{path}' não encontrado no "
                f"repositório '{repo_owner}/{repo_name}'."
            )

            return default_content

        # ----------------------------------------------------
        # TOKEN / PERMISSÃO
        # ----------------------------------------------------

        elif response.status_code in (401, 403):

            st.error(
                f"GitHub recusou o acesso a '{path}'. "
                f"HTTP {response.status_code}. "
                "Verifique o GITHUB_TOKEN e suas permissões."
            )

            return ""

        # ----------------------------------------------------
        # OUTROS ERROS
        # ----------------------------------------------------

        else:

            st.error(
                f"Erro ao ler '{path}'. "
                f"HTTP {response.status_code}: "
                f"{response.text}"
            )

            return ""

    except requests.RequestException as exc:

        st.error(
            f"Erro de conexão com GitHub ao ler "
            f"'{path}': {exc}"
        )

        return ""


# ============================================================
# GITHUB — ESCRITA
# ============================================================

def save_github_content(path, content):
    """
    Cria ou atualiza um arquivo no GitHub.
    """

    if not github_configured():

        st.error(
            "GitHub não está configurado."
        )

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

        # Verifica se o arquivo já existe
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        sha = None

        if response.status_code == 200:

            sha = response.json().get("sha")

        elif response.status_code != 404:

            st.error(
                f"Erro ao verificar '{path}': "
                f"HTTP {response.status_code} — "
                f"{response.text}"
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
            timeout=30
        )

        if response.status_code in (200, 201):

            return True

        st.error(
            f"Erro ao salvar '{path}': "
            f"HTTP {response.status_code} — "
            f"{response.text}"
        )

    except requests.RequestException as exc:

        st.error(
            f"Erro de conexão com GitHub: {exc}"
        )

    return False


# ============================================================
# ANEXOS
# ============================================================

def upload_file_to_github(uploaded_file):

    if not github_configured():
        return False

    uploaded_file.seek(0)

    path = (
        f"{PASTA_ANEXOS}/"
        f"{uploaded_file.name}"
    )

    url = (
        f"https://api.github.com/repos/"
        f"{repo_owner}/{repo_name}/contents/{path}"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    try:

        check = requests.get(
            url,
            headers=headers,
            timeout=20
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
            "message": (
                f"Upload: {uploaded_file.name}"
            ),
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
        f"{repo_owner}/{repo_name}/contents/"
        f"{PASTA_ANEXOS}"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20
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

    default = (
        "Claude\n"
        "Gemini\n"
        "ChatGPT\n"
        "JEV IA"
    )

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

def update_performance(
    ia_name,
    scores_dict
):

    perf_content = get_github_content(
        PERFORMANCE_PATH,
        "# Performance C.IA\n"
    )

    lines = perf_content.splitlines()

    found = False
    new_lines = []

    for line in lines:

        if not line.startswith(
            f"IA: {ia_name} |"
        ):

            new_lines.append(line)

            continue

        parts = [
