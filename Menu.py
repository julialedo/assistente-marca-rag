import streamlit as st


st.title(" Agente Coca Cola")
st.write(
    "Sistema inteligente de gestão de conteúdo"
)
st.divider()
coluna1, coluna2 = st.columns(2)

with coluna1:
    with st.container(border=True):
        st.markdown("**Chatbot Agente Coca Cola**")
        st.write("Assistente virtual para diretrizes da marca:")
        if st.button("Acessar Chatbot", key="chatbot_btn", use_container_width=True):
            st.switch_page("pages/Faça_perguntas.py")

    with st.container(border=True):
        st.markdown("**Aprovação de Conteúdo**")
        st.write("Analise e aprove conteúdos")
        if st.button("Acessar Chatbot para análise de imagem", key="chatbot_imagem_btn", use_container_width=True):
            st.switch_page("pages/Analise_a_imagem.py")

with coluna2:
    with st.container(border=True):
        st.markdown("**Geração de Conteúdo**")
        st.write("Crie conteúdos alinhados")
        
    with st.container(border=True):
        st.markdown("**Briefings Coca Cola**")
        st.write("Crie briefings completos")


