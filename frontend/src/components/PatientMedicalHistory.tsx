import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { FileText, Calendar, User, Activity, Pill, AlertCircle, Loader2 } from "lucide-react";
import { medicalHistoryService, type MedicalHistory } from "../services/medicalHistoryService";

interface PatientMedicalHistoryProps {
  patientId: string;
}

export function PatientMedicalHistory({ patientId }: PatientMedicalHistoryProps) {
  const [medicalHistory, setMedicalHistory] = useState<MedicalHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedHistory, setSelectedHistory] = useState<MedicalHistory | null>(null);

  useEffect(() => {
    fetchMedicalHistory();
  }, [patientId]);

  const fetchMedicalHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await medicalHistoryService.getPatientMedicalHistory(patientId);
      setMedicalHistory(response.records);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load medical history');
    } finally {
      setLoading(false);
    }
  };

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
            <Button onClick={fetchMedicalHistory} className="mt-4" variant="outline">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (medicalHistory.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Medical History</CardTitle>
          <CardDescription>Your complete medical records</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No medical history records found</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Medical History</CardTitle>
          <CardDescription>Your complete medical records</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {medicalHistory.map((record) => (
              <div
                key={record.history_id}
                className="border rounded-lg p-4 hover:bg-slate-50 cursor-pointer transition-colors"
                onClick={() => setSelectedHistory(record)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-medium">{record.doctor_name}</h3>
                        <p className="text-sm text-slate-500">
                          <Calendar className="inline h-3 w-3 mr-1" />
                          {new Date(record.visit_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    {record.diagnosis && (
                      <div className="mt-2 pl-13">
                        <p className="text-sm"><span className="font-medium">Diagnosis:</span> {record.diagnosis}</p>
                      </div>
                    )}

                    <div className="flex flex-wrap gap-2 mt-3 pl-13">
                      {record.health_status && (
                        <Badge variant="outline" className="text-xs">
                          <Activity className="h-3 w-3 mr-1" />
                          {record.health_status}
                        </Badge>
                      )}
                      {record.blood_pressure && (
                        <Badge variant="outline" className="text-xs">
                          BP: {record.blood_pressure}
                        </Badge>
                      )}
                      {record.prescriptions && record.prescriptions.length > 0 && (
                        <Badge variant="outline" className="text-xs">
                          <Pill className="h-3 w-3 mr-1" />
                          {record.prescriptions.length} Medication{record.prescriptions.length > 1 ? 's' : ''}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">View Details</Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Detailed View Modal */}
      {selectedHistory && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Medical Record Details</h2>
                <Button variant="ghost" onClick={() => setSelectedHistory(null)}>
                  Close
                </Button>
              </div>

              <div className="space-y-6">
                {/* Doctor and Visit Info */}
                <div>
                  <h3 className="font-semibold text-lg mb-3">Visit Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-slate-500">Doctor</p>
                      <p className="font-medium">{selectedHistory.doctor_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-500">Visit Date</p>
                      <p className="font-medium">{new Date(selectedHistory.visit_date).toLocaleDateString()}</p>
                    </div>
                    {selectedHistory.health_status && (
                      <div>
                        <p className="text-sm text-slate-500">Health Status</p>
                        <p className="font-medium">{selectedHistory.health_status}</p>
                      </div>
                    )}
                    {selectedHistory.blood_pressure && (
                      <div>
                        <p className="text-sm text-slate-500">Blood Pressure</p>
                        <p className="font-medium">{selectedHistory.blood_pressure}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Diagnosis */}
                {selectedHistory.diagnosis && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Diagnosis</h3>
                    <p className="text-slate-700">{selectedHistory.diagnosis}</p>
                  </div>
                )}

                {/* Symptoms */}
                {selectedHistory.symptoms && selectedHistory.symptoms.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Symptoms</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedHistory.symptoms.map((symptom, index) => (
                        <Badge key={index} variant="secondary">
                          {symptom}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Prescriptions */}
                {selectedHistory.prescriptions && selectedHistory.prescriptions.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Prescriptions</h3>
                    <div className="space-y-3">
                      {selectedHistory.prescriptions.map((prescription, index) => (
                        <div key={index} className="border rounded-lg p-4 bg-slate-50">
                          <div className="flex items-start gap-3">
                            <Pill className="h-5 w-5 text-blue-600 mt-1" />
                            <div className="flex-1">
                              <h4 className="font-medium">{prescription.medication_name}</h4>
                              <div className="mt-2 grid grid-cols-2 gap-2 text-sm">
                                <div>
                                  <span className="text-slate-500">Dosage:</span> {prescription.dosage}
                                </div>
                                <div>
                                  <span className="text-slate-500">Frequency:</span> {prescription.frequency}
                                </div>
                                {prescription.duration && (
                                  <div>
                                    <span className="text-slate-500">Duration:</span> {prescription.duration}
                                  </div>
                                )}
                              </div>
                              {prescription.instructions && (
                                <p className="mt-2 text-sm text-slate-600">
                                  <span className="font-medium">Instructions:</span> {prescription.instructions}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Notes */}
                {selectedHistory.notes && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Notes</h3>
                    <p className="text-slate-700">{selectedHistory.notes}</p>
                  </div>
                )}

                {/* Follow-up */}
                {selectedHistory.follow_up_date && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Follow-up</h3>
                    <p className="text-slate-700">
                      Scheduled for: {new Date(selectedHistory.follow_up_date).toLocaleDateString()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
