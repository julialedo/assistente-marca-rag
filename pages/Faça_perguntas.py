__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


ASTRA_METHOD = "unknown"

try:
    from langchain_astradb import AstraDBVectorStore
    ASTRA_METHOD = "modern"
except ImportError:
    try:
        from langchain_community.vectorstores import AstraDB
        ASTRA_METHOD = "community"
        st.info("Método community detectado")
    except ImportError:
        from langchain_community.vectorstores import Chroma
        ASTRA_METHOD = "chroma_local"
        st.warning("Usando fallback local")

st.set_page_config(
    page_title="Chatbot Coca-Cola", 
    page_icon="🥤", 
    layout="wide"
)

st.title("Chatbot Coca-Cola")
st.write(f"**Método de conexão:** {ASTRA_METHOD}")

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    ASTRA_DB_TOKEN = st.secrets["ASTRA_DB_APPLICATION_TOKEN"]
    ASTRA_DB_ENDPOINT = st.secrets["ASTRA_DB_API_ENDPOINT"]
    ASTRA_DB_KEYSPACE = st.secrets.get("ASTRA_DB_KEYSPACE", "default_keyspace")
except Exception as e:
    st.error(f"Erro nas chaves: {str(e)}")
    st.stop()

@st.cache_resource(show_spinner="Inicializando sistema...")
def configurar_sistema_rag():
    try:
        if not os.path.exists("dados_coca_cola.txt"):
            with open("dados_coca_cola.txt", "w", encoding="utf-8") as f:
                f.write("Informações sobre a Coca-Cola.\nA Coca-Cola foi inventada em 1886.")
            st.info("Arquivo de exemplo criado")

        loader = TextLoader("dados_coca_cola.txt", encoding="utf-8")
        documentos = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        pedacos = text_splitter.split_documents(documentos)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        vectorstore = None
        
        if ASTRA_METHOD == "modern":
            try:
                vectorstore = AstraDBVectorStore(
                    embedding=embeddings,
                    collection_name="coca_cola_chat",
                    api_endpoint=ASTRA_DB_ENDPOINT,
                    token=ASTRA_DB_TOKEN,
                    namespace=ASTRA_DB_KEYSPACE
                )
                st.success("Conectado via Data API")
            except Exception as e:
                st.error(f"Erro na conexão moderna: {str(e)}")
                return None
                
        elif ASTRA_METHOD == "community":
            try:
                vectorstore = AstraDB(
                    embedding=embeddings,
                    collection_name="coca_cola_chat", 
                    api_endpoint=ASTRA_DB_ENDPOINT,
                    token=ASTRA_DB_TOKEN
                )
            except Exception as e:
                st.error(f"Erro na conexão community: {str(e)}")
                return None
                
        else:  # chroma_local
            vectorstore = Chroma.from_documents(
                documents=pedacos,
                embedding=embeddings,
                persist_directory="./chroma_db"
            )
            st.info("Usando banco local")

        if ASTRA_METHOD != "chroma_local":
            try:
                vectorstore.add_documents(pedacos)
                st.success(f"{len(pedacos)} documentos adicionados")
            except Exception as e:
                st.warning(f"Erro ao adicionar documentos: {str(e)}")

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3
        )
        
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )

        return qa_chain

    except Exception as e:
        st.error(f"Erro crítico: {str(e)}")
        return None


qa_chain = configurar_sistema_rag()

if qa_chain:
    st.success("Sistema pronto para uso!")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Olá! Pergunte-me sobre a Coca-Cola!"
        }]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input do usuário
    if prompt := st.chat_input("Sua pergunta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    response = qa_chain.invoke({"question": prompt})
                    answer = response["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = f"Erro: {str(e)}"
                    st.error(error_msg)
else:
    st.error("Falha na inicialização do sistema")

with st.sidebar:
    st.header("Status do Sistema")
    st.info(f"""
    **Método:** {ASTRA_METHOD}
    **Status:** {'Conectado' if qa_chain else 'Erro'}
    **Endpoint:** {ASTRA_DB_ENDPOINT[:20]}...
    """)