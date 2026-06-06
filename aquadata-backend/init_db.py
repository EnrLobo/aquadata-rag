import os
import time
import pandas as pd
import chromadb
import requests
from dotenv import load_dotenv

load_dotenv()

chave_api = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
if not chave_api:
    raise ValueError("Chave API do Gemini não encontrada no arquivo .env")

# 1. Configurar o banco de dados vetorial ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="recordes_natacao")

# 2. Função corrigida com o modelo oficial estável
def obtener_embedding_texto(texto):
    # Usando o modelo clássico do roteiro do professor para garantir compatibilidade total
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-embedding-001:embedContent?key={chave_api}"
    
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {
            "parts": [{"text": texto}]
        }
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_json = response.json()
        
        if 'embedding' in response_json:
            return response_json['embedding']['values']
        else:
            print(f"Erro na resposta do Google: {response_json}")
            return None
    except Exception as e:
        print(f"Erro de conexão para o texto: {texto[:20]}... Erro: {str(e)}")
        return None

# 3. Carregar o arquivo formatado
nome_arquivo_csv = 'DB-WorldRecordsRAG.csv'
nome_arquivo_xlsx = 'Recordes_Formatados_RAG.xlsx'

df = None
if os.path.exists(nome_arquivo_csv):
    df = pd.read_csv(nome_arquivo_csv, encoding='utf-8')
    print("Planilha formatada (.csv) carregada com sucesso!")
elif os.path.exists(nome_arquivo_xlsx):
    df = pd.read_excel(nome_arquivo_xlsx)
    print("Planilha formatada (.xlsx) carregada com sucesso!")
else:
    print("ERRO: Nenhum arquivo encontrado.")
    exit()

documentos = []
embeddings = []
metadados = []
ids = []

print("\nIniciando geração de Embeddings com proteção de tempo. Aguarde...")

for index, row in df.iterrows():
    try:
        texto_recorde = str(row['Conteúdo'])
        titulo_recorde = str(row['Titulo']) if 'Titulo' in df.columns else f"Recorde_{index}"
        
        # Gera o embedding
        vetor = obtener_embedding_texto(texto_recorde)
        
        if vetor:
            documentos.append(texto_recorde)
            embeddings.append(vetor)
            ids.append(f"id_recorde_{index}")
            metadados.append({"titulo": titulo_recorde})
            print(f"✅ [{index + 1}/{len(df)}] Sucesso: {titulo_recorde[:40]}...")
        else:
            print(f"❌ [{index + 1}/{len(df)}] Falhou ao gerar embedding.")
            
        # O PULO DO GATO: Espera 1.2 segundos antes de ir para a próxima linha
        # Isso impede o Google de bloquear sua chave por excesso de velocidade!
        time.sleep(1.2)
            
    except Exception as e_linha:
        print(f"Aviso: Erro na linha {index}: {str(e_linha)}")

# Salva tudo no banco vetorial
if documentos:
    collection.add(
        documents=documentos,
        embeddings=embeddings,
        metadatas=metadados,
        ids=ids
    )
    print(f"\n[SENSACIONAL!] {len(documentos)} recordes salvos com sucesso no ChromaDB!")
else:
    print("\nNenhum embedding pôde ser salvo.")