# Conceitos do Projeto — Chatbot com RAG

## RAG (Retrieval-Augmented Generation)

Técnica central do sistema. Em vez de o LLM responder apenas com o que aprendeu no treinamento, ele primeiro **busca informações relevantes nos PDFs** e usa esse contexto para gerar a resposta.

**Fluxo:** usuário pergunta → sistema busca nos PDFs → LLM responde com base no que encontrou.

---

## Embeddings

Representações numéricas (vetores) do texto. Textos com significado parecido geram vetores parecidos, permitindo busca por **semelhança semântica** e não apenas por palavras-chave.

**No projeto:** o modelo `neuralmind/bert-base-portuguese-cased` transforma os chunks dos PDFs em vetores numéricos.

> ⚠️ **Primeira execução:** o modelo de embeddings é baixado do HuggingFace automaticamente e pode ter centenas de MB. Por isso, o primeiro carregamento é mais demorado — isso é normal. Das execuções seguintes em diante, o modelo já estará em cache local e o índice FAISS estará salvo em disco, tornando o carregamento muito mais rápido.

**Modelos disponíveis e suas características:**

| Modelo | Tamanho | Qualidade em PT |
|---|---|---|
| `BAAI/bge-m3` | ~2GB | Excelente |
| `neuralmind/bert-base-portuguese-cased` | ~440MB | Boa |
| `sentence-transformers/all-mpnet-base-v2` | ~420MB | Razoável (foco em inglês) |
| `sentence-transformers/all-MiniLM-L6-v2` | ~90MB | Fraca |

> 💡 **Atenção ao trocar de modelo:** se o índice FAISS já foi gerado com um modelo, delete a pasta `index_faiss/` antes de trocar — os vetores são incompatíveis entre modelos diferentes.

---

## FAISS (Vector Store)

Banco de dados que armazena os vetores (embeddings). Quando o usuário faz uma pergunta, ela também vira um vetor e o FAISS encontra os chunks mais similares.

**No projeto:** `FAISS.from_texts(chunks, embedding=embeddings)`

---

## Chunks

Pedaços menores em que os textos dos PDFs são divididos para facilitar a recuperação. Cada chunk tem um tamanho máximo e uma sobreposição com o chunk anterior para não perder contexto.

**No projeto:** `chunk_size=1000` e `chunk_overlap=200`

---

## Retriever

Interface que faz a busca no FAISS. Recebe a pergunta e retorna os chunks mais relevantes.

**No projeto:** usa busca **MMR** (Maximum Marginal Relevance), que evita retornar chunks repetidos — traz diversidade nos resultados.

---

## Chain

Sequência de etapas encadeadas onde a saída de uma alimenta a entrada da próxima.

**No projeto existem duas chains:**
- `history_aware_retriever` — reformula a pergunta considerando o histórico, depois busca no FAISS
- `qa_chain` — recebe os chunks recuperados e gera a resposta final

A `rag_chain` junta as duas em sequência.

---

## Session State

Específico do Streamlit. Como o Streamlit reexecuta o script inteiro a cada interação, o `st.session_state` guarda dados entre as execuções — no caso, o histórico do chat e o retriever já configurado.

---

## Groq e LLM

O **Groq** é uma empresa que criou um hardware especializado para rodar modelos de IA — o **LPU (Language Processing Unit)**, um chip projetado especificamente para inferência de LLMs, muito mais rápido que GPUs convencionais para essa tarefa.

É importante separar dois conceitos:

| | O que é |
|---|---|
| **Groq** | A infraestrutura — o hardware e a API |
| **LLaMA, Gemma, Mixtral...** | Os modelos que rodam nessa infraestrutura |

O LLaMA foi criado pela **Meta** — o Groq apenas hospeda e serve o modelo via API com alta velocidade.

**No projeto:**
```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # modelo da Meta rodando na infraestrutura Groq
    temperature=0.7,
)
```

O fluxo de uma requisição é:
```
seu código → API Groq → LPU processa o LLaMA → resposta retorna
```

A chave `GROQ_API_KEY` no arquivo `.env` autentica suas requisições para a API.

**Por que usar Groq?**
- **Gratuito** para uso moderado — ideal para estudos e projetos
- **Muito rápido** — respostas em segundos mesmo com modelos grandes como o LLaMA 70B
- **Sem instalação** — o modelo roda na nuvem deles, não na sua máquina

---

## Fluxo Completo do Sistema

```
PDF → chunks → embeddings → FAISS
                                ↓
usuário pergunta → retriever busca chunks relevantes
                                ↓
            LLM recebe pergunta + chunks + histórico
                                ↓
                        resposta gerada
```

---


## Tecnologias do Projeto

### Streamlit
Framework Python para criação de interfaces web de forma simples, sem necessidade de conhecimento em HTML ou CSS. Cada interação do usuário reexecuta o script inteiro — por isso o `st.session_state` é essencial para guardar dados entre execuções.

**No projeto:** toda a interface do chat — botão de início, spinner de carregamento, histórico de mensagens e campo de input — é construída com Streamlit.

---

### LangChain
Framework que facilita a construção de aplicações com LLMs. Fornece componentes prontos para carregar documentos, dividir textos, criar prompts, montar chains e integrar com diversas ferramentas e modelos.

**No projeto:** usado para montar toda a pipeline RAG — desde o carregamento dos PDFs até a chain final que combina recuperação e geração de resposta.

```
LangChain orquestra: PDFs → chunks → embeddings → FAISS → retriever → LLM → resposta
```

---

### Groq
Empresa que criou o **LPU (Language Processing Unit)** — hardware especializado para inferência de LLMs, muito mais rápido que GPUs convencionais. Oferece acesso via API a modelos como LLaMA, Gemma e Mixtral.

**No projeto:** serve o modelo LLaMA 3.3 70B via API, gerando as respostas do chatbot na nuvem — sem necessidade de GPU local.

> 💡 Gratuito para uso moderado, ideal para estudos e projetos.

---

### FAISS (Facebook AI Similarity Search)
Biblioteca criada pelo time de pesquisa da Meta para busca eficiente de vetores por similaridade. Armazena os embeddings dos chunks e encontra rapidamente os mais relevantes para cada pergunta.

**No projeto:** armazena os vetores dos PDFs localmente na pasta `index_faiss/`. Na primeira execução cria e salva o índice — nas seguintes carrega direto do disco.

```python
# Criando o índice
FAISS.from_texts(chunks, embedding=embeddings)

# Carregando do disco
FAISS.load_local("index_faiss", embeddings, allow_dangerous_deserialization=True)
```

---

### HuggingFace
Plataforma open source com um repositório gigante de modelos de IA. Qualquer pessoa ou organização pode publicar modelos lá. O caminho do modelo no código é exatamente o endereço na plataforma:

```python
"neuralmind/bert-base-portuguese-cased"
#  ↑ organização    ↑ nome do modelo
```

**No projeto:** fornece o modelo de embeddings `neuralmind/bert-base-portuguese-cased`, baixado automaticamente na primeira execução e armazenado em cache local.

> 💡 Para encontrar o melhor modelo de embeddings para seu caso, consulte o ranking **MTEB Leaderboard** em `huggingface.co/spaces/mteb/leaderboard`.
