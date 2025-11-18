/**
 * Medical History API Service
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

export interface Prescription {
  medication_name: string;
  dosage: string;
  frequency: string;
  duration?: string;
  instructions?: string;
}

export interface MedicalHistory {
  history_id?: string;
  patient_id: string;
  doctor_id?: string;
  doctor_name: string;
  visit_date: string;
  diagnosis?: string;
  prescriptions?: Prescription[];
  health_status?: string;
  blood_pressure?: string;
  symptoms?: string[];
  notes?: string;
  follow_up_date?: string;
  created_at?: string;
  updated_at?: string;
}

export interface MedicalHistoryListResponse {
  records: MedicalHistory[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PatientListResponse {
  patients: any[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

class MedicalHistoryService {
  /**
   * Create a new medical history record
   */
  async createMedicalHistory(data: MedicalHistory): Promise<MedicalHistory> {
    const response = await fetch(`${API_BASE_URL}/medical-history/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create medical history');
    }

    return response.json();
  }

  /**
   * Get medical history by ID
   */
  async getMedicalHistory(historyId: string): Promise<MedicalHistory> {
    const response = await fetch(`${API_BASE_URL}/medical-history/${historyId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get medical history');
    }

    return response.json();
  }

  /**
   * Get all medical history for a patient
   */
  async getPatientMedicalHistory(
    patientId: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<MedicalHistoryListResponse> {
    const response = await fetch(
      `${API_BASE_URL}/medical-history/patient/${patientId}?page=${page}&page_size=${pageSize}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get patient medical history');
    }

    return response.json();
  }

  /**
   * Get all patients for a doctor
   */
  async getDoctorPatients(
    doctorId: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<PatientListResponse> {
    const response = await fetch(
      `${API_BASE_URL}/medical-history/doctor/${doctorId}/patients?page=${page}&page_size=${pageSize}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get doctor patients');
    }

    return response.json();
  }

  /**
   * Get all patients in the system
   */
  async getAllPatients(
    page: number = 1,
    pageSize: number = 20
  ): Promise<PatientListResponse> {
    const response = await fetch(
      `${API_BASE_URL}/medical-history/patients/all?page=${page}&page_size=${pageSize}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get all patients');
    }

    return response.json();
  }

  /**
   * Update medical history record
   */
  async updateMedicalHistory(
    historyId: string,
    data: Partial<MedicalHistory>
  ): Promise<MedicalHistory> {
    const response = await fetch(`${API_BASE_URL}/medical-history/${historyId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update medical history');
    }

    return response.json();
  }

  /**
   * Delete medical history record
   */
  async deleteMedicalHistory(historyId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/medical-history/${historyId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete medical history');
    }
  }

  /**
   * Upload a file (prescription, report, etc.)
   */
  async uploadFile(file: File, folder: string = 'prescriptions'): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder);

    const response = await fetch(`${API_BASE_URL}/files/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload file');
    }

    return response.json();
  }
}

export const medicalHistoryService = new MedicalHistoryService();
