import { Activity, Clock, MapPin } from "lucide-react";
import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";
import type { Patient, EmergencyLevel } from "./PatientDashboard";

interface PatientCardProps {
  patient: Patient;
  onClick: () => void;
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

export function PatientCard({ patient, onClick }: PatientCardProps) {
  const config = emergencyConfig[patient.emergencyRating];
  const admissionTime = new Date(patient.admissionTime);
  const timeAgo = getTimeAgo(admissionTime);

  return (
    <Card 
      className={`border-l-4 ${config.bgColor.split(" ")[1]} cursor-pointer hover:shadow-md transition-shadow`}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-slate-900">{patient.name}</h3>
              <Badge className={`${config.bgColor} ${config.color} border`}>
                {config.label}
              </Badge>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
              <div>
                <p className="text-slate-600">Age: {patient.age} years</p>
                <p className="text-slate-600">Condition: {patient.condition}</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1 text-slate-600">
                  <MapPin className="w-4 h-4" />
                  <span>{patient.roomNumber}</span>
                </div>
                <div className="flex items-center gap-1 text-slate-600">
                  <Clock className="w-4 h-4" />
                  <span>{timeAgo}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-6 p-3 bg-slate-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-slate-600" />
                <span className="text-slate-600">HR:</span>
                <span className="text-slate-900">{patient.vitals.heartRate} bpm</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-600">BP:</span>
                <span className="text-slate-900">{patient.vitals.bloodPressure}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-600">Temp:</span>
                <span className="text-slate-900">{patient.vitals.temperature}°C</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function getTimeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);

  if (diffHours > 0) {
    return `${diffHours}h ${diffMins % 60}m ago`;
  }
  return `${diffMins}m ago`;
}