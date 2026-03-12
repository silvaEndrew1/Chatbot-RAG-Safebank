import streamlit as st
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
 
 
def extract_text_pdf(file_path):
    """Carrega um PDF e extrai todo o seu conteúdo como texto."""
    loader = PyMuPDFLoader(file_path)              # Inicializa o leitor de PDF
    doc = loader.load()                            # Carrega todas as páginas do documento
    content = "\n".join([page.page_content for page in doc])  # Junta o conteúdo de todas as páginas
    return content
 
 
def config_retriever(folder_path="content"):
    """
    Configura o retriever: carrega PDFs, divide em chunks e indexa no FAISS.
    Fluxo: PDF -> Texto -> Chunks -> Embeddings -> FAISS -> Retriever
    """
    # Busca todos os arquivos PDF na pasta indicada
    docs_path = Path(folder_path)
    pdf_files = [f for f in docs_path.glob("*.pdf")]
 
    # Encerra a aplicação se nenhum PDF for encontrado
    if len(pdf_files) < 1:
        st.error("Nenhum arquivo PDF carregado")
        st.stop()
 
    # Extrai o texto de cada PDF encontrado
    loaded_documents = [extract_text_pdf(pdf) for pdf in pdf_files]
 
    # Divide os textos em chunks menores para melhor recuperação
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,    # Tamanho máximo de cada chunk em caracteres
        chunk_overlap=200   # Sobreposição entre chunks para não perder contexto
    )
 
    # Gera os chunks a partir de todos os documentos carregados
    chunks = []
    for doc in loaded_documents:
        chunks.extend(text_splitter.split_text(doc))
 
    # Define e inicializa o modelo de embeddings para vetorização dos chunks
    #embedding_model = "BAAI/bge-m3"  
    embedding_model = "neuralmind/bert-base-portuguese-cased"
    
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
 
    # Carrega índice FAISS salvo se já existir, senão cria e salva um novo
    if Path("index_faiss").exists():
        vectorstore = FAISS.load_local("index_faiss", embeddings, allow_dangerous_deserialization=True)
    else:
        vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
        vectorstore.save_local("index_faiss")
 
    # Configura o retriever com busca MMR (evita resultados repetidos)
    retriever = vectorstore.as_retriever(
        search_type='mmr',       # MMR = Maximum Marginal Relevance
        search_kwargs={
            'k': 3,              # Número de chunks retornados ao LLM
            'fetch_k': 4         # Número de candidatos analisados antes de selecionar os k
        }
    )
 
    return retriever