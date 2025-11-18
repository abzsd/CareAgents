/**
 * Doctor API Service
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface Doctor {
  doctor_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  specialization: string;
  sub_specializations?: string[];
  license_number: string;
  license_state: string;
  years_of_experience?: number;
  consultation_fee?: number;
  rating?: number;
  total_patients_treated?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DoctorListResponse {
  doctors: Doctor[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

class DoctorService {
  /**
   * Get all doctors with optional filters
   */
  async getDoctors(
    page: number = 1,
    pageSize: number = 20,
    specialization?: string,
    activeOnly: boolean = true
  ): Promise<DoctorListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      active_only: activeOnly.toString(),
    });

    if (specialization) {
      params.append('specialization', specialization);
    }

    const response = await fetch(`${API_BASE_URL}/doctors/?${params.toString()}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get doctors');
    }

    return response.json();
  }

  /**
   * Get doctor by ID
   */
  async getDoctor(doctorId: string): Promise<Doctor> {
    const response = await fetch(`${API_BASE_URL}/doctors/${doctorId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get doctor');
    }

    return response.json();
  }

  /**
   * Get doctor by user ID
   */
  async getDoctorByUserId(userId: string): Promise<Doctor> {
    const response = await fetch(`${API_BASE_URL}/doctors/user/${userId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get doctor');
    }

    return response.json();
  }

  /**
   * Search doctors
   */
  async searchDoctors(query: string, limit: number = 20): Promise<Doctor[]> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });

    const response = await fetch(`${API_BASE_URL}/doctors/search/?${params.toString()}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to search doctors');
    }

    return response.json();
  }

  /**
   * Get list of all specializations
   */
  async getSpecializations(): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/doctors/specializations/list`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get specializations');
    }

    return response.json();
  }
}

export const doctorService = new DoctorService();
