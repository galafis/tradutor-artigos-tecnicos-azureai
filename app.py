"""
Aplicacao Streamlit para traducao de artigos tecnicos com Azure AI.
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
from src.translator import AzureTranslator


def extract_text_from_url(url: str) -> str:
    """Extrai texto de uma URL."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        article = soup.find("article") or soup.find("main") or soup.find("body")
        return article.get_text(separator="\n", strip=True) if article else ""
    except Exception as e:
        st.error(f"Erro ao extrair texto da URL: {e}")
        return ""


def main():
    st.set_page_config(
        page_title="Tradutor de Artigos Tecnicos - Azure AI",
        page_icon="🌐",
        layout="wide",
    )

    st.title("Tradutor de Artigos Tecnicos com Azure AI")
    st.markdown("Traduza artigos tecnicos com precisao terminologica usando Azure Translator e OpenAI.")

    st.sidebar.header("Configuracoes")

    target_lang = st.sidebar.selectbox(
        "Idioma de destino",
        ["pt-br", "en", "es", "fr", "de", "it", "ja", "ko", "zh-Hans"],
        index=0,
    )

    input_method = st.radio("Metodo de entrada", ["URL do artigo", "Texto direto"])

    article_text = ""

    if input_method == "URL do artigo":
        url = st.text_input("Insira a URL do artigo tecnico:")
        if url and st.button("Extrair texto"):
            with st.spinner("Extraindo texto do artigo..."):
                article_text = extract_text_from_url(url)
                if article_text:
                    st.session_state["article_text"] = article_text
                    st.success("Texto extraido com sucesso!")

        if "article_text" in st.session_state:
            article_text = st.session_state["article_text"]
            st.text_area("Texto extraido:", article_text, height=200)
    else:
        article_text = st.text_area(
            "Cole o texto do artigo tecnico:",
            height=300,
            placeholder="Cole aqui o texto do artigo que deseja traduzir...",
        )

    if st.button("Traduzir", type="primary") and article_text:
        try:
            translator = AzureTranslator()

            with st.spinner("Traduzindo artigo..."):
                lang_info = translator.detect_language(article_text)
                st.info(f"Idioma detectado: {lang_info['language']} (confianca: {lang_info['score']:.2%})")

                translated = translator.translate_article(article_text, target_lang)

            st.subheader("Artigo Traduzido")
            st.markdown(translated)

            st.download_button(
                label="Baixar traducao (Markdown)",
                data=translated,
                file_name="artigo_traduzido.md",
                mime="text/markdown",
            )
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Erro na traducao: {e}")


if __name__ == "__main__":
    main()
