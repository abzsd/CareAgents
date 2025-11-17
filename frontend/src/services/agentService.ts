/**
 * Agent Service - WebSocket and REST client for CareAgents AI
 */

export enum MessageType {
  CONNECTED = 'connected',
  CHAT_MESSAGE = 'chat_message',
  CHAT_RESPONSE = 'chat_response',
  STREAM_START = 'stream_start',
  STREAM_CHUNK = 'stream_chunk',
  STREAM_END = 'stream_end',
  ERROR = 'error',
  RECORD_REQUEST = 'record_request',
  RECORD_RESPONSE = 'record_response',
  SYSTEM = 'system',
  TYPING = 'typing'
}

export interface Message {
  type: MessageType;
  message?: string;
  chunk?: string;
  response?: string;
  error?: string;
  code?: string;
  timestamp?: string;
  session_id?: string;
  metadata?: Record<string, any>;
  is_typing?: boolean;
  agent_type?: string;
  full_response?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface AgentServiceConfig {
  wsBaseUrl?: string;
  apiBaseUrl?: string;
  autoReconnect?: boolean;
  reconnectDelay?: number;
  maxReconnectAttempts?: number;
}

export type MessageHandler = (message: Message) => void;
export type ChunkHandler = (chunk: string) => void;
export type ErrorHandler = (error: string, code?: string) => void;

export class AgentService {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private patientId?: string;
  private config: Required<AgentServiceConfig>;
  private reconnectAttempts = 0;
  private messageHandlers: Set<MessageHandler> = new Set();
  private chunkHandlers: Set<ChunkHandler> = new Set();
  private errorHandlers: Set<ErrorHandler> = new Set();
  private reconnectTimeout?: NodeJS.Timeout;
  private isConnecting = false;

  constructor(
    sessionId: string,
    patientId?: string,
    config?: AgentServiceConfig
  ) {
    this.sessionId = sessionId;
    this.patientId = patientId;
    this.config = {
      wsBaseUrl: config?.wsBaseUrl || 'ws://localhost:8000',
      apiBaseUrl: config?.apiBaseUrl || 'http://localhost:8000',
      autoReconnect: config?.autoReconnect ?? true,
      reconnectDelay: config?.reconnectDelay || 3000,
      maxReconnectAttempts: config?.maxReconnectAttempts || 5
    };
  }

  /**
   * Connect to WebSocket
   */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    if (this.isConnecting) {
      console.log('Connection already in progress');
      return;
    }

    this.isConnecting = true;

    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.config.wsBaseUrl}/ws/chat/${this.sessionId}${
          this.patientId ? `?patient_id=${this.patientId}` : ''
        }`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: Message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.isConnecting = false;
          this.handleDisconnect();
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Send a chat message
   */
  async sendMessage(message: string, patientId?: string): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      await this.connect();
    }

    const payload = {
      type: MessageType.CHAT_MESSAGE,
      message,
      patient_id: patientId || this.patientId,
      timestamp: new Date().toISOString()
    };

    this.ws!.send(JSON.stringify(payload));
  }

  /**
   * Request patient records
   */
  async requestRecords(
    requestType: 'summary' | 'vitals' | 'prescriptions',
    options?: {
      vitalType?: string;
      days?: number;
    }
  ): Promise<void> {
    if (!this.patientId) {
      throw new Error('Patient ID is required for record requests');
    }

    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      await this.connect();
    }

    const payload = {
      type: MessageType.RECORD_REQUEST,
      request_type: requestType,
      patient_id: this.patientId,
      ...options,
      timestamp: new Date().toISOString()
    };

    this.ws!.send(JSON.stringify(payload));
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: Message): void {
    // Call all message handlers
    this.messageHandlers.forEach(handler => handler(message));

    // Handle specific message types
    switch (message.type) {
      case MessageType.STREAM_CHUNK:
        if (message.chunk) {
          this.chunkHandlers.forEach(handler => handler(message.chunk!));
        }
        break;

      case MessageType.ERROR:
        if (message.error) {
          this.errorHandlers.forEach(handler => handler(message.error!, message.code));
        }
        break;

      case MessageType.CONNECTED:
        console.log('Connected to agent:', message.message);
        break;

      case MessageType.STREAM_START:
        console.log('Stream started:', message.agent_type);
        break;

      case MessageType.STREAM_END:
        console.log('Stream ended');
        break;
    }
  }

  /**
   * Handle disconnection
   */
  private handleDisconnect(): void {
    if (
      this.config.autoReconnect &&
      this.reconnectAttempts < this.config.maxReconnectAttempts
    ) {
      this.reconnectAttempts++;
      console.log(
        `Attempting to reconnect (${this.reconnectAttempts}/${this.config.maxReconnectAttempts})...`
      );

      this.reconnectTimeout = setTimeout(() => {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error);
        });
      }, this.config.reconnectDelay);
    } else if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.errorHandlers.forEach(handler =>
        handler('Connection lost. Please refresh the page.', 'MAX_RECONNECT_REACHED')
      );
    }
  }

  /**
   * Add message handler
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  /**
   * Add chunk handler for streaming
   */
  onChunk(handler: ChunkHandler): () => void {
    this.chunkHandlers.add(handler);
    return () => this.chunkHandlers.delete(handler);
  }

  /**
   * Add error handler
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.add(handler);
    return () => this.errorHandlers.delete(handler);
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // REST API Methods (for non-streaming requests)

  /**
   * Send non-streaming chat message
   */
  async chatNonStreaming(message: string, patientId?: string): Promise<string> {
    const response = await fetch(`${this.config.apiBaseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        patient_id: patientId || this.patientId,
        session_id: this.sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.response;
  }

  /**
   * Get patient summary (non-streaming)
   */
  async getPatientSummary(patientId?: string): Promise<string> {
    const response = await fetch(`${this.config.apiBaseUrl}/api/records/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        patient_id: patientId || this.patientId,
        request_type: 'summary',
        session_id: this.sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.summary;
  }

  /**
   * Analyze vitals (non-streaming)
   */
  async analyzeVitals(
    options?: {
      vitalType?: string;
      days?: number;
      patientId?: string;
    }
  ): Promise<string> {
    const response = await fetch(`${this.config.apiBaseUrl}/api/records/vitals`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        patient_id: options?.patientId || this.patientId,
        request_type: 'vitals',
        vital_type: options?.vitalType,
        days: options?.days || 30,
        session_id: this.sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.analysis;
  }

  /**
   * Get prescription summary (non-streaming)
   */
  async getPrescriptionSummary(patientId?: string): Promise<string> {
    const response = await fetch(`${this.config.apiBaseUrl}/api/records/prescriptions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        patient_id: patientId || this.patientId,
        request_type: 'prescriptions',
        session_id: this.sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    const data = await response.json();
    return data.summary;
  }

  /**
   * Clear session
   */
  async clearSession(): Promise<void> {
    await fetch(`${this.config.apiBaseUrl}/api/session/${this.sessionId}`, {
      method: 'DELETE'
    });
  }
}

/**
 * Create a new agent service instance
 */
export function createAgentService(
  sessionId?: string,
  patientId?: string,
  config?: AgentServiceConfig
): AgentService {
  const id = sessionId || `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  return new AgentService(id, patientId, config);
}

export default AgentService;
