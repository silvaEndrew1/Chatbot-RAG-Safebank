# Atendimento SafeBank — Chatbot com RAG

Chatbot de atendimento com recuperação de documentos (RAG) usando LangChain, Groq e Streamlit.

## Como rodar

1. Clone o repositório
2. Crie e ative a venv:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
   > Desenvolvido com Python 3.11. Para reprodução exata do ambiente use: 
   > ```bash
   > pip install -r requirements-freeze.txt
   > ```

4. Crie o arquivo `.env` com sua chave Groq:
   ```
   GROQ_API_KEY=sua_chave_aqui
   ```
5. Adicione PDFs na pasta `content/`
6. Execute:
   ```bash
   streamlit run main.py
   ```

## Estrutura do projeto

```
├── app/
│   ├── __init__.py
│   ├── llm.py               # Carregamento do modelo LLM
│   ├── retriever.py         # Extração de PDF, chunks e indexação FAISS
│   └── rag_chain.py         # Chain RAG e interação com o chat
├── content/                 # PDFs da base de conhecimento (não versionado)
├── index_faiss/             # Índice vetorial gerado (não versionado)
├── docs/
│   ├── conceitos.md         # Explicação dos conceitos do projeto
│   └── cenario.md           # Contexto e justificativa do projeto
├── main.py                  # Interface Streamlit e fluxo principal
├── requirements.txt         # Dependências diretas
├── requirements-freeze.txt  # Versões exatas de todas as dependências
├── .env                     # Chave da API (não versionado)
└── .gitignore
```

## Tecnologias

- [Streamlit](https://streamlit.io/) — Interface web
- [LangChain](https://langchain.com/) — Framework para LLMs
- [Groq](https://groq.com/) — API do modelo LLaMA (Meta), rodando em LPU
- [FAISS](https://faiss.ai/) — Banco vetorial local
- [HuggingFace](https://huggingface.co/) — Modelo de embeddings em português
