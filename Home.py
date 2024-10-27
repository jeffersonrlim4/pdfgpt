import streamlit as st
from time import sleep
from utils import criar_chain_conversa, PASTA_ARQUIVOS

# def cria_chain_conversa():
#     st.session_state['chain'] = True
    
#     memory = ConversationBufferMemory(return_messages=True)
    
#     memory.chat_memory.add_user_message('Oi')
#     memory.chat_memory.add_ai_message('Oi me chamo PDFnaldo, estou aqui pra te ajudar com seus arquivos PDFs')
    
#     st.session_state['memory'] = memory
#     pass

def sidebar():
    uploaded_pdfs = st.file_uploader('Adicione seus arquivos pdf', type=['.pdf'], accept_multiple_files=True)
    if uploaded_pdfs:
        for file in PASTA_ARQUIVOS.glob('*.pdf'):
            file.unlink()
        for pdf in uploaded_pdfs:
            with open(PASTA_ARQUIVOS / pdf.name, 'wb') as f:
                f.write(pdf.read())
                
    label_botao = 'Inicializar ChatBot'
    if 'chain' in st.session_state:
        label_botao = 'Atualizar ChatBot'
    if st.button(label_botao, use_container_width=True):
        if len(list(PASTA_ARQUIVOS.glob('*pdf'))) == 0:
            st.error('Adicione arquivos .pdf para inicializar o chatbot')
        else:
            st.success('Inicializando ChaBot...')
            sleep(3)
            criar_chain_conversa()
            st.rerun()

def chat_window():
    st.header('Bem vindo ao PDFgpt', divider=True)
    if not 'chain' in st.session_state:
        st.error('Faça o upload de um arquivo PDF para começar')
        st.stop()
        
    chain = st.session_state['chain']
    memory = chain.memory
    
    mensagens = memory.load_memory_variables({})['chat_history']
    
    container = st.container()
    for mensagem in mensagens:
        chat = container.chat_message(mensagem.type)
        chat.markdown(mensagem.content)
        
    nova_mensagem = st.chat_input('Converse com seus documentos')
    if nova_mensagem:
        chat = container.chat_message('human')
        chat.markdown(nova_mensagem)
        chat = container.chat_message('ai')
        chat.markdown('Gerando resposta')
        
        resposta = chain.invoke({'question': nova_mensagem})
        st.session_state['ultima_resposta'] = resposta
        
        # sleep(2)
        
        # memory.chat_memory.add_user_message(nova_mensagem)
        # memory.chat_memory.add_ai_message('Macacos me mordam')
        st.rerun()
        

def main():
    with st.sidebar:
        sidebar()
    chat_window()

if __name__ == '__main__':
    main()