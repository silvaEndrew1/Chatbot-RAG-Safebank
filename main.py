import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
from app.llm import load_llm
from app.retriever import config_retriever
from app.rag_chain import config_rag_chain, chat_llm
 
# Carrega as variáveis de ambiente do arquivo .env (ex: chave da API Groq)
load_dotenv()
 
# Configuração da página do Streamlit
st.set_page_config(page_title="Atendimento SafeBank 🤖", page_icon="🤖")
st.title("Atendimento SafeBank")
 
# Configurações do modelo e do caminho dos documentos PDF
id_model = "llama-3.3-70b-versatile"  # Modelo LLaMA via Groq
temperature = 0.7                      # Criatividade das respostas (0 = preciso, 1 = criativo)
path = "content"                       # Pasta onde os PDFs serão carregados
 
# Carrega o LLM com as configurações definidas
llm = load_llm(id_model, temperature)
 
# Controla se o atendimento já foi iniciado pelo usuário
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
 
# Inicializa o retriever como None (será configurado ao clicar no botão)
if "retriever" not in st.session_state:
    st.session_state.retriever = None
 
# Exibe o botão de início enquanto o chat não foi iniciado
if not st.session_state.chat_started:
    st.markdown("Clique abaixo para iniciar o atendimento:")
    if st.button("Iniciar atendimento"):
        with st.spinner("Aguarde enquanto te transferimos para um atendente..."):
            st.session_state.retriever = config_retriever(path)
            st.session_state.chat_started = True
            st.rerun()  # Força reexecução para exibir o chat
    st.stop()  # Impede que o restante do código seja executado antes do clique
 
# Inicializa o histórico do chat com a mensagem de boas-vindas
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Olá, sou o seu assistente virtual! Como posso te ajudar?"),
    ]
 
# Campo de entrada de texto do chat
input = st.chat_input("Digite sua mensagem aqui...")
 
# Exibe todo o histórico de mensagens na interface
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

 
# Processa a nova mensagem quando o usuário envia algo
if input is not None:

    # Exibe a mensagem do usuário no chat
    with st.chat_message("Human"):
        st.markdown(input)

    # Exibe a resposta do assistente no chat
    with st.chat_message("AI"):

        # Monta a chain RAG com o LLM e o retriever já configurado
        rag_chain = config_rag_chain(llm, st.session_state.retriever)

        # Exibe spinner enquanto o LLM processa e gera a resposta
        with st.spinner("Aguarde..."):
            res = chat_llm(rag_chain, input)

        # Exibe a resposta gerada na interface
        st.write(res)