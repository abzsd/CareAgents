import { AlertCircle, TrendingUp, Users, Clock } from "lucide-react";
import { Card, CardContent } from "./ui/card";
import type { Patient } from "./PatientDashboard";

interface DashboardStatsProps {
  patients: Patient[];
}

export function DashboardStats({ patients }: DashboardStatsProps) {
  const criticalCount = patients.filter(p => p.emergencyRating === "critical").length;
  const highCount = patients.filter(p => p.emergencyRating === "high").length;
  const totalCount = patients.length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600">Total Patients</p>
              <p className="text-slate-900">{totalCount}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600">Critical Cases</p>
              <p className="text-red-600">{criticalCount}</p>
            </div>
            <div className="bg-red-100 p-3 rounded-lg">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600">High Priority</p>
              <p className="text-orange-600">{highCount}</p>
            </div>
            <div className="bg-orange-100 p-3 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-600">Avg Wait Time</p>
              <p className="text-slate-900">12 min</p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <Clock className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
