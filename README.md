# mktia
# Oráculo de Fachadas Brahma

Este projeto demonstra uma aplicação simples em **Streamlit** para analisar
fachadas de bares da Brahma. É possível enviar imagens individuais, arquivos
`PPTX` ou `PDF`, além de textos. O código inclui exemplos de uso das APIs da
OpenAI ou Gemini (de forma ilustrativa) para indicar possíveis problemas na
fachada.

## Requisitos

- Python 3.10 ou superior
- `streamlit`, `python-pptx`, `Pillow`, `PyPDF2`, `openai` e
  `google-generativeai`

Instale tudo com:

```bash
pip install -r requirements.txt
```

## Execução

1. Coloque os arquivos que deseja analisar em um diretório.
2. Inicie a interface web:

```bash
streamlit run oracle.py
```

3. Informe sua chave de API (OpenAI ou Gemini) e envie o arquivo ou texto.

A barra lateral exibe imagens de exemplo em `examples/` para ilustrar uma
fachada correta e uma incorreta.

## Treinamento de modelo

Utilize suas referências para criar um conjunto de dados com fachadas corretas
e incorretas. Treine um modelo de classificação ou detecção (por exemplo com
PyTorch ou TensorFlow) e adapte as funções do código para enviar as imagens ao
modelo e retornar sugestões reais.

## Aviso

Este repositório é apenas um ponto de partida. Não há garantia de que a
analise produza resultados reais até que você integre seu próprio modelo.
Os arquivos nesta sessão são temporários, portanto mantenha cópias em local
seguro caso esteja treinando modelos personalizados.
