/**
 * Appointment API Service
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

export interface Appointment {
  appointment_id?: string;
  patient_id: string;
  doctor_id: string;
  appointment_date: string;
  appointment_time: string;
  appointment_type: 'consultation' | 'follow_up' | 'routine_checkup' | 'emergency' | 'teleconsultation';
  status?: 'scheduled' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  reason?: string;
  notes?: string;
  location?: string;
  duration_minutes?: number;
  patient_name?: string;
  doctor_name?: string;
  doctor_specialization?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AppointmentListResponse {
  appointments: Appointment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

class AppointmentService {
  /**
   * Create a new appointment
   */
  async createAppointment(data: Omit<Appointment, 'appointment_id'>): Promise<Appointment> {
    const response = await fetch(`${API_BASE_URL}/appointments/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create appointment');
    }

    return response.json();
  }

  /**
   * Get appointment by ID
   */
  async getAppointment(appointmentId: string): Promise<Appointment> {
    const response = await fetch(`${API_BASE_URL}/appointments/${appointmentId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get appointment');
    }

    return response.json();
  }

  /**
   * Get all appointments for a patient
   */
  async getPatientAppointments(
    patientId: string,
    page: number = 1,
    pageSize: number = 20,
    status?: string
  ): Promise<AppointmentListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (status) {
      params.append('status', status);
    }

    const response = await fetch(
      `${API_BASE_URL}/appointments/patient/${patientId}?${params.toString()}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get patient appointments');
    }

    return response.json();
  }

  /**
   * Get all appointments for a doctor
   */
  async getDoctorAppointments(
    doctorId: string,
    page: number = 1,
    pageSize: number = 20,
    status?: string,
    appointmentDate?: string
  ): Promise<AppointmentListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (status) {
      params.append('status', status);
    }

    if (appointmentDate) {
      params.append('appointment_date', appointmentDate);
    }

    const response = await fetch(
      `${API_BASE_URL}/appointments/doctor/${doctorId}?${params.toString()}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get doctor appointments');
    }

    return response.json();
  }

  /**
   * Update appointment
   */
  async updateAppointment(
    appointmentId: string,
    data: Partial<Appointment>
  ): Promise<Appointment> {
    const response = await fetch(`${API_BASE_URL}/appointments/${appointmentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update appointment');
    }

    return response.json();
  }

  /**
   * Cancel appointment
   */
  async cancelAppointment(appointmentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/appointments/${appointmentId}/cancel`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to cancel appointment');
    }
  }

  /**
   * Delete appointment
   */
  async deleteAppointment(appointmentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/appointments/${appointmentId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete appointment');
    }
  }
}

export const appointmentService = new AppointmentService();
