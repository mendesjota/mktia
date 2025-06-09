"""Streamlit app para analisar fachadas de bares Brahma.

Este aplicativo permite enviar imagens, PDFs ou arquivos PPTX e realizar uma
analise preliminar usando as APIs da OpenAI ou Gemini. O objetivo e servir
como ponto de partida para treinar um modelo mais robusto.
"""

from io import BytesIO
from pathlib import Path
import base64

import streamlit as st
from pptx import Presentation
from PIL import Image, UnidentifiedImageError
import PyPDF2
import openai
import google.generativeai as genai


def analyze_with_openai(prompt: str, api_key: str) -> str:
    """Envia o prompt para a API da OpenAI e retorna a resposta.

    Esta implementacao e apenas ilustrativa. Substitua a chamada pela que
    preferir, por exemplo usando ``openai.ChatCompletion.create``.
    """

    openai.api_key = api_key
    messages_payload = []
    
    content_list = [{"type": "text", "text": prompt}]

    if image:
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=70) 
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        content_list.append({"type": "image_url", "image_url": {"url": f"data:image:jpeg;base64,{img_str}", "detail": "low"}})
        model_name = "gpt-4o"
    else:
        model_name = "gpt-3.5-turbo"

    messages_payload.append({"role": "user", "content": content_list})

    try:
        response = openai.chat.completions.create(
            model=model_name,
            messages=messages_payload,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        st.error(f"Erro da API OpenAI: {e.status_code} - {e.response.json().get('error', {}).get('message', 'Mensagem de erro não disponível')}")
        st.exception(e)
        return f"O Oráculo encontrou um problema com a API OpenAI: {e.status_code}. Verifique sua chave e os limites de uso."
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado com OpenAI: {e}")
        st.exception(e)
        return "O Oráculo não conseguiu se comunicar com OpenAI. Tente novamente mais tarde."

def analyze_with_gemini(prompt: str, api_key: str, image: Image.Image = None) -> str:
    """
    Envia o prompt (e opcionalmente uma imagem) para a API Gemini e retorna a resposta.
    Utiliza modelos de visão se uma imagem for fornecida.
    """
    if not api_key:
        return "Erro: Chave da API Gemini não fornecida."

    try:
        genai.configure(api_key=api_key)
        
        if image:
            # Tenta usar o modelo de visão armazenado na session_state ou o flash mais recente
            model_name = st.session_state.get("gemini_vision_model", 'gemini-1.5-flash-latest')
            model = genai.GenerativeModel(model_name) 
            response = model.generate_content([prompt, image])
        else:
            # Tenta usar o modelo de texto armazenado na session_state ou o pro
            model_name = st.session_state.get("gemini_text_model", 'gemini-pro')
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
        return response.text
    except exceptions.NotFound as e: # Captura o erro específico de modelo não encontrado
        st.error(f"Erro: O modelo Gemini '{e.message}' não foi encontrado. Por favor, valide sua chave API na barra lateral e verifique os modelos disponíveis para sua região.")
        st.exception(e)
        return "O Oráculo não conseguiu acessar o modelo Gemini. Verifique sua chave API e os modelos disponíveis."
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado com Gemini: {e}")
        st.exception(e)
        return "O Oráculo não conseguiu se comunicar com Gemini. Tente novamente mais tarde. Verifique sua chave da API."

# --- Funções de Extração de Conteúdo ---

def analyze_image_content(image: Image.Image, provider: str, api_key: str) -> str:
    """Realiza a análise de uma imagem usando o provedor escolhido."""
    prompt = "Analise a fachada presente na imagem. Descreva os elementos relacionados à marca Brahma, como logotipos, cores, materiais, e qualquer inconsistência ou oportunidade de melhoria. Seja conciso e direto."
    if provider == "OpenAI":
        return analyze_with_openai(prompt, api_key, image=image)
    return analyze_with_gemini(prompt, api_key, image=image)

def extract_images_from_pptx(file_bytes: BytesIO) -> list[Image.Image]:
    """Extrai e retorna todas as imagens de um arquivo PPTX."""
    pres = Presentation(file_bytes)
    images: list[Image.Image] = []
    for slide in pres.slides:
        for shape in slide.shapes:
            if hasattr(shape, "image"):
                try:
                    img_io = BytesIO(shape.image.blob)
                    img = Image.open(img_io)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    images.append(img)
                except UnidentifiedImageError:
                    st.warning(f"Um arquivo dentro do PPTX ({shape.name}) não pôde ser identificado como imagem. Pulando.")
                except Exception as e:
                    st.warning(f"Erro ao extrair imagem ({shape.name}) do PPTX: {e}. Pulando.")
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
            st.error("Por favor, **informe a API Key** na barra lateral para iniciar a análise.")
            return

        if not user_input_text and not uploaded_file:
            st.warning("Por favor, digite uma pergunta ou envie um arquivo para analisar.")
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