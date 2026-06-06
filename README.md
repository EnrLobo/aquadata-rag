# 🏊‍♂️ AquaData ChatBot — Sistema RAG para Recordes Mundiais de Natação

O **AquaData ChatBot** é um assistente inteligente baseado em Inteligência Artificial e arquitetura **RAG (Retrieval-Augmented Generation)** focado no desempenho esportivo e histórico de recordes mundiais de natação. O projeto foi desenvolvido como Trabalho Prático para a disciplina de Inteligência Artificial do **IFSULDEMINAS Campus Machado**, estando diretamente integrado ao escopo do Trabalho de Conclusão de Curso (TCC) dos desenvolvedores.

A aplicação utiliza modelos de linguagem de última geração para fornecer respostas precisas, rápidas, humanizadas e totalmente livres de alucinações, consumindo dados estruturados diretamente de fontes oficiais do esporte.

---

## 🚀 Links da Aplicação no Ar

* **⚡ Frontend (Vercel):** [https://aquadata-rag.vercel.app/](https://aquadata-rag.vercel.app/)
* **⚙️ Backend API (Render):** [https://aquadata-backend.onrender.com](https://aquadata-backend.onrender.com)

---

## 👥 Desenvolvedores & Autores

O projeto foi planejado, estruturado e codificado em dupla por:

* **Enrique Rocha**
    * *GitHub:* [@EnrLobo](https://github.com/EnrLobo)
    * *Papel:* Desenvolvimento da arquitetura do backend Flask, engenharia de prompt, pipeline de ingestão de dados RAG e infraestrutura de deploy no Render.
* **João Henrique**
    * *GitHub:* [@kkjaokk](https://github.com/kkjaokk)
    * *Papel:* Desenvolvimento da interface responsiva em React, estilização temática aquática, integração de consumo de APIs e deploy na Vercel.

---

## 📊 Fontes de Dados & Dataset

O conjunto de dados (*Dataset*) que abastece o cérebro do ChatBot foi construído meticulosamente com mais de **70 registros detalhados** (superando o requisito mínimo de 30 linhas da atividade). Ele engloba recordes masculinos e femininos em piscina longa (50 metros) e piscina curta (25 metros), extraídos rigorosamente de fontes oficiais e enciclopédicas do esporte:

1.  **Olympics Official Channel:** [Lista de Recordes Mundiais de Natação - Olympics](https://www.olympics.com/pt/noticias/natacao-lista-recordes-mundiais)
2.  **Wikipédia Lusófona:** [Lista dos Recordes Mundiais de Natação - Wikipedia](https://pt.wikipedia.org/wiki/Lista_dos_recordes_mundiais_de_nata%C3%A7%C3%A3o)

Os dados foram tratados e estruturados em um pipeline de texto legível para modelos LLM, contendo: *Distância, Estilo, Tempo Exato, Nome do Atleta, País Representado, Data Histórica do Feito e a Competição onde o recorde foi quebrado*.

---

## 🧠 Arquitetura Técnica & Soluções Aplicadas

A estrutura foi desenhada sob o conceito de **Monorepo**, dividindo-se em duas aplicações independentes e desacopladas que se comunicam via requisições HTTP seguras.

### 1. Ingestão e Banco de Vetores (`init_db.py` - Desafio)
* **Geração de Embeddings:** Os registros textuais do dataset foram convertidos em vetores densos através do modelo oficial **`models/gemini-embedding-001`** do Google AI Studio.
* **Banco Vetorial Persistent:** Implementação com sucesso do desafio prático utilizando o **ChromaDB** (`chromadb.PersistentClient`) para indexar matematicamente os embeddings e guardar a base de dados vetorizada localmente na pasta `chroma_data/`.

### 2. Backend & Mecanismo Retrieval (`aquadata-backend/`)
* **Tecnologias:** Python, Flask, Flask-CORS e Gunicorn.
* **Algoritmo RAG Inteligente:** O backend intercepta as perguntas do usuário, filtra ruídos gramaticais (como stop-words) e realiza uma busca de contexto cirúrgica por correspondência semântica e aproximação no dataset estruturado.
* **Geração de Conteúdo:** O contexto recuperado é envelopado e injetado em um prompt sistêmico restrito enviado ao modelo **Gemini 2.5 Flash** via requisição estável HTTP (`v1`). Isso garante que a IA responda estritamente baseada em fatos reais da planilha.
* **Deploy:** Hospedado no **Render**, configurado com variáveis de ambiente ocultas e leitura dinâmica de portas para produção.

### 3. Frontend Temático (`aquadata-frontend/`)
* **Tecnologias:** React.js, Vite, HTML5, CSS3 avançado.
* **Customização Visual:** Interface 100% customizada do zero com paleta de cores azulada (temática de piscina), tipografia moderna, componentes de chat fluidos, tratamento de loading e renderização limpa.
* **Deploy:** Hospedado na **Vercel** com mapeamento direto de subpasta e isolamento de compilação Node.

---

## 🛠️ Como Executar o Projeto Localmente

### Backend (Flask)
1. Navegue até a pasta: `cd aquadata-backend`
2. Ative seu ambiente virtual: `venv\\Scripts\\activate` (Windows) ou `source venv/bin/activate` (Linux/Mac)
3. Instale as dependências limpas: `pip install -r requirements.txt`
4. Crie um arquivo `.env` na raiz da pasta e adicione sua chave:
env
   GEMINI_API_KEY=AIzaSy...

    Execute o servidor: python app.py (rodará em http://localhost:5000)

Frontend (React + Vite)

    Navegue até a pasta: cd aquadata-frontend

    Instale os pacotes do Node: npm install

    Inicie o servidor de desenvolvimento: npm run dev

🎓 Requisitos do Trabalho Prático Satisfeitos

    [x] Dataset Customizado: Mais de 70 linhas de dados reais sobre natação.

    [x] Temática de Interesse: Alinhado 100% ao TCC da dupla.

    [x] Embeddings do Google: Gerados com modelos oficiais do AI Studio.

    [x] Interface React Modificada: Cores, ícones e estilos adaptados ao tema.

    [x] Desafio Aceito: Implementação e estudo de embeddings com ChromaDB.

    [x] Hospedagem Completa: Frontend na Vercel e Backend no Render conversando em tempo real.

    [x] Código no GitHub: Repositório organizado em Monorepo limpo.

Desenvolvido com 💙 por Enrique e João Henrique — 2026.
