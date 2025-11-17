import { PatientCard } from "./PatientCard";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import type { Patient, EmergencyLevel } from "./PatientDashboard";

interface PatientListProps {
  patients: Patient[];
  filterLevel: EmergencyLevel | "all";
  onFilterChange: (level: EmergencyLevel | "all") => void;
  onPatientClick: (patient: Patient) => void;
}

export function PatientList({ patients, filterLevel, onFilterChange, onPatientClick }: PatientListProps) {
  const filters: { label: string; value: EmergencyLevel | "all"; color: string }[] = [
    { label: "All", value: "all", color: "bg-slate-200 text-slate-900 hover:bg-slate-300" },
    { label: "Critical", value: "critical", color: "bg-red-100 text-red-700 hover:bg-red-200" },
    { label: "High", value: "high", color: "bg-orange-100 text-orange-700 hover:bg-orange-200" },
    { label: "Medium", value: "medium", color: "bg-yellow-100 text-yellow-700 hover:bg-yellow-200" },
    { label: "Low", value: "low", color: "bg-green-100 text-green-700 hover:bg-green-200" },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Patient Queue</CardTitle>
          <div className="flex gap-2">
            {filters.map((filter) => (
              <Button
                key={filter.value}
                variant={filterLevel === filter.value ? "default" : "outline"}
                size="sm"
                onClick={() => onFilterChange(filter.value)}
                className={filterLevel === filter.value ? "" : filter.color}
              >
                {filter.label}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {patients.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              No patients in this category
            </div>
          ) : (
            patients.map((patient) => (
              <PatientCard key={patient.id} patient={patient} onClick={() => onPatientClick(patient)} />
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}