import { ArrowLeft, Calendar, FileText, Activity, Pill, AlertCircle } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { PatientChat } from "./PatientChat";
import type { Patient, EmergencyLevel } from "./PatientDashboard";
import { ClipboardList, Stethoscope } from "lucide-react";

interface PatientDetailDashboardProps {
  patient: Patient;
  onBack: () => void;
}

const emergencyConfig: Record<EmergencyLevel, { color: string; bgColor: string; label: string }> = {
  critical: {
    color: "text-red-700",
    bgColor: "bg-red-100 border-red-300",
    label: "CRITICAL",
  },
  high: {
    color: "text-orange-700",
    bgColor: "bg-orange-100 border-orange-300",
    label: "HIGH",
  },
  medium: {
    color: "text-yellow-700",
    bgColor: "bg-yellow-100 border-yellow-300",
    label: "MEDIUM",
  },
  low: {
    color: "text-green-700",
    bgColor: "bg-green-100 border-green-300",
    label: "LOW",
  },
};

export function PatientDetailDashboard({ patient, onBack }: PatientDetailDashboardProps) {
  const config = emergencyConfig[patient.emergencyRating];

  // Mock medical history data
  const medicalHistory = {
    allergies: ["Penicillin", "Sulfa drugs"],
    chronicConditions: ["Type 2 Diabetes", "Hypertension"],
    currentMedications: [
      { name: "Metformin", dosage: "500mg", frequency: "Twice daily" },
      { name: "Lisinopril", dosage: "10mg", frequency: "Once daily" },
      { name: "Aspirin", dosage: "81mg", frequency: "Once daily" },
    ],
    recentVisits: [
      { date: "2025-10-15", reason: "Annual checkup", doctor: "Dr. Johnson" },
      { date: "2025-08-22", reason: "Blood pressure check", doctor: "Dr. Smith" },
      { date: "2025-06-10", reason: "Diabetes management", doctor: "Dr. Johnson" },
    ],
    labResults: [
      { test: "Blood Glucose", value: "145 mg/dL", date: "2025-11-10", status: "High" },
      { test: "HbA1c", value: "7.2%", date: "2025-11-10", status: "Elevated" },
      { test: "Blood Pressure", value: "140/90", date: "2025-11-17", status: "High" },
    ],
    notes: [
      { date: "2025-11-17", note: "Patient admitted with acute symptoms. Monitoring vitals closely.", author: "Dr. Smith" },
      { date: "2025-10-15", note: "Patient managing diabetes well. Continue current medication regimen.", author: "Dr. Johnson" },
    ],
  };

  // Mock prescriptions data
  const prescriptions = [
    { 
      medication: "Nitroglycerin", 
      dosage: "0.4mg", 
      frequency: "As needed for chest pain", 
      duration: "30 days",
      prescribedBy: "Dr. Smith",
      date: "2025-11-17",
      instructions: "Place under tongue when chest pain occurs. May repeat every 5 minutes up to 3 doses."
    },
    { 
      medication: "Atorvastatin", 
      dosage: "20mg", 
      frequency: "Once daily at bedtime", 
      duration: "90 days",
      prescribedBy: "Dr. Smith",
      date: "2025-11-17",
      instructions: "Take with or without food. Avoid grapefruit juice."
    },
    { 
      medication: "Clopidogrel", 
      dosage: "75mg", 
      frequency: "Once daily", 
      duration: "90 days",
      prescribedBy: "Dr. Smith",
      date: "2025-11-17",
      instructions: "Take at the same time each day with food."
    },
  ];

  // Mock department diagnosis data
  const departmentDiagnosis = [
    {
      department: "Cardiology",
      doctor: "Dr. Robert Chen",
      date: "2025-11-17",
      diagnosis: "Acute Coronary Syndrome",
      findings: "ECG shows ST-segment elevation. Troponin levels elevated at 2.5 ng/mL. Recommended immediate cardiac catheterization.",
      status: "Urgent",
      color: "border-red-500"
    },
    {
      department: "Radiology",
      doctor: "Dr. Emily Watson",
      date: "2025-11-17",
      diagnosis: "Chest X-Ray Analysis",
      findings: "Mild cardiomegaly noted. No signs of pulmonary edema or pneumothorax. Clear lung fields bilaterally.",
      status: "Completed",
      color: "border-blue-500"
    },
    {
      department: "Laboratory",
      doctor: "Dr. Michael Torres",
      date: "2025-11-17",
      diagnosis: "Blood Work Panel",
      findings: "Elevated cardiac enzymes. HbA1c at 7.2% indicating suboptimal diabetes control. Lipid panel shows high LDL at 165 mg/dL.",
      status: "Completed",
      color: "border-purple-500"
    },
    {
      department: "Endocrinology",
      doctor: "Dr. Sarah Johnson",
      date: "2025-11-16",
      diagnosis: "Diabetes Management Review",
      findings: "Patient's diabetes control needs improvement. Recommend adjusting Metformin dosage and adding SGLT2 inhibitor. Diet and exercise counseling provided.",
      status: "Follow-up Required",
      color: "border-yellow-500"
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 pb-16">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto p-6">
          <div className="flex items-center gap-4 mb-4">
            <Button variant="ghost" size="icon" onClick={onBack}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h1>{patient.name}</h1>
                <Badge className={`${config.bgColor} ${config.color} border`}>
                  {config.label}
                </Badge>
              </div>
              <p className="text-slate-600">
                {patient.age} years • {patient.condition} • Room {patient.roomNumber}
              </p>
            </div>
          </div>

          {/* Current Vitals */}
          <div className="flex items-center gap-6 p-4 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-slate-600" />
              <span className="text-slate-600">Heart Rate:</span>
              <span className="text-slate-900">{patient.vitals.heartRate} bpm</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-600">Blood Pressure:</span>
              <span className="text-slate-900">{patient.vitals.bloodPressure}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-600">Temperature:</span>
              <span className="text-slate-900">{patient.vitals.temperature}°C</span>
            </div>
          </div>
        </div>
      </div>

      {/* Medical History Content */}
      <div className="container mx-auto p-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Allergies & Chronic Conditions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                Allergies & Conditions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-slate-600 mb-2">Allergies</p>
                <div className="flex flex-wrap gap-2">
                  {medicalHistory.allergies.map((allergy, index) => (
                    <Badge key={index} variant="destructive">
                      {allergy}
                    </Badge>
                  ))}
                </div>
              </div>
              <Separator />
              <div>
                <p className="text-slate-600 mb-2">Chronic Conditions</p>
                <div className="flex flex-wrap gap-2">
                  {medicalHistory.chronicConditions.map((condition, index) => (
                    <Badge key={index} variant="secondary">
                      {condition}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Current Medications */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Pill className="w-5 h-5 text-blue-600" />
                Current Medications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {medicalHistory.currentMedications.map((med, index) => (
                  <div key={index} className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-slate-900">{med.name}</p>
                    <p className="text-slate-600">
                      {med.dosage} - {med.frequency}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Lab Results */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-purple-600" />
                Recent Lab Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {medicalHistory.labResults.map((lab, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                    <div>
                      <p className="text-slate-900">{lab.test}</p>
                      <p className="text-slate-600">{lab.date}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-slate-900">{lab.value}</p>
                      <Badge variant={lab.status === "High" || lab.status === "Elevated" ? "destructive" : "secondary"}>
                        {lab.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Visits */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-green-600" />
                Recent Visits
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {medicalHistory.recentVisits.map((visit, index) => (
                  <div key={index} className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-slate-900">{visit.reason}</p>
                    <p className="text-slate-600">
                      {visit.date} • {visit.doctor}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Medical Notes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-slate-600" />
              Medical Notes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {medicalHistory.notes.map((note, index) => (
                <div key={index} className="p-4 border-l-4 border-blue-500 bg-slate-50 rounded">
                  <div className="flex justify-between items-start mb-2">
                    <p className="text-slate-600">{note.date}</p>
                    <p className="text-slate-600">{note.author}</p>
                  </div>
                  <p className="text-slate-900">{note.note}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Current Prescriptions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ClipboardList className="w-5 h-5 text-blue-600" />
              Current Prescriptions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {prescriptions.map((prescription, index) => (
                <div key={index} className="p-4 border border-slate-200 rounded-lg bg-white">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="text-slate-900">{prescription.medication}</h4>
                      <p className="text-slate-600">{prescription.dosage} - {prescription.frequency}</p>
                    </div>
                    <Badge variant="outline" className="bg-blue-50">
                      {prescription.duration}
                    </Badge>
                  </div>
                  <Separator className="my-2" />
                  <div className="space-y-1">
                    <p className="text-slate-600">
                      <span className="text-slate-900">Instructions:</span> {prescription.instructions}
                    </p>
                    <p className="text-slate-500 text-xs">
                      Prescribed by {prescription.prescribedBy} on {prescription.date}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Department Diagnosis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Stethoscope className="w-5 h-5 text-green-600" />
              Department Consultations & Diagnosis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {departmentDiagnosis.map((dept, index) => (
                <div key={index} className={`p-4 border-l-4 ${dept.color} bg-slate-50 rounded`}>
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="text-slate-900">{dept.department}</h4>
                      <p className="text-slate-600">{dept.doctor}</p>
                    </div>
                    <div className="text-right">
                      <Badge 
                        variant={dept.status === "Urgent" ? "destructive" : dept.status === "Completed" ? "secondary" : "outline"}
                        className={dept.status === "Follow-up Required" ? "bg-yellow-100 text-yellow-800" : ""}
                      >
                        {dept.status}
                      </Badge>
                      <p className="text-slate-500 text-xs mt-1">{dept.date}</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <span className="text-slate-900">Diagnosis: </span>
                      <span className="text-slate-700">{dept.diagnosis}</span>
                    </div>
                    <div>
                      <span className="text-slate-900">Findings: </span>
                      <span className="text-slate-600">{dept.findings}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Patient Chat at Bottom */}
      <PatientChat patient={patient} />
    </div>
  );
}