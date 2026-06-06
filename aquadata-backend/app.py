import os
import pandas as pd
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
# CARREGAMENTO DA BASE DE DADOS FORMATADA
# ==========================================
nome_arquivo_csv = 'Recordes_Formatados_RAG.xlsx - Recordes_Formatados_RAG.csv.csv'
nome_arquivo_xlsx = 'Recordes_Formatados_RAG.xlsx'
df = None

try:
    if os.path.exists(nome_arquivo_csv):
        df = pd.read_csv(nome_arquivo_csv, encoding='utf-8')
        print("Planilha formatada (.csv) carregada com sucesso!")
    elif os.path.exists(nome_arquivo_xlsx):
        df = pd.read_excel(nome_arquivo_xlsx)
        print("Planilha formatada (.xlsx) carregada com sucesso!")
except Exception as e:
    print(f"Aviso ao carregar planilha: {str(e)}")

# ==========================================
# RETRIEVAL (BUSCA DE CONTEXTO OTIMIZADA)
# ==========================================
def buscar_contexto_rag(pergunta):
    global df
    if df is None or df.empty:
        return "Nenhum dado disponível na planilha."
        
    pergunta_limpa = pergunta.lower()
    palavras_chave = pergunta_limpa.split()
    
    # Filtra palavras irrelevantes para focar no estilo/distância
    ignorar = ["o", "a", "os", "as", "do", "da", "dos", "das", "de", "quem", "é", "recorde", "mundial", "feminino", "masculino"]
    filtradas = [p for p in palavras_chave if p not in ignorar and len(p) > 1]
    
    contextos_encontrados = []
    
    for index, row in df.iterrows():
        conteudo_linha = str(row['Conteúdo']).lower()
        # Se as palavras chaves (ex: "50m", "livre") baterem com a linha do conteúdo, captura ela
        if filtradas and all(palavra in conteudo_linha for palabra in filtradas):
            contextos_encontrados.append(str(row['Conteúdo']))
            
    if contextos_encontrados:
        return "\n".join(contextos_encontrados[:3])
        
    # Busca por aproximação secundária caso a estrita falhe
    for index, row in df.iterrows():
        conteudo_linha = str(row['Conteúdo']).lower()
        if any(palavra in conteudo_linha for palavra in palavras_chave if len(palavra) > 3):
            contextos_encontrados.append(str(row['Conteúdo']))
            
    if contextos_encontrados:
        return "\n".join(contextos_encontrados[:3])
        
    return "Nenhum registro correspondente exato na planilha."

# ==========================================
# ROTA DO CHAT
# ==========================================
@app.route("/chat", methods=["POST"])
def chat():
    dados = request.get_json()
    pergunta_usuario = dados.get("mensagem", "")
    
    if not pergunta_usuario:
        return jsonify({"erro": "A mensagem não pode estar vazia"}), 400
        
    # Recupera o contexto estruturado da planilha formatada
    contexto_tcc = buscar_contexto_rag(pergunta_usuario)
    
    prompt_sistema = f"""
    Você é o AquaData ChatBot, um assistente inteligente especialista em desempenho e recordes mundiais de natação, baseado no TCC dos alunos Enrique Rocha e João Henrique do IFSULDEMINAS Campus Machado.
    
    Instruções de resposta:
    1. Use o contexto fornecido abaixo para responder de forma clara, direta e humanizada à pergunta do usuário.
    2. Sempre que perguntarem de um recorde, traga obrigatoriamente: o Tempo, Quando foi feito (Data), Onde/Qual Competição, quem é o Atleta e o País dele.
    3. Se a resposta exata não puder ser encontrada no contexto, use o seu conhecimento geral sobre natação para responder perfeitamente, mas cite os dados do contexto se houver aproximação.

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