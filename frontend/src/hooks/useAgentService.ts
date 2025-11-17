/**
 * React Hook for CareAgents AI Service
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import {
  AgentService,
  createAgentService,
  MessageType,
  Message,
  ChatMessage,
  AgentServiceConfig
} from '../services/agentService';

export interface UseAgentServiceOptions extends AgentServiceConfig {
  sessionId?: string;
  patientId?: string;
  autoConnect?: boolean;
}

export interface UseAgentServiceReturn {
  // State
  messages: ChatMessage[];
  isConnected: boolean;
  isTyping: boolean;
  error: string | null;
  currentResponse: string;

  // Actions
  sendMessage: (message: string) => Promise<void>;
  requestSummary: () => Promise<void>;
  requestVitals: (vitalType?: string, days?: number) => Promise<void>;
  requestPrescriptions: () => Promise<void>;
  clearMessages: () => void;
  reconnect: () => Promise<void>;
  disconnect: () => void;

  // Service instance
  service: AgentService | null;
}

export function useAgentService(
  options?: UseAgentServiceOptions
): UseAgentServiceReturn {
  const [service, setService] = useState<AgentService | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentResponse, setCurrentResponse] = useState('');

  const currentResponseRef = useRef('');
  const isStreamingRef = useRef(false);

  // Initialize service
  useEffect(() => {
    const agentService = createAgentService(
      options?.sessionId,
      options?.patientId,
      {
        wsBaseUrl: options?.wsBaseUrl,
        apiBaseUrl: options?.apiBaseUrl,
        autoReconnect: options?.autoReconnect,
        reconnectDelay: options?.reconnectDelay,
        maxReconnectAttempts: options?.maxReconnectAttempts
      }
    );

    setService(agentService);

    // Setup message handler
    const unsubscribeMessage = agentService.onMessage((message: Message) => {
      handleMessage(message);
    });

    // Setup chunk handler
    const unsubscribeChunk = agentService.onChunk((chunk: string) => {
      currentResponseRef.current += chunk;
      setCurrentResponse(currentResponseRef.current);
    });

    // Setup error handler
    const unsubscribeError = agentService.onError((errorMsg: string, code?: string) => {
      setError(errorMsg);
      console.error('Agent error:', errorMsg, code);
    });

    // Auto-connect if enabled
    if (options?.autoConnect !== false) {
      agentService.connect().catch(err => {
        setError('Failed to connect to agent service');
        console.error('Connection error:', err);
      });
    }

    // Cleanup
    return () => {
      unsubscribeMessage();
      unsubscribeChunk();
      unsubscribeError();
      agentService.disconnect();
    };
  }, [options?.sessionId, options?.patientId]);

  // Handle messages
  const handleMessage = useCallback((message: Message) => {
    switch (message.type) {
      case MessageType.CONNECTED:
        setIsConnected(true);
        setError(null);
        break;

      case MessageType.STREAM_START:
        isStreamingRef.current = true;
        currentResponseRef.current = '';
        setCurrentResponse('');
        setIsTyping(true);
        break;

      case MessageType.STREAM_CHUNK:
        // Already handled by chunk handler
        break;

      case MessageType.STREAM_END:
        isStreamingRef.current = false;
        setIsTyping(false);

        // Add assistant message
        if (currentResponseRef.current) {
          setMessages(prev => [
            ...prev,
            {
              role: 'assistant',
              content: currentResponseRef.current,
              timestamp: new Date().toISOString()
            }
          ]);
        }

        currentResponseRef.current = '';
        setCurrentResponse('');
        break;

      case MessageType.CHAT_RESPONSE:
        // Non-streaming response
        if (message.response) {
          setMessages(prev => [
            ...prev,
            {
              role: 'assistant',
              content: message.response!,
              timestamp: new Date().toISOString()
            }
          ]);
        }
        break;

      case MessageType.ERROR:
        setError(message.error || 'An error occurred');
        setIsTyping(false);
        isStreamingRef.current = false;
        break;

      case MessageType.TYPING:
        setIsTyping(message.is_typing || false);
        break;

      default:
        console.log('Unhandled message type:', message.type);
    }
  }, []);

  // Send message
  const sendMessage = useCallback(async (message: string) => {
    if (!service) {
      setError('Service not initialized');
      return;
    }

    try {
      // Add user message
      setMessages(prev => [
        ...prev,
        {
          role: 'user',
          content: message,
          timestamp: new Date().toISOString()
        }
      ]);

      setError(null);
      await service.sendMessage(message);
    } catch (err) {
      setError('Failed to send message');
      console.error('Send message error:', err);
    }
  }, [service]);

  // Request patient summary
  const requestSummary = useCallback(async () => {
    if (!service) {
      setError('Service not initialized');
      return;
    }

    try {
      setError(null);
      await service.requestRecords('summary');
    } catch (err) {
      setError('Failed to request summary');
      console.error('Request summary error:', err);
    }
  }, [service]);

  // Request vitals analysis
  const requestVitals = useCallback(async (vitalType?: string, days?: number) => {
    if (!service) {
      setError('Service not initialized');
      return;
    }

    try {
      setError(null);
      await service.requestRecords('vitals', { vitalType, days });
    } catch (err) {
      setError('Failed to request vitals');
      console.error('Request vitals error:', err);
    }
  }, [service]);

  // Request prescriptions
  const requestPrescriptions = useCallback(async () => {
    if (!service) {
      setError('Service not initialized');
      return;
    }

    try {
      setError(null);
      await service.requestRecords('prescriptions');
    } catch (err) {
      setError('Failed to request prescriptions');
      console.error('Request prescriptions error:', err);
    }
  }, [service]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentResponse('');
    currentResponseRef.current = '';
  }, []);

  // Reconnect
  const reconnect = useCallback(async () => {
    if (!service) {
      setError('Service not initialized');
      return;
    }

    try {
      setError(null);
      await service.connect();
    } catch (err) {
      setError('Failed to reconnect');
      console.error('Reconnect error:', err);
    }
  }, [service]);

  // Disconnect
  const disconnect = useCallback(() => {
    if (service) {
      service.disconnect();
      setIsConnected(false);
    }
  }, [service]);

  return {
    messages,
    isConnected,
    isTyping,
    error,
    currentResponse,
    sendMessage,
    requestSummary,
    requestVitals,
    requestPrescriptions,
    clearMessages,
    reconnect,
    disconnect,
    service
  };
}

export default useAgentService;
