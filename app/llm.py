### Carregamento do modelo LLM

from langchain_groq import ChatGroq
 
 
def load_llm(id_model, temperature):
    """Inicializa e retorna o modelo de linguagem (LLM) via Groq."""
    llm = ChatGroq(
        model=id_model,           # ID do modelo a ser usado
        temperature=temperature,  # Nível de criatividade das respostas
        max_tokens=None,          # Sem limite de tokens na resposta
        timeout=None,             # Sem tempo limite de espera
        max_retries=2,            # Tenta novamente até 2x em caso de falha
    )
    return llm