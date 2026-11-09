# Assistente de marca com RAG

Chatbot em Streamlit que responde perguntas sobre as diretrizes de uma marca e analisa imagens de peças criativas com base nessas diretrizes.

## Funcionalidades

- **Perguntas sobre a marca**: o guia da marca é dividido em trechos, indexado num banco vetorial, e o chatbot responde usando esses trechos como contexto. A conversa tem memória.
- **Análise de imagem**: o usuário envia uma peça e faz uma pergunta. O Gemini descreve a imagem, essa descrição é combinada com a pergunta, e o sistema consulta as diretrizes para avaliar se a peça está de acordo.
- **Novos documentos**: dá para enviar outro arquivo e indexá-lo na base.

## Como funciona

- Embeddings: `paraphrase-multilingual-MiniLM-L12-v2` (Hugging Face), que funciona bem em português
- Banco vetorial: Astra DB, com Chroma local como alternativa se o Astra não estiver disponível
- LLM: Gemini, via LangChain (`ConversationalRetrievalChain`)

## Como rodar

Crie `.streamlit/secrets.toml` com:

```toml
GOOGLE_API_KEY = ""
ASTRA_DB_API_ENDPOINT = ""
ASTRA_DB_APPLICATION_TOKEN = ""
```

```bash
pip install -r requirements.txt
streamlit run Menu.py
```
