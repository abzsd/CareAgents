import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { MessageSquare, X, Send, Loader2, Bot, User } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const GuestChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your CareAgent AI assistant. How can I help you today? You can ask me about our services, book appointments, or get general health information.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat/guest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          history: messages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message || "I'm here to help! Could you please rephrase your question?",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);

      const fallbackResponses: Record<string, string> = {
        'appointment': "To book an appointment, please sign in with your Google account. Once logged in, you can browse our doctors and schedule appointments based on their availability.",
        'doctor': "We have over 100 certified healthcare professionals across various specializations including cardiology, pediatrics, general medicine, and more. Sign in to view their profiles and book consultations.",
        'service': "CareAgent offers telemedicine consultations, health record management, prescription tracking, appointment scheduling, and AI-powered health insights. Sign in to access all features!",
        'cost': "We offer flexible pricing plans. Basic consultations start at affordable rates. Sign in to view detailed pricing and available packages.",
        'emergency': "For medical emergencies, please call 911 or visit your nearest emergency room. Our platform is designed for non-emergency consultations and health management.",
        'default': "I'm here to help! I can provide information about our services, doctors, appointments, and features. For full access to all features including booking appointments and managing your health records, please sign in with your Google account.",
      };

      let responseContent = fallbackResponses.default;
      const lowerInput = userMessage.content.toLowerCase();

      for (const [key, value] of Object.entries(fallbackResponses)) {
        if (lowerInput.includes(key)) {
          responseContent = value;
          break;
        }
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseContent,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Chat Toggle Button */}
      {!isOpen && (
        <div
          id="guest-chat"
          className="fixed bottom-6 right-6 z-10"
        >
          <Button
            onClick={() => setIsOpen(true)}
            className="h-16 w-16 rounded-full bg-blue-600 hover:bg-blue-700 shadow-2xl"
          >
            <MessageSquare className="h-7 w-7 text-white" />
          </Button>
          <div className="absolute top-0 right-0 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
        </div>
      )}

      {/* Chat Window */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-slate-900 opacity-20"
            style={{ zIndex: 40 }}
            onClick={() => setIsOpen(false)}
          />

          {/* Chat Card */}
          <div
            className="fixed bottom-6 right-6 w-96 bg-white rounded-lg shadow-2xl border border-slate-200 flex flex-col"
            style={{ zIndex: 50, height: '600px' }}
          >
            {/* Header */}
            <div className="bg-blue-600 text-white rounded-t-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center" style={{ opacity: 0.2 }}>
                    <Bot className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <div className="text-lg font-medium">CareAgent AI</div>
                    <p className="text-xs text-blue-100">Always here to help</p>
                  </div>
                </div>
                <Button
                  onClick={() => setIsOpen(false)}
                  className="text-white h-8 w-8 p-0 bg-transparent hover:bg-white hover:bg-opacity-20"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 bg-slate-50">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div className={`flex items-start gap-2 ${message.role === 'user' ? 'flex-row-reverse' : ''}`} style={{ maxWidth: '80%' }}>
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          message.role === 'user'
                            ? 'bg-blue-500'
                            : 'bg-slate-200'
                        }`}
                      >
                        {message.role === 'user' ? (
                          <User className="h-4 w-4 text-white" />
                        ) : (
                          <Bot className="h-4 w-4 text-slate-700" />
                        )}
                      </div>
                      <div
                        className={`rounded-lg px-4 py-2 ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-slate-800 border border-slate-200'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p
                          className={`text-xs mt-1 ${
                            message.role === 'user' ? 'text-blue-100' : 'text-slate-400'
                          }`}
                        >
                          {message.timestamp.toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-start gap-2">
                      <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-slate-700" />
                      </div>
                      <div className="bg-white rounded-lg px-4 py-3 border border-slate-200">
                        <div className="flex gap-2">
                          <div className="w-2 h-2 bg-slate-400 rounded-full"></div>
                          <div className="w-2 h-2 bg-slate-400 rounded-full"></div>
                          <div className="w-2 h-2 bg-slate-400 rounded-full"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input */}
            <div className="p-4 bg-white border-t border-slate-200 rounded-b-lg">
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  disabled={isLoading}
                  className="flex-1 px-4 py-2 border border-slate-300 rounded-full text-sm"
                  style={{
                    outline: 'none',
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#3b82f6';
                    e.target.style.boxShadow = '0 0 0 2px rgba(59, 130, 246, 0.3)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#cbd5e1';
                    e.target.style.boxShadow = 'none';
                  }}
                />
                <Button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="rounded-full w-10 h-10 p-0 bg-blue-600 hover:bg-blue-700"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-slate-400 mt-2 text-center">
                Press Enter to send
              </p>
            </div>
          </div>
        </>
      )}
    </>
  );
};
