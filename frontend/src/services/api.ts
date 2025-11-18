import { auth } from '../firebase/config';

// Base URL without /api/v1 suffix
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

// Get Firebase ID token for authenticated requests
const getIdToken = async (): Promise<string | null> => {
  const user = auth.currentUser;
  if (user) {
    try {
      return await user.getIdToken();
    } catch (error) {
      console.error('Error getting ID token:', error);
      return null;
    }
  }
  return null;
};

// Generic API request function
const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = await getIdToken();

  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  
  // Add Firebase ID token to Authorization header if user is authenticated
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    
    // Handle 401 Unauthorized responses
    if (response.status === 401) {
      console.warn('Unauthorized request - user may need to re-authenticate');
      // Optionally trigger re-authentication or redirect to login
    }
    
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// User API functions
export const userApi = {
  // Create new user
  createUser: async (userData: any) => {
    const response = await apiRequest('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    if (!response.ok) {
      throw new Error(`Failed to create user: ${response.statusText}`);
    }
    return response.json();
  },

  // Get user by Firebase UID
  getUserByFirebaseUid: async (firebaseUid: string) => {
    const response = await apiRequest(`/users/firebase/${firebaseUid}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`);
    }
    return response.json();
  },

  // Get user by email
  getUserByEmail: async (email: string) => {
    const response = await apiRequest(`/users/email/${email}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`);
    }
    return response.json();
  },

  // Update user
  updateUser: async (userId: string, userData: any) => {
    const response = await apiRequest(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
    if (!response.ok) {
      throw new Error(`Failed to update user: ${response.statusText}`);
    }
    return response.json();
  },

  // Set user as onboarded
  setUserOnboarded: async (userId: string) => {
    const response = await apiRequest(`/users/${userId}/onboarded`, {
      method: 'PUT',
    });
    if (!response.ok) {
      throw new Error(`Failed to update user onboarding status: ${response.statusText}`);
    }
    return response.json();
  },

  // Get user by database ID
  getUserById: async (userId: string) => {
    const response = await apiRequest(`/users/${userId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`);
    }
    return response.json();
  }
};

// Patient API functions
export const patientApi = {
  // Get all patients
  getPatients: async (page: number = 1, pageSize: number = 20, activeOnly: boolean = true) => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      active_only: activeOnly.toString()
    });
    const response = await apiRequest(`/patients?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch patients: ${response.statusText}`);
    }
    return response.json();
  },

  // Get patient by ID
  getPatient: async (patientId: string) => {
    const response = await apiRequest(`/patients/${patientId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch patient: ${response.statusText}`);
    }
    return response.json();
  },

  // Create new patient
  createPatient: async (patientData: any) => {
    const response = await apiRequest('/patients', {
      method: 'POST',
      body: JSON.stringify(patientData),
    });
    if (!response.ok) {
      throw new Error(`Failed to create patient: ${response.statusText}`);
    }
    return response.json();
  },

  // Update patient
  updatePatient: async (patientId: string, patientData: any) => {
    const response = await apiRequest(`/patients/${patientId}`, {
      method: 'PUT',
      body: JSON.stringify(patientData),
    });
    if (!response.ok) {
      throw new Error(`Failed to update patient: ${response.statusText}`);
    }
    return response.json();
  },

  // Delete patient (soft delete)
  deletePatient: async (patientId: string) => {
    const response = await apiRequest(`/patients/${patientId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to delete patient: ${response.statusText}`);
    }
    return response.status === 204;
  },

  // Search patients
  searchPatients: async (query: string, limit: number = 20) => {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString()
    });
    const response = await apiRequest(`/patients/search?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to search patients: ${response.statusText}`);
    }
    return response.json();
  }
};

// Guest Chat API functions (no authentication required)
export const guestChatApi = {
  // Send a guest chat message
  sendMessage: async (message: string, history: Array<{ role: string; content: string }>) => {
    const url = `${BASE_URL}/api/chat/guest`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        history,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`);
    }

    return response.json();
  },

  // Check guest chat health
  checkHealth: async () => {
    const url = `${BASE_URL}/api/chat/health`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to check chat health: ${response.statusText}`);
    }

    return response.json();
  },
};

// Doctor API functions
export const doctorApi = {
  // Get doctor by user ID
  getDoctorByUserId: async (userId: string) => {
    const response = await apiRequest(`/doctors/user/${userId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch doctor: ${response.statusText}`);
    }
    return response.json();
  },

  // Get doctor by ID
  getDoctor: async (doctorId: string) => {
    const response = await apiRequest(`/doctors/${doctorId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch doctor: ${response.statusText}`);
    }
    return response.json();
  }
};

// Onboarding API functions
export const onboardingApi = {
  // Onboard a doctor
  onboardDoctor: async (doctorData: any) => {
    const response = await apiRequest('/onboarding/doctor', {
      method: 'POST',
      body: JSON.stringify(doctorData),
    });
    if (!response.ok) {
      throw new Error(`Failed to onboard doctor: ${response.statusText}`);
    }
    return response.json();
  },

  // Onboard a patient
  onboardPatient: async (patientData: any) => {
    const response = await apiRequest('/onboarding/patient', {
      method: 'POST',
      body: JSON.stringify(patientData),
    });
    if (!response.ok) {
      throw new Error(`Failed to onboard patient: ${response.statusText}`);
    }
    return response.json();
  },

  // Check onboarding status
  checkOnboardingStatus: async (userId: string) => {
    const response = await apiRequest(`/onboarding/status/${userId}`);
    if (!response.ok) {
      throw new Error(`Failed to check onboarding status: ${response.statusText}`);
    }
    return response.json();
  }
};

// Export the main API request function for custom endpoints
export default apiRequest;
