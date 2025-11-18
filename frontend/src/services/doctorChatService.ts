/**
 * Doctor Chat Service
 * AI-powered patient summary and chat interface
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface ChatMessage {
  role: string;
  parts: Array<{ text: string }>;
}

export interface ChatResponse {
  response: string;
  patient_id: string;
}

export interface SummaryResponse {
  summary: string;
  summary_type: string;
  patient_id: string;
}

export interface RiskAnalysis {
  risk_level: 'low' | 'moderate' | 'high' | 'unknown';
  risk_factors?: string[];
  health_trends?: {
    overall: 'improving' | 'stable' | 'declining';
    details: string;
  };
  areas_of_concern?: string[];
  recommendations?: string[];
  summary?: string;
  patient_id: string;
}

class DoctorChatService {
  /**
   * Chat with AI agent about a patient
   */
  async chat(
    query: string,
    patientId: string,
    conversationHistory?: ChatMessage[]
  ): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/doctor-chat/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        patient_id: patientId,
        conversation_history: conversationHistory,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Chat failed');
    }

    return response.json();
  }

  /**
   * Get patient summary
   */
  async getSummary(
    patientId: string,
    summaryType: 'comprehensive' | 'brief' | 'recent' | 'medications' = 'comprehensive'
  ): Promise<SummaryResponse> {
    const response = await fetch(`${API_BASE_URL}/doctor-chat/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        patient_id: patientId,
        summary_type: summaryType,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get summary');
    }

    return response.json();
  }

  /**
   * Get risk analysis for a patient
   */
  async getRiskAnalysis(patientId: string): Promise<RiskAnalysis> {
    const response = await fetch(`${API_BASE_URL}/doctor-chat/risk-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        patient_id: patientId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get risk analysis');
    }

    return response.json();
  }

  /**
   * Chat with streaming responses
   */
  async chatStream(
    query: string,
    patientId: string,
    conversationHistory?: ChatMessage[]
  ): Promise<ReadableStream<Uint8Array>> {
    const response = await fetch(`${API_BASE_URL}/doctor-chat/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        patient_id: patientId,
        conversation_history: conversationHistory,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Streaming chat failed');
    }

    if (!response.body) {
      throw new Error('Response body is null');
    }

    return response.body;
  }
}

export const doctorChatService = new DoctorChatService();
