import { useState } from "react";
import { PatientList } from "./PatientList";
import { DashboardHeader } from "./DashboardHeader";
import { DashboardStats } from "./DashboardStats";
import { ChatWidget } from "./ChatWidget";
import { PatientDetailDashboard } from "./PatientDetailDashboard";

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

const mockPatients: Patient[] = [
  {
    id: "1",
    name: "Sarah Johnson",
    age: 45,
    condition: "Cardiac Arrest",
    emergencyRating: "critical",
    admissionTime: "2025-11-17T08:30:00",
    roomNumber: "ER-101",
    vitals: {
      heartRate: 145,
      bloodPressure: "180/110",
      temperature: 38.5,
    },
  },
  {
    id: "2",
    name: "Michael Chen",
    age: 32,
    condition: "Severe Trauma",
    emergencyRating: "critical",
    admissionTime: "2025-11-17T09:15:00",
    roomNumber: "ER-102",
    vitals: {
      heartRate: 130,
      bloodPressure: "90/60",
      temperature: 36.8,
    },
  },
  {
    id: "3",
    name: "Emily Rodriguez",
    age: 28,
    condition: "Acute Asthma Attack",
    emergencyRating: "high",
    admissionTime: "2025-11-17T10:00:00",
    roomNumber: "ER-105",
    vitals: {
      heartRate: 110,
      bloodPressure: "130/85",
      temperature: 37.2,
    },
  },
  {
    id: "4",
    name: "James Wilson",
    age: 67,
    condition: "Stroke Symptoms",
    emergencyRating: "high",
    admissionTime: "2025-11-17T10:45:00",
    roomNumber: "ER-103",
    vitals: {
      heartRate: 95,
      bloodPressure: "160/95",
      temperature: 37.0,
    },
  },
  {
    id: "5",
    name: "Lisa Anderson",
    age: 41,
    condition: "Severe Abdominal Pain",
    emergencyRating: "medium",
    admissionTime: "2025-11-17T11:20:00",
    roomNumber: "ER-106",
    vitals: {
      heartRate: 88,
      bloodPressure: "125/80",
      temperature: 37.8,
    },
  },
  {
    id: "6",
    name: "Robert Martinez",
    age: 55,
    condition: "Chest Pain",
    emergencyRating: "medium",
    admissionTime: "2025-11-17T11:50:00",
    roomNumber: "ER-104",
    vitals: {
      heartRate: 92,
      bloodPressure: "140/88",
      temperature: 36.9,
    },
  },
  {
    id: "7",
    name: "Amanda Taylor",
    age: 34,
    condition: "Minor Laceration",
    emergencyRating: "low",
    admissionTime: "2025-11-17T12:10:00",
    roomNumber: "ER-108",
    vitals: {
      heartRate: 75,
      bloodPressure: "120/75",
      temperature: 36.6,
    },
  },
  {
    id: "8",
    name: "David Brown",
    age: 29,
    condition: "Sprained Ankle",
    emergencyRating: "low",
    admissionTime: "2025-11-17T12:30:00",
    roomNumber: "ER-109",
    vitals: {
      heartRate: 70,
      bloodPressure: "118/72",
      temperature: 36.5,
    },
  },
];

export function PatientDashboard() {
  const [patients] = useState<Patient[]>(mockPatients);
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