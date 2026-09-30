import streamlit as st
import requests

st.set_page_config(
    page_title="Teste C.IA",
    page_icon="🧠"
)

st.title("🧠 C.IA — Teste de Conexão")

st.write("Aplicação carregada corretamente.")

token = st.secrets.get("GITHUB_TOKEN", "")
user = st.secrets.get("GITHUB_USER", "")
repo = st.secrets.get("GITHUB_REPO", "")

st.subheader("Credenciais detectadas")

st.write("Token:", "✅ Encontrado" if token else "❌ Não encontrado")
st.write("Usuário:", user if user else "❌ Não encontrado")
st.write("Repositório:", repo if repo else "❌ Não encontrado")

st.divider()

if st.button("🔎 Testar GitHub"):

    if not token or not user or not repo:

        st.error("As credenciais do GitHub não estão completas.")

    else:

        url = f"https://api.github.com/repos/{user}/{repo}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=20
            )

            st.write("HTTP:", response.status_code)

            if response.status_code == 200:

                data = response.json()

                st.success("✅ GitHub conectado corretamente.")

                st.write(
                    "Repositório:",
                    data.get("full_name")
                )

            else:

                st.error(
                    f"GitHub respondeu HTTP {response.status_code}"
                )

                st.code(response.text)

        except Exception as error:

            st.error(
                f"Erro de conexão: {error}"
            )

st.divider()

if st.button("📖 Ler MEMORIA.md"):

    if not token or not user or not repo:

        st.error("Credenciais incompletas.")

    else:

        url = (
            f"https://api.github.com/repos/"
            f"{user}/{repo}/contents/MEMORIA.md"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=20
            )

            st.write(
                "HTTP:",
                response.status_code
            )

            if response.status_code == 200:

                import base64

                data = response.json()

                content = base64.b64decode(
                    data["content"].replace("\n", "")
                ).decode("utf-8")

                st.success(
                    f"MEMORIA.md lida com sucesso — "
                    f"{len(content)} caracteres."
                )

                st.text_area(
                    "Conteúdo:",
                    content,
                    height=500
                )

            else:

                st.error(
                    f"Não foi possível ler MEMORIA.md. "
                    f"HTTP {response.status_code}"
                )

                st.code(response.text)

        except Exception as error:

            st.error(
                f"Erro ao ler MEMORIA.md: {error}"
            )
