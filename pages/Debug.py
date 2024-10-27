import streamlit as st
from configs import get_config
from langchain.prompts import PromptTemplate

def debug_page():
    st.header('Debug', divider=True)
    prompt_template = get_config('prompt')
    prompt_template = PromptTemplate.from_template(prompt_template)
    
    if not 'ultima_resposta' in st.session_state:
        st.error('Faça uma pergunta no chat para visualizar o debug')
        st.stop()
        
    ultima_reposta = st.session_state['ultima_resposta']
    
    contexto_docs = ultima_reposta['source_documents']
    contexto_list = [doc.page_content for doc in contexto_docs]
    contexto_str = '\n\n'.join(contexto_list)
    
    chain = st.session_state['chain']
    memory = chain.memory
    chat_history = memory.buffer_as_str
    
    with st.container(border=True):
        prompt = prompt_template.format(
            chat_history=chat_history,
            context=contexto_str,
            question=''
        )
        st.code(prompt)

    
debug_page()