"""Streamlit app para analisar fachadas de bares Brahma.

Este aplicativo permite enviar imagens, PDFs ou arquivos PPTX e realizar uma
analise preliminar usando as APIs da OpenAI ou Gemini. O objetivo e servir
como ponto de partida para treinar um modelo mais robusto.
"""

from io import BytesIO
from pathlib import Path

import streamlit as st
from pptx import Presentation
from PIL import Image
import PyPDF2
import openai
import google.generativeai as genai


def analyze_with_openai(prompt: str, api_key: str) -> str:
    """Envia o prompt para a API da OpenAI e retorna a resposta.

    Esta implementacao e apenas ilustrativa. Substitua a chamada pela que
    preferir, por exemplo usando ``openai.ChatCompletion.create``.
    """

    openai.api_key = api_key
    # Exemplo simplificado
    return "Resultado gerado pela API OpenAI (exemplo)."


def analyze_with_gemini(prompt: str, api_key: str) -> str:
    """Envia o prompt para a API Gemini e retorna a resposta.

    Ajuste conforme o SDK oficial do Gemini.
    """

    genai.configure(api_key=api_key)
    return "Resultado gerado pela API Gemini (exemplo)."


def analyze_image(image: Image.Image, provider: str, api_key: str) -> str:
    """Realiza a analise de uma imagem usando o provedor escolhido."""

    prompt = "Analise a fachada presente na imagem."
    if provider == "OpenAI":
        return analyze_with_openai(prompt, api_key)
    return analyze_with_gemini(prompt, api_key)


def extract_images_from_pptx(file_bytes: BytesIO) -> list[Image.Image]:
    """Extrai e retorna todas as imagens de um arquivo PPTX."""

    pres = Presentation(file_bytes)
    images: list[Image.Image] = []
    for slide in pres.slides:
        for shape in slide.shapes:
            if hasattr(shape, "image"):
                images.append(Image.open(BytesIO(shape.image.blob)))
    return images


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extrai texto de um PDF para fins de exemplo."""

    reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def main() -> None:
    """Interface principal em Streamlit."""

    st.title("Oráculo de Fachadas Brahma")
    st.write(
        "Envie imagens, PDFs ou apresentações PPTX para obter um diagnóstico "
        "inicial. Informe sua chave da API para prosseguir."
    )

    provider = st.sidebar.selectbox("Provedor", ["OpenAI", "Gemini"])
    api_key = st.sidebar.text_input("API Key", type="password")

    uploaded = st.file_uploader(
        "Escolha um arquivo",
        type=["png", "jpg", "jpeg", "pdf", "pptx"],
    )
    text_input = st.text_area("Ou cole um texto para avaliar")

    if st.button("Analisar"):
        if not api_key:
            st.error("Informe a API key.")
            return

        if uploaded is not None:
            name = uploaded.name.lower()
            if name.endswith(".pptx"):
                images = extract_images_from_pptx(uploaded)
                for idx, img in enumerate(images):
                    st.image(img, caption=f"Slide {idx + 1}")
                    resp = analyze_image(img, provider, api_key)
                    st.write(resp)
            elif name.endswith(".pdf"):
                text = extract_text_from_pdf(uploaded.read())
                st.write("Texto extraído do PDF:")
                st.write(text)
                resp = (
                    analyze_with_openai(text, api_key)
                    if provider == "OpenAI"
                    else analyze_with_gemini(text, api_key)
                )
                st.write(resp)
            else:
                img = Image.open(uploaded)
                st.image(img, caption="Imagem enviada")
                resp = analyze_image(img, provider, api_key)
                st.write(resp)

        if text_input.strip():
            st.write("Analisando texto...")
            resp = (
                analyze_with_openai(text_input, api_key)
                if provider == "OpenAI"
                else analyze_with_gemini(text_input, api_key)
            )
            st.write(resp)

    st.sidebar.markdown("### Exemplos de Referência")
    sidebar_example_dir = Path("examples")
    correct = sidebar_example_dir / "correct_facade.png"
    incorrect = sidebar_example_dir / "incorrect_facade.png"
    if correct.exists():
        st.sidebar.image(str(correct), caption="Fachada correta")
    if incorrect.exists():
        st.sidebar.image(str(incorrect), caption="Fachada incorreta")


if __name__ == "__main__":
    main()
