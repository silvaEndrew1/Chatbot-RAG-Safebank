import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
 
 
def config_rag_chain(llm, retriever):
    """Monta a chain completa da RAG com histórico de conversa."""
 
    # Prompt de contextualização: reformula a pergunta levando em conta o histórico,
    # para que ela faça sentido de forma independente
    context_q_system_prompt = """Given the following chat history and the follow-up question 
    which might reference context in the chat history, formulate a standalone question which 
    can be understood without the chat history. Do NOT answer the question, just reformulate 
    it if needed and otherwise return it as is."""
 
    context_q_user_prompt = "Question: {input}"
 
    context_q_prompt = ChatPromptTemplate.from_messages([
        ("system", context_q_system_prompt),
        MessagesPlaceholder("chat_history"),  # Injeta o histórico da conversa
        ("human", context_q_user_prompt),
    ])
 
    # Chain que usa o histórico para recuperar documentos relevantes
    history_aware_retriever = create_history_aware_retriever(
        llm=llm, retriever=retriever, prompt=context_q_prompt
    )
 
    # Prompt principal: instrui o assistente a responder com base no contexto recuperado
    system_prompt = """Você é um assistente virtual prestativo e está respondendo perguntas gerais sobre os serviços de uma empresa.
    Use os seguintes pedaços de contexto recuperado para responder à pergunta.
    Se você não sabe a resposta, apenas comente que não sabe dizer com certeza.
    Mas caso seja uma dúvida muito comum, pode sugerir como alternativa uma solução possível.
    Mantenha a resposta concisa.
    Responda em português. \n\n"""
 
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),  # Injeta o histórico da conversa
        ("human", "Pergunta: {input}\n\n Contexto: {context}"),
    ])
 
    # Chain que combina os documentos recuperados e gera a resposta final
    qa_chain = create_stuff_documents_chain(llm, qa_prompt)
 
    # Chain completa da RAG: recuperação com histórico + geração de resposta
    rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)
 
    return rag_chain
 
 
def chat_llm(rag_chain, input):
    """Envia a mensagem do usuário para a RAG chain e retorna a resposta."""
 
    # Adiciona a mensagem do usuário ao histórico
    st.session_state.chat_history.append(HumanMessage(content=input))
 
    # Invoca a chain com a pergunta e o histórico atual
    response = rag_chain.invoke({
        "input": input,
        "chat_history": st.session_state.chat_history
    })
 
    # Extrai a resposta e remove bloco de "pensamento interno" do modelo, se existir
    res = response["answer"]
    res = res.split("</think>")[-1].strip() if "</think>" in res else res.strip()
 
    # Adiciona a resposta do assistente ao histórico
    st.session_state.chat_history.append(AIMessage(content=res))
 
    return res