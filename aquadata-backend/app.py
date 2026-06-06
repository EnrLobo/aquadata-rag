import os
import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (.env)
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

chave_api = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")

# ==========================================
# CARREGAMENTO DA BASE DE DADOS (CSV NATIVO)
# ==========================================
nome_arquivo_csv = 'Recordes_Formatados_RAG.xlsx - Recordes_Formatados_RAG.csv.csv'
dataset_recordes = []

try:
    if os.path.exists(nome_arquivo_csv):
        with open(nome_arquivo_csv, mode='r', encoding='utf-8') as arquivo:
            # Lê o CSV tratando a primeira linha como cabeçalho
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                dataset_recordes.append(linha)
        print(f"Dataset carregado com sucesso! {len(dataset_recordes)} registros encontrados.")
    else:
        print("Aviso: Arquivo CSV formatado não encontrado na pasta.")
except Exception as e:
    print(f"Erro ao carregar a base de dados via CSV: {str(e)}")

# ==========================================
# RETRIEVAL (BUSCA DE CONTEXTO SEM PANDAS)
# ==========================================
def buscar_contexto_rag(pergunta):
    global dataset_recordes
    if not dataset_recordes:
        return "Nenhum dado disponível no momento."
        
    pergunta_limpa = pergunta.lower()
    palavras_chave = pergunta_limpa.split()
    
    # Filtra palavras comuns para focar nos termos de busca importantes
    ignorar = ["o", "a", "os", "as", "do", "da", "dos", "das", "de", "quem", "é", "recorde", "mundial", "feminino", "masculino", "qual"]
    filtradas = [p for p in palavras_chave if p not in ignorar and len(p) > 1]
    
    contextos_encontrados = []
    
    # Busca estrita: todas as palavras filtradas devem estar na linha
    for linha in dataset_recordes:
        conteudo_linha = str(linha.get('Conteúdo', '')).lower()
        if filtradas and all(palavra in conteudo_linha for palavra in filtradas):
            contextos_encontrados.append(str(linha.get('Conteúdo', '')))
            
    if contextos_encontrados:
        return "\n".join(contextos_encontrados[:3])
        
    # Busca por aproximação secundária
    for linha in dataset_recordes:
        conteudo_linha = str(linha.get('Conteúdo', '')).lower()
        if any(palavra in conteudo_linha for palavra in palavras_chave if len(palavra) > 3):
            contextos_encontrados.append(str(linha.get('Conteúdo', '')))
            
    if contextos_encontrados:
        return "\n".join(contextos_encontrados[:3])
        
    return "Nenhum registro correspondente exato encontrado na planilha de recordes."

# ==========================================
# ROTA DO CHAT
# ==========================================
@app.route("/chat", methods=["POST"])
def chat():
    dados = request.get_json()
    pergunta_usuario = dados.get("mensagem", "")
    
    if not pergunta_usuario:
        return jsonify({"erro": "A mensagem não pode estar vazia"}), 400
        
    # Recupera o contexto do nosso buscador leve
    contexto_tcc = buscar_contexto_rag(pergunta_usuario)
    
    prompt_sistema = f"""
    Você é o AquaData ChatBot, um assistente inteligente especialista em desempenho e recordes mundiais de natação, baseado no TCC dos alunos Enrique Rocha e João Henrique do IFSULDEMINAS Campus Machado.
    
    Instruções de resposta:
    1. Use o contexto fornecido abaixo para responder de forma clara, direta e humanizada à pergunta do usuário.
    2. Sempre que perguntarem de um recorde, traga obrigatoriamente: o Tempo, Quando foi feito (Data), Onde/Qual Competição, quem é o Atleta e o País dele.
    3. Se a resposta exata não puder ser encontrada no contexto, use o seu conhecimento geral sobre natação para responder perfeitamente.

    CONTEXTO RECUPERADO DO DATASET:
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
        resposta_final = f"Erro na geração da resposta pela IA: {str(e)}"
        
    return jsonify({"mensagem": resposta_final})

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)