import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, RefreshCw, Waves } from 'lucide-react';
import './App.css';
import ReactMarkdown from 'react-markdown';

function App() {
  const [mensagens, setMensagens] = useState([
    { 
      id: 1, 
      texto: "Olá! Sou o AquaData ChatBot. Sou especialista na análise de desempenho e recordes mundiais de natação. O que você gostaria de consultar hoje?", 
      remetente: 'bot' 
    }
  ]);
  const [input, setInput] = useState('');
  const [carregando, setCarregando] = useState(false);
  const mensagensEndRef = useRef(null);

  useEffect(() => {
    mensagensEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [mensagens, carregando]);

  const enviarMensagem = async () => {
    if (!input.trim()) return;

    const mensagemUsuario = input;
    setInput('');
    
    setMensagens(prev => [...prev, { id: Date.now(), texto: mensagemUsuario, remetente: 'user' }]);
    setCarregando(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mensagem: mensagemUsuario }),
      });

      const dados = await response.json();

      if (response.ok) {
        setMensagens(prev => [...prev, { id: Date.now() + 1, texto: dados.mensagem, remetente: 'bot' }]);
      } else {
        setMensagens(prev => [...prev, { id: Date.now() + 1, texto: "Ops, ocorreu um erro ao processar a resposta.", remetente: 'bot' }]);
      }
    } catch (error) {
      console.error(error);
      setMensagens(prev => [...prev, { id: Date.now() + 1, texto: "Não consegui conectar ao servidor do backend. Verifique se o Flask está rodando.", remetente: 'bot' }]);
    } finally {
      setCarregando(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      enviarMensagem();
    }
  };

  const limparChat = () => {
    setMensagens([
      { 
        id: 1, 
        texto: "Histórico limpo. Como posso ajudar com os recordes de natação agora?", 
        remetente: 'bot' 
      }
    ]);
  };

  return (
    <div className="app-container">
      {/* Topo / Header Temático de Natação com Identificação do Campus */}
      <header className="chat-header">
        <div className="header-info">
          <div className="logo-swimming">
            <Waves size={24} color="#00ffff" />
          </div>
          <div>
            <h1>AquaData ChatBot</h1>
            <p className="sub-institucional">IFSULDEMINAS — Campus Machado</p>
          </div>
        </div>
        <button onClick={limparChat} className="btn-clear" title="Novo Chat">
          <RefreshCw size={16} />
          <span>Novo Chat</span>
        </button>
      </header>

      {/* Área de Histórico das Mensagens */}
      <div className="chat-messages">
        {mensagens.map((msg) => (
          <div key={msg.id} className={`message-row ${msg.remetente}`}>
            <div className="avatar">
              {msg.remetente === 'bot' ? <Bot size={20} /> : <User size={20} />}
            </div>
            <div className="message-bubble">
              <ReactMarkdown>{msg.texto}</ReactMarkdown>
            </div>
          </div>
        ))}

        {/* Indicador de Carregamento */}
        {carregando && (
          <div className="message-row bot loading">
            <div className="avatar">
              <Bot size={20} />
            </div>
            <div className="message-bubble loading-bubble">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          </div>
        )}
        <div ref={mensagensEndRef} />
      </div>

      {/* Campo de Entrada (Input) e Créditos */}
      <footer className="chat-footer">
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pergunte sobre uma prova ou recordista (Ex: Recorde dos 100m livre)"
            disabled={carregando}
          />
          <button onClick={enviarMensagem} disabled={carregando || !input.trim()}>
            <Send size={18} />
          </button>
        </div>
        
        {/* Assinatura dos Desenvolvedores e TCC */}
        <div className="footer-credits">
          <p>Desenvolvido por: <strong>Enrique Rocha Lobo da Silva</strong> & <strong>João Henrique Souza Almeida</strong></p>
          <p className="tcc-tag">Projeto AquaData — TCC Sistemas de Informação</p>
        </div>
      </footer>
    </div>
  );
}

export default App;