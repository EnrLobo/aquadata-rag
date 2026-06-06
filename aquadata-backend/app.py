import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import chromadb
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (.env local ou configuradas no Render)
load_dotenv()

app = Flask(__name__)
# Configuração de CORS flexível para aceitar as requisições do frontend publicado
CORS(app, resources={r"/*": {"origins": "*"}})

chave_api = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")

# Configura o caminho do banco vetorial de forma segura para o servidor de hospedagem
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_data")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="recordes_natacao")

def obter_embedding_pergunta(texto):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-embedding-001:embedContent?key={chave_api}"
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": texto}]}
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_json = response.json()
        if 'embedding' in response_json:
            return response_json['embedding']['values']
        return None
    except Exception as e:
        print(f"Erro no embedding: {str(e)}")
        return None

def buscar_contexto_vetorial(pergunta):
    vetor_pergunta = obter_embedding_pergunta(pergunta)
    if not vetor_pergunta:
        return "Nenhum dado vetorial correspondente encontrado."
    try:
        resultados = collection.query(
            query_embeddings=[vetor_pergunta],
            n_results=3
        )
        if resultados and resultados['documents'] and len(resultados['documents'][0]) > 0:
            return "\n".join(resultados['documents'][0])
    except Exception as e:
        print(f"Erro no ChromaDB: {str(e)}")
    return "Nenhum dado vetorial correspondente encontrado."

@app.route("/chat", methods=["POST"])
def chat():
    dados = request.get_json()
    pergunta_usuario = dados.get("mensagem", "")
    
    if not pergunta_usuario:
        return jsonify({"erro": "A mensagem não pode estar vazia"}), 400
        
    contexto_tcc = buscar_contexto_vetorial(pergunta_usuario)
    
    prompt_sistema = f"""
    Você é o AquaData ChatBot, um assistente inteligente baseado em RAG especialista em desempenho e recordes mundiais de natação, baseado no TCC dos alunos Enrique Rocha e João Henrique do IFSULDEMINAS Campus Machado.
    
    Instruções de resposta:
    1. Use estritamente o contexto recuperado por embeddings fornecido abaixo para responder de forma clara, direta e humanizada à pergunta.
    2. Sempre que perguntarem de um recorde, traga obrigatoriamente: o Tempo, Quando foi feito (Data), Onde/Qual Competição, quem é o Atleta e o País dele.
    3. Se a informação não estiver clara no contexto, use seu conhecimento de natação para responder de forma correta e profissional.

    CONTEXTO RECUPERADO POR EMBEDDINGS DO BANCO VETORIAL:
    {contexto_tcc}

    Pergunta do Usuário: {pergunta_usuario}
    Resposta (Seja direto, claro e formate dados importantes em negrito):
    """
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={chave_api}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt_sistema}]}]}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_json = response.json()
        resposta_final = response_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        resposta_final = f"Erro na geração da resposta: {str(e)}"
        
    return jsonify({"mensagem": resposta_final})

if __name__ == "__main__":
    # ALTERAÇÃO CRUCIAL PARA DEPLOY: Lê a porta do servidor de hospedagem ou usa a 5000 por padrão
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)