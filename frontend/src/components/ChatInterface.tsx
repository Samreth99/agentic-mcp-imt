import React, { useState, useRef, useEffect, useCallback } from 'react';
import MessageBubble, { type Message } from './MessageBubble';
import ChatInput from './ChatInput';
import apiClient from '../api/client';
import './ChatInterface.css';

const generateId = () => Math.random().toString(36).substring(2, 9);

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [threadId] = useState(() => `thread-${generateId()}`);
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const health = await apiClient.healthCheck();
        setIsConnected(health.status === 'healthy');
      } catch {
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: generateId(),
      content,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.chat({
        message: content,
        thread_id: threadId,
      });

      const assistantMessage: Message = {
        id: generateId(),
        content: response.response,
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      
      const errorAssistantMessage: Message = {
        id: generateId(),
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorAssistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="chat-interface">
      <header className="chat-header">
        <div className="header-content">
          <div className="header-title">
            <h1>IMT Mines Alès Assistant</h1>
            <p className="header-subtitle">AI-powered help for students and staff</p>
          </div>
          <div className="header-actions">
            <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
              <span className="status-dot"></span>
              <span className="status-text">
                {isConnected === null ? 'Checking...' : isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            {messages.length > 0 && (
              <button className="clear-button" onClick={handleClearChat}>
                Clear Chat
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="chat-messages" ref={messagesContainerRef}>
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-icon">🎓</div>
            <h2>Welcome to IMT Mines Alès Assistant</h2>
            <p>Ask me anything about school programs, courses, regulations, or student life!</p>
            {/* <div className="suggestion-chips">
              <button onClick={() => handleSendMessage("What engineering programs are available?")}>
                Engineering programs
              </button>
              <button onClick={() => handleSendMessage("How can I access student services?")}>
                Student services
              </button>
              <button onClick={() => handleSendMessage("Tell me about the admission process")}>
                Admission process
              </button>
            </div> */}
          </div>
        ) : (
          <>
            {messages.map(message => (
              <MessageBubble key={message.id} message={message} />
            ))}
          </>
        )}
        <div ref={messagesEndRef} />
      </main>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      <ChatInput
        onSend={handleSendMessage}
        disabled={isLoading}
        placeholder={isLoading ? "Waiting for response..." : "Ask me anything..."}
      />
    </div>
  );
};

export default ChatInterface;
