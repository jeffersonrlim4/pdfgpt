from pathlib import Path
from  langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_community.vectorstores.faiss import FAISS
from langchain.prompts import PromptTemplate
from configs import *
import streamlit as st

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

PASTA_ARQUIVOS = Path(__file__).parent / 'files'


def importacao_documentos():
    documentos = []
    for arquivo in PASTA_ARQUIVOS.glob('*pdf'):
        loader = PyPDFLoader(str(arquivo))
        documentos_arquivo = loader.load()
        documentos.extend(documentos_arquivo)
    return documentos

def split_de_documentos(documentos):
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=250,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    documentos = recursive_splitter.split_documents(documentos)
    
    for i, doc in enumerate(documentos):
        doc.metadata['source'] = doc.metadata['source'].split('/')[-1]
        doc.metadata['doc_id'] = i
        
    return documentos

def criar_vector_store(documentos):
    embedding_model = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(
        documents=documentos,
        embedding=embedding_model
    )
    return vector_store

def criar_chain_conversa():
    
    documentos = importacao_documentos()
    documentos_split = split_de_documentos(documentos)
    vector_store = criar_vector_store(documentos_split)
    
    chat = ChatOpenAI(model=get_config('model_name'))
    memory = ConversationBufferMemory(return_messages=True, memory_key='chat_history', output_key='answer')
    retriever = vector_store.as_retriever(
        search_type=get_config('retrieval_search_type'),
        search_kwargs=get_config('retrieval_kwargs')
    )
    prompt_template = PromptTemplate.from_template(get_config('prompt'))
    chat_chain = ConversationalRetrievalChain.from_llm(
        llm=chat,
        memory=memory,
        retriever=retriever,
        return_source_documents=True,
        verbose=True,
        combine_docs_chain_kwargs={'prompt': prompt_template}
    )
    
    st.session_state['chain'] = chat_chain

# if __name__ == '__main__':
#     documentos = importacao_documentos()
#     documentos_split = split_de_documentos(documentos)
#     vector_store = criar_vector_store(documentos_split)
#     chain = criar_chain_conversa(vector_store)