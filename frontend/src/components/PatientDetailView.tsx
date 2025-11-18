import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  User,
  Calendar,
  Phone,
  Mail,
  MapPin,
  Activity,
  FileText,
  Pill,
  ArrowLeft,
  Plus,
  Loader2,
  AlertCircle,
  MessageSquare
} from "lucide-react";
import { medicalHistoryService, type MedicalHistory } from "../services/medicalHistoryService";

interface PatientDetailViewProps {
  patient: any;
  onBack: () => void;
  onAddRecord: () => void;
  onOpenChat?: () => void;
}

export function PatientDetailView({ patient, onBack, onAddRecord, onOpenChat }: PatientDetailViewProps) {
  const [medicalHistory, setMedicalHistory] = useState<MedicalHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<MedicalHistory | null>(null);

  useEffect(() => {
    fetchMedicalHistory();
  }, [patient.patient_id]);

  const fetchMedicalHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await medicalHistoryService.getPatientMedicalHistory(patient.patient_id);
      setMedicalHistory(response.records);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load medical history');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Patients
        </Button>
        <div className="flex gap-2">
          {onOpenChat && (
            <Button onClick={onOpenChat} variant="outline" className="bg-blue-50 border-blue-200 hover:bg-blue-100">
              <MessageSquare className="h-4 w-4 mr-2" />
              Chat with AI
            </Button>
          )}
          <Button onClick={onAddRecord}>
            <Plus className="h-4 w-4 mr-2" />
            Add Medical Record
          </Button>
        </div>
      </div>

      {/* Patient Information */}
      <Card>
        <CardHeader>
          <CardTitle>Patient Information</CardTitle>
          <CardDescription>Personal and contact details</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-start gap-6">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="h-10 w-10 text-blue-600" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold">
                {patient.first_name} {patient.last_name}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
                {patient.email && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4 text-slate-400" />
                    <span>{patient.email}</span>
                  </div>
                )}
                {patient.phone && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="h-4 w-4 text-slate-400" />
                    <span>{patient.phone}</span>
                  </div>
                )}
                {patient.date_of_birth && (
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="h-4 w-4 text-slate-400" />
                    <span>DOB: {new Date(patient.date_of_birth).toLocaleDateString()}</span>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap gap-2 mt-4">
                {patient.gender && <Badge variant="secondary">{patient.gender}</Badge>}
                {patient.age && <Badge variant="secondary">Age: {patient.age}</Badge>}
                {patient.blood_type && <Badge variant="secondary">Blood Type: {patient.blood_type}</Badge>}
              </div>

              {patient.address && (
                <div className="mt-4 flex items-start gap-2 text-sm">
                  <MapPin className="h-4 w-4 text-slate-400 mt-0.5" />
                  <span className="text-slate-600">
                    {patient.address.street && `${patient.address.street}, `}
                    {patient.address.city && `${patient.address.city}, `}
                    {patient.address.state && `${patient.address.state} `}
                    {patient.address.zip_code}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Health Info */}
          {(patient.allergies?.length > 0 || patient.chronic_conditions?.length > 0) && (
            <div className="mt-6 pt-6 border-t">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {patient.allergies?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-sm text-slate-700 mb-2">Allergies</h3>
                    <div className="flex flex-wrap gap-2">
                      {patient.allergies.map((allergy: string, index: number) => (
                        <Badge key={index} variant="destructive" className="text-xs">
                          {allergy}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {patient.chronic_conditions?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-sm text-slate-700 mb-2">Chronic Conditions</h3>
                    <div className="flex flex-wrap gap-2">
                      {patient.chronic_conditions.map((condition: string, index: number) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {condition}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Medical History */}
      <Card>
        <CardHeader>
          <CardTitle>Medical History</CardTitle>
          <CardDescription>Past visits and treatments</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-600">{error}</p>
              <Button onClick={fetchMedicalHistory} className="mt-4" variant="outline">
                Retry
              </Button>
            </div>
          ) : medicalHistory.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-500">No medical history records found</p>
              <Button onClick={onAddRecord} className="mt-4" variant="outline">
                Add First Record
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {medicalHistory.map((record) => (
                <div
                  key={record.history_id}
                  className="border rounded-lg p-4 hover:bg-slate-50 cursor-pointer transition-colors"
                  onClick={() => setSelectedRecord(record)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                          <Activity className="h-5 w-5 text-green-600" />
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
                          <p className="text-sm">
                            <span className="font-medium">Diagnosis:</span> {record.diagnosis}
                          </p>
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
                            {record.prescriptions.length} Medication
                            {record.prescriptions.length > 1 ? 's' : ''}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      View
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Detailed Record Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Medical Record Details</h2>
                <Button variant="ghost" onClick={() => setSelectedRecord(null)}>
                  Close
                </Button>
              </div>

              <div className="space-y-6">
                {/* Visit Information */}
                <div>
                  <h3 className="font-semibold text-lg mb-3">Visit Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-slate-500">Doctor</p>
                      <p className="font-medium">{selectedRecord.doctor_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-500">Visit Date</p>
                      <p className="font-medium">
                        {new Date(selectedRecord.visit_date).toLocaleDateString()}
                      </p>
                    </div>
                    {selectedRecord.health_status && (
                      <div>
                        <p className="text-sm text-slate-500">Health Status</p>
                        <p className="font-medium">{selectedRecord.health_status}</p>
                      </div>
                    )}
                    {selectedRecord.blood_pressure && (
                      <div>
                        <p className="text-sm text-slate-500">Blood Pressure</p>
                        <p className="font-medium">{selectedRecord.blood_pressure}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Diagnosis */}
                {selectedRecord.diagnosis && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Diagnosis</h3>
                    <p className="text-slate-700">{selectedRecord.diagnosis}</p>
                  </div>
                )}

                {/* Symptoms */}
                {selectedRecord.symptoms && selectedRecord.symptoms.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Symptoms</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedRecord.symptoms.map((symptom, index) => (
                        <Badge key={index} variant="secondary">
                          {symptom}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Prescriptions */}
                {selectedRecord.prescriptions && selectedRecord.prescriptions.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Prescriptions</h3>
                    <div className="space-y-3">
                      {selectedRecord.prescriptions.map((prescription, index) => (
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
                                  <span className="text-slate-500">Frequency:</span>{' '}
                                  {prescription.frequency}
                                </div>
                                {prescription.duration && (
                                  <div>
                                    <span className="text-slate-500">Duration:</span>{' '}
                                    {prescription.duration}
                                  </div>
                                )}
                              </div>
                              {prescription.instructions && (
                                <p className="mt-2 text-sm text-slate-600">
                                  <span className="font-medium">Instructions:</span>{' '}
                                  {prescription.instructions}
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
                {selectedRecord.notes && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Notes</h3>
                    <p className="text-slate-700">{selectedRecord.notes}</p>
                  </div>
                )}

                {/* Follow-up */}
                {selectedRecord.follow_up_date && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3">Follow-up</h3>
                    <p className="text-slate-700">
                      Scheduled for: {new Date(selectedRecord.follow_up_date).toLocaleDateString()}
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
