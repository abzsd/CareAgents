/**
 * AI-Powered Appointment Service
 * Uses Google ADK for intelligent doctor matching and scheduling
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface DoctorMatchRequest {
  reason: string;
  symptoms?: string[];
  preferred_specialization?: string;
}

export interface DoctorMatchResponse {
  recommended_doctor_id: string;
  doctor_name: string;
  specialization: string;
  confidence_score: number;
  reasoning: string;
  alternative_doctors: string[];
}

export interface AppointmentSlot {
  date: string;
  time: string;
  day_of_week: string;
  time_of_day: string;
  confidence: number;
}

export interface SlotSuggestionResponse {
  suggested_slots: AppointmentSlot[];
  reasoning: string;
  notes: string;
}

export interface RequestAnalysisResponse {
  urgency_level: 'routine' | 'moderate' | 'urgent' | 'emergency';
  recommended_specialization: string;
  alternative_specializations: string[];
  teleconsultation_suitable: boolean;
  suggested_questions: string[];
  pre_appointment_notes: string;
  reasoning: string;
}

export interface SmartBookingRequest {
  patient_id: string;
  reason: string;
  symptoms?: string[];
  preferred_specialization?: string;
  patient_preference?: string; // morning, afternoon, evening
}

export interface SmartBookingResponse {
  analysis: RequestAnalysisResponse;
  doctor_match: DoctorMatchResponse;
  suggested_slots: SlotSuggestionResponse;
  next_steps: string;
}

class AIAppointmentService {
  /**
   * Use AI to match patient with the best doctor
   */
  async matchDoctor(request: DoctorMatchRequest): Promise<DoctorMatchResponse> {
    const response = await fetch(`${API_BASE_URL}/ai-appointments/match-doctor`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to match doctor');
    }

    return response.json();
  }

  /**
   * Use AI to suggest optimal appointment slots
   */
  async suggestSlots(
    doctorId: string,
    patientPreference?: string,
    preferredDate?: string
  ): Promise<SlotSuggestionResponse> {
    const response = await fetch(`${API_BASE_URL}/ai-appointments/suggest-slots`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        doctor_id: doctorId,
        patient_preference: patientPreference,
        preferred_date: preferredDate,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to suggest slots');
    }

    return response.json();
  }

  /**
   * Use AI to analyze appointment request
   */
  async analyzeRequest(
    reason: string,
    symptoms?: string[],
    patientId?: string
  ): Promise<RequestAnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/ai-appointments/analyze-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        reason,
        symptoms,
        patient_id: patientId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to analyze request');
    }

    return response.json();
  }

  /**
   * Smart booking - complete end-to-end AI-powered appointment booking
   */
  async bookSmart(request: SmartBookingRequest): Promise<SmartBookingResponse> {
    const params = new URLSearchParams({
      patient_id: request.patient_id,
      reason: request.reason,
    });

    if (request.symptoms && request.symptoms.length > 0) {
      request.symptoms.forEach(symptom => params.append('symptoms', symptom));
    }

    if (request.preferred_specialization) {
      params.append('preferred_specialization', request.preferred_specialization);
    }

    if (request.patient_preference) {
      params.append('patient_preference', request.patient_preference);
    }

    const response = await fetch(
      `${API_BASE_URL}/ai-appointments/book-smart?${params.toString()}`,
      {
        method: 'POST',
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to book appointment');
    }

    return response.json();
  }
}

export const aiAppointmentService = new AIAppointmentService();
