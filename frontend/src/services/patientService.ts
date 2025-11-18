/**
 * Patient API Service
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface PatientData {
  patient_id?: string;
  user_id?: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  email?: string;
  phone?: string;
  blood_type?: string;
  allergies?: string[];
  chronic_conditions?: string[];
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zip_code?: string;
    country?: string;
  };
  emergency_contact?: {
    name?: string;
    relationship?: string;
    phone?: string;
  };
  insurance_info?: {
    provider?: string;
    policy_number?: string;
    group_number?: string;
  };
  age?: number;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreatePatientRequest {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  email?: string;
  phone?: string;
  blood_type?: string;
  allergies?: string[];
  chronic_conditions?: string[];
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zip_code?: string;
    country?: string;
  };
  emergency_contact?: {
    name?: string;
    relationship?: string;
    phone?: string;
  };
  insurance_info?: {
    provider?: string;
    policy_number?: string;
    group_number?: string;
  };
}

class PatientService {
  /**
   * Create a patient record for a user
   */
  async createPatientForUser(userId: string, data: CreatePatientRequest): Promise<PatientData> {
    const response = await fetch(`${API_BASE_URL}/patients/user/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create patient');
    }

    return response.json();
  }

  /**
   * Get patient by user ID
   */
  async getPatientByUserId(userId: string): Promise<PatientData> {
    const response = await fetch(`${API_BASE_URL}/patients/user/${userId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get patient');
    }

    return response.json();
  }

  /**
   * Get patient by ID
   */
  async getPatient(patientId: string): Promise<PatientData> {
    const response = await fetch(`${API_BASE_URL}/patients/${patientId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get patient');
    }

    return response.json();
  }

  /**
   * Update patient information
   */
  async updatePatient(patientId: string, data: Partial<CreatePatientRequest>): Promise<PatientData> {
    const response = await fetch(`${API_BASE_URL}/patients/${patientId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update patient');
    }

    return response.json();
  }

  /**
   * List all patients
   */
  async listPatients(page: number = 1, pageSize: number = 20): Promise<{
    patients: PatientData[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    const response = await fetch(`${API_BASE_URL}/patients/?${params.toString()}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to list patients');
    }

    return response.json();
  }
}

export const patientService = new PatientService();
