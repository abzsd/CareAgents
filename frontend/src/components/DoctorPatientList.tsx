import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import {
  Users,
  Search,
  User,
  Calendar,
  Activity,
  AlertCircle,
  Loader2,
  ChevronRight
} from "lucide-react";
import { medicalHistoryService } from "../services/medicalHistoryService";

interface DoctorPatientListProps {
  doctorId: string;
  onPatientSelect: (patient: any) => void;
}

export function DoctorPatientList({ doctorId, onPatientSelect }: DoctorPatientListProps) {
  const [patients, setPatients] = useState<any[]>([]);
  const [allPatients, setAllPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<'my-patients' | 'all-patients'>('all-patients');

  useEffect(() => {
    fetchPatients();
  }, [doctorId, viewMode]);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      setError(null);

      if (viewMode === 'my-patients') {
        const response = await medicalHistoryService.getDoctorPatients(doctorId);
        setPatients(response.patients);
      } else {
        const response = await medicalHistoryService.getAllPatients();
        setAllPatients(response.patients);
        setPatients(response.patients);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  const filteredPatients = patients.filter(patient => {
    const searchLower = searchQuery.toLowerCase();
    const fullName = `${patient.first_name} ${patient.last_name}`.toLowerCase();
    return fullName.includes(searchLower) ||
           patient.email?.toLowerCase().includes(searchLower) ||
           patient.phone?.includes(searchQuery);
  });

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-600">{error}</p>
            <Button onClick={fetchPatients} className="mt-4" variant="outline">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Patients</CardTitle>
            <CardDescription>
              {viewMode === 'my-patients' ? 'Patients you have treated' : 'All patients in the system'}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'all-patients' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('all-patients')}
            >
              All Patients
            </Button>
            <Button
              variant={viewMode === 'my-patients' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('my-patients')}
            >
              My Patients
            </Button>
          </div>
        </div>

        {/* Search */}
        <div className="relative mt-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            type="text"
            placeholder="Search patients by name, email, or phone..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </CardHeader>

      <CardContent>
        {filteredPatients.length === 0 ? (
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">
              {searchQuery ? 'No patients found matching your search' : 'No patients found'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredPatients.map((patient) => (
              <div
                key={patient.patient_id}
                className="border rounded-lg p-4 hover:bg-slate-50 cursor-pointer transition-colors"
                onClick={() => onPatientSelect(patient)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <User className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-lg">
                        {patient.first_name} {patient.last_name}
                      </h3>
                      <div className="flex items-center gap-3 mt-1 text-sm text-slate-500">
                        {patient.email && (
                          <span>{patient.email}</span>
                        )}
                        {patient.phone && (
                          <span>• {patient.phone}</span>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {patient.gender && (
                          <Badge variant="secondary" className="text-xs">
                            {patient.gender}
                          </Badge>
                        )}
                        {patient.age && (
                          <Badge variant="secondary" className="text-xs">
                            Age: {patient.age}
                          </Badge>
                        )}
                        {patient.blood_type && (
                          <Badge variant="secondary" className="text-xs">
                            {patient.blood_type}
                          </Badge>
                        )}
                        {patient.visit_date && (
                          <Badge variant="outline" className="text-xs">
                            <Calendar className="h-3 w-3 mr-1" />
                            Last visit: {new Date(patient.visit_date).toLocaleDateString()}
                          </Badge>
                        )}
                        {patient.health_status && (
                          <Badge variant="outline" className="text-xs">
                            <Activity className="h-3 w-3 mr-1" />
                            {patient.health_status}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-slate-400" />
                </div>
              </div>
            ))}
          </div>
        )}

        {filteredPatients.length > 0 && (
          <div className="mt-4 text-center text-sm text-slate-500">
            Showing {filteredPatients.length} patient{filteredPatients.length !== 1 ? 's' : ''}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
