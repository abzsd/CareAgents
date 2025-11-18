/**
 * Prescription Parser Service
 * Interfaces with the prescription parsing AI agent
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface ParsedPrescription {
  doctor: {
    name: string;
    license: string;
    clinic: string;
    contact: string;
  };
  patient: {
    name: string;
    age: string;
    gender: string;
    id: string;
  };
  date: string;
  medications: Array<{
    name: string;
    brand_name?: string;
    dosage: string;
    frequency: string;
    duration: string;
    quantity: string;
    instructions: string;
    route: string;
  }>;
  diagnosis: string;
  additional_notes: string;
  follow_up: string;
  confidence_score: number;
  unclear_portions?: string[];
  handwritten_sections?: string[];
  warnings?: string[];
  gcs_url?: string;
  file_id?: string;
  error?: string;
}

class PrescriptionParserService {
  /**
   * Parse a prescription image file
   */
  async parseImage(file: File): Promise<ParsedPrescription> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/prescription-parser/parse-image`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to parse prescription');
    }

    return response.json();
  }

  /**
   * Parse a prescription from URL
   */
  async parseFromUrl(imageUrl: string): Promise<ParsedPrescription> {
    const formData = new FormData();
    formData.append('image_url', imageUrl);

    const response = await fetch(`${API_BASE_URL}/prescription-parser/parse-url`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to parse prescription');
    }

    return response.json();
  }

  /**
   * Convert parsed prescription to editable text
   */
  async convertToText(prescriptionData: ParsedPrescription): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/prescription-parser/convert-to-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(prescriptionData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to convert prescription');
    }

    const result = await response.json();
    return result.text;
  }
}

export const prescriptionParserService = new PrescriptionParserService();
