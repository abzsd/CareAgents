/**
 * Example Chat Interface Component using CareAgents AI
 *
 * This is a complete example showing how to integrate the AI agent service
 * into your React application.
 */

import React, { useState, useRef, useEffect } from 'react';
import { useAgentService } from '../hooks/useAgentService';
import './ChatInterface.css'; // Create this file with your styles

interface ChatInterfaceProps {
  patientId?: string;
  sessionId?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  patientId,
  sessionId
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isConnected,
    isTyping,
    currentResponse,
    error,
    sendMessage,
    requestSummary,
    requestVitals,
    requestPrescriptions,
    clearMessages,
    reconnect
  } = useAgentService({
    sessionId,
    patientId,
    autoConnect: true,
    wsBaseUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
    apiBaseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000'
  });

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentResponse]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    await sendMessage(inputMessage);
    setInputMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-interface">
      {/* Header */}
      <div className="chat-header">
        <h2>CareAgents AI Assistant</h2>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
          {!isConnected && (
            <button onClick={reconnect} className="reconnect-btn">
              Reconnect
            </button>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <button onClick={requestSummary} disabled={!patientId || isTyping}>
          📋 Get Summary
        </button>
        <button onClick={requestVitals} disabled={!patientId || isTyping}>
          💓 View Vitals
        </button>
        <button onClick={requestPrescriptions} disabled={!patientId || isTyping}>
          💊 Prescriptions
        </button>
        <button onClick={clearMessages} disabled={isTyping}>
          🗑️ Clear Chat
        </button>
      </div>

      {/* Messages Area */}
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>👋 Welcome to CareAgents!</h3>
            <p>I can help you with:</p>
            <ul>
              <li>Accessing your medical records</li>
              <li>Understanding your health vitals</li>
              <li>Reviewing prescriptions and medications</li>
              <li>Answering healthcare questions</li>
            </ul>
            <p>How can I assist you today?</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role}`}
          >
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-text">
                {message.content}
              </div>
              <div className="message-timestamp">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {/* Streaming Response */}
        {isTyping && currentResponse && (
          <div className="message assistant streaming">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="message-text">
                {currentResponse}
                <span className="typing-cursor">▋</span>
              </div>
            </div>
          </div>
        )}

        {/* Typing Indicator */}
        {isTyping && !currentResponse && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button onClick={() => window.location.reload()}>
              Refresh
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-container">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
          disabled={!isConnected || isTyping}
          rows={3}
        />
        <button
          onClick={handleSendMessage}
          disabled={!isConnected || !inputMessage.trim() || isTyping}
          className="send-button"
        >
          {isTyping ? '⏳' : '📤'} Send
        </button>
      </div>

      {/* Footer */}
      <div className="chat-footer">
        <small>
          Powered by CareAgents AI • {messages.length} messages
        </small>
      </div>
    </div>
  );
};

export default ChatInterface;
