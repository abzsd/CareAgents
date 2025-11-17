import { useState, useEffect } from "react";
import { PatientList } from "./PatientList";
import { DashboardHeader } from "./DashboardHeader";
import { DashboardStats } from "./DashboardStats";
import { ChatWidget } from "./ChatWidget";
import { PatientDetailDashboard } from "./PatientDetailDashboard";
import { patientApi } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

export type EmergencyLevel = "critical" | "high" | "medium" | "low";

export interface Patient {
  id: string;
  name: string;
  age: number;
  condition: string;
  emergencyRating: EmergencyLevel;
  admissionTime: string;
  roomNumber: string;
  vitals: {
    heartRate: number;
    bloodPressure: string;
    temperature: number;
  };
}

export function PatientDashboard() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    const fetchPatients = async () => {
      if (!user) return;
      
      try {
        setLoading(true);
        const response = await patientApi.getPatients(1, 100, true);
        // Assuming the response has a 'patients' array or similar structure
        // You may need to adjust this based on your actual API response format
        const patientsData = response.patients || response.data || response;
        setPatients(Array.isArray(patientsData) ? patientsData : []);
      } catch (err: any) {
        console.error('Error fetching patients:', err);
        setError(err.message || 'Failed to fetch patients');
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, [user]);
  const [filterLevel, setFilterLevel] = useState<EmergencyLevel | "all">("all");
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);

  const filteredPatients = filterLevel === "all" 
    ? patients 
    : patients.filter(p => p.emergencyRating === filterLevel);

  // Sort by emergency rating priority
  const sortedPatients = [...filteredPatients].sort((a, b) => {
    const priority: Record<EmergencyLevel, number> = {
      critical: 0,
      high: 1,
      medium: 2,
      low: 3,
    };
    return priority[a.emergencyRating] - priority[b.emergencyRating];
  });

  // Show patient detail view if a patient is selected
  if (selectedPatient) {
    return (
      <PatientDetailDashboard 
        patient={selectedPatient} 
        onBack={() => setSelectedPatient(null)} 
      />
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading patients...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center p-6">
          <div className="text-red-500 text-xl font-semibold">Error</div>
          <p className="mt-2 text-slate-600">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <DashboardHeader />
      <div className="container mx-auto p-6 space-y-6">
        <DashboardStats patients={patients} />
        <PatientList 
          patients={sortedPatients} 
          filterLevel={filterLevel}
          onFilterChange={setFilterLevel}
          onPatientClick={setSelectedPatient}
        />
      </div>
      <ChatWidget />
    </div>
  );
}
