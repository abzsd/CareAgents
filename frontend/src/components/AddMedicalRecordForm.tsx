import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Badge } from "./ui/badge";
import {
  Plus,
  X,
  Upload,
  Loader2,
  ArrowLeft,
  Pill,
  FileText
} from "lucide-react";
import { medicalHistoryService, type Prescription } from "../services/medicalHistoryService";
import { useAuth } from "../contexts/AuthContext";

interface AddMedicalRecordFormProps {
  patientId: string;
  patientName: string;
  onBack: () => void;
  onSuccess: () => void;
}

export function AddMedicalRecordForm({
  patientId,
  patientName,
  onBack,
  onSuccess
}: AddMedicalRecordFormProps) {
  const { userProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadingFile, setUploadingFile] = useState(false);

  // Form state
  const [visitDate, setVisitDate] = useState(new Date().toISOString().split('T')[0]);
  const [diagnosis, setDiagnosis] = useState("");
  const [healthStatus, setHealthStatus] = useState("");
  const [bloodPressure, setBloodPressure] = useState("");
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [symptomInput, setSymptomInput] = useState("");
  const [notes, setNotes] = useState("");
  const [followUpDate, setFollowUpDate] = useState("");

  // Prescriptions
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [showPrescriptionForm, setShowPrescriptionForm] = useState(false);
  const [currentPrescription, setCurrentPrescription] = useState<Prescription>({
    medication_name: "",
    dosage: "",
    frequency: "",
    duration: "",
    instructions: ""
  });

  // File upload
  const [uploadedFiles, setUploadedFiles] = useState<{url: string, name: string}[]>([]);

  const addSymptom = () => {
    if (symptomInput.trim() && !symptoms.includes(symptomInput.trim())) {
      setSymptoms([...symptoms, symptomInput.trim()]);
      setSymptomInput("");
    }
  };

  const removeSymptom = (symptom: string) => {
    setSymptoms(symptoms.filter(s => s !== symptom));
  };

  const addPrescription = () => {
    if (currentPrescription.medication_name && currentPrescription.dosage) {
      setPrescriptions([...prescriptions, currentPrescription]);
      setCurrentPrescription({
        medication_name: "",
        dosage: "",
        frequency: "",
        duration: "",
        instructions: ""
      });
      setShowPrescriptionForm(false);
    }
  };

  const removePrescription = (index: number) => {
    setPrescriptions(prescriptions.filter((_, i) => i !== index));
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploadingFile(true);
      setError(null);

      const result = await medicalHistoryService.uploadFile(file, 'prescriptions');
      setUploadedFiles([...uploadedFiles, { url: result.file_url, name: file.name }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    } finally {
      setUploadingFile(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!diagnosis.trim()) {
      setError('Please provide a diagnosis');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const recordData = {
        patient_id: patientId,
        doctor_id: userProfile?.doctor_id || null,
        doctor_name: userProfile?.display_name || `${userProfile?.first_name || ''} ${userProfile?.last_name || ''}`.trim() || 'Unknown Doctor',
        visit_date: visitDate,
        diagnosis,
        prescriptions: prescriptions.length > 0 ? prescriptions : undefined,
        health_status: healthStatus || undefined,
        blood_pressure: bloodPressure || undefined,
        symptoms: symptoms.length > 0 ? symptoms : undefined,
        notes: notes || undefined,
        follow_up_date: followUpDate || undefined
      };

      await medicalHistoryService.createMedicalHistory(recordData);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create medical record');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add Medical Record</CardTitle>
          <CardDescription>
            Creating medical record for {patientName}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {/* Visit Date */}
            <div>
              <Label htmlFor="visitDate">Visit Date *</Label>
              <Input
                id="visitDate"
                type="date"
                value={visitDate}
                onChange={(e) => setVisitDate(e.target.value)}
                required
              />
            </div>

            {/* Diagnosis */}
            <div>
              <Label htmlFor="diagnosis">Diagnosis *</Label>
              <Textarea
                id="diagnosis"
                placeholder="Enter diagnosis..."
                value={diagnosis}
                onChange={(e) => setDiagnosis(e.target.value)}
                required
                rows={3}
              />
            </div>

            {/* Health Status & Blood Pressure */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="healthStatus">Health Status</Label>
                <Input
                  id="healthStatus"
                  placeholder="e.g., Stable, Critical, Good"
                  value={healthStatus}
                  onChange={(e) => setHealthStatus(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="bloodPressure">Blood Pressure</Label>
                <Input
                  id="bloodPressure"
                  placeholder="e.g., 120/80"
                  value={bloodPressure}
                  onChange={(e) => setBloodPressure(e.target.value)}
                />
              </div>
            </div>

            {/* Symptoms */}
            <div>
              <Label>Symptoms</Label>
              <div className="flex gap-2 mt-2">
                <Input
                  placeholder="Add symptom..."
                  value={symptomInput}
                  onChange={(e) => setSymptomInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSymptom())}
                />
                <Button type="button" onClick={addSymptom} variant="outline">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              {symptoms.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {symptoms.map((symptom) => (
                    <Badge key={symptom} variant="secondary">
                      {symptom}
                      <X
                        className="h-3 w-3 ml-1 cursor-pointer"
                        onClick={() => removeSymptom(symptom)}
                      />
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* Prescriptions */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <Label>Prescriptions</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowPrescriptionForm(!showPrescriptionForm)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Prescription
                </Button>
              </div>

              {showPrescriptionForm && (
                <div className="border rounded-lg p-4 mb-4 bg-slate-50">
                  <div className="space-y-3">
                    <Input
                      placeholder="Medication name *"
                      value={currentPrescription.medication_name}
                      onChange={(e) =>
                        setCurrentPrescription({ ...currentPrescription, medication_name: e.target.value })
                      }
                    />
                    <div className="grid grid-cols-2 gap-3">
                      <Input
                        placeholder="Dosage *"
                        value={currentPrescription.dosage}
                        onChange={(e) =>
                          setCurrentPrescription({ ...currentPrescription, dosage: e.target.value })
                        }
                      />
                      <Input
                        placeholder="Frequency"
                        value={currentPrescription.frequency}
                        onChange={(e) =>
                          setCurrentPrescription({ ...currentPrescription, frequency: e.target.value })
                        }
                      />
                    </div>
                    <Input
                      placeholder="Duration"
                      value={currentPrescription.duration}
                      onChange={(e) =>
                        setCurrentPrescription({ ...currentPrescription, duration: e.target.value })
                      }
                    />
                    <Textarea
                      placeholder="Instructions"
                      value={currentPrescription.instructions}
                      onChange={(e) =>
                        setCurrentPrescription({ ...currentPrescription, instructions: e.target.value })
                      }
                      rows={2}
                    />
                    <div className="flex gap-2">
                      <Button type="button" onClick={addPrescription} size="sm">
                        Add
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowPrescriptionForm(false)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {prescriptions.length > 0 && (
                <div className="space-y-2">
                  {prescriptions.map((prescription, index) => (
                    <div key={index} className="border rounded-lg p-3 bg-white flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <Pill className="h-5 w-5 text-blue-600 mt-0.5" />
                        <div>
                          <h4 className="font-medium">{prescription.medication_name}</h4>
                          <p className="text-sm text-slate-600">
                            {prescription.dosage} - {prescription.frequency}
                          </p>
                        </div>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removePrescription(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* File Upload */}
            <div>
              <Label>Attach Files (Prescriptions, Reports, etc.)</Label>
              <div className="mt-2">
                <label className="flex items-center justify-center border-2 border-dashed rounded-lg p-6 cursor-pointer hover:bg-slate-50 transition-colors">
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleFileUpload}
                    accept="image/*,.pdf,.doc,.docx"
                  />
                  {uploadingFile ? (
                    <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                  ) : (
                    <div className="text-center">
                      <Upload className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                      <p className="text-sm text-slate-600">Click to upload file</p>
                      <p className="text-xs text-slate-400 mt-1">Images, PDF, or documents</p>
                    </div>
                  )}
                </label>
                {uploadedFiles.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="flex items-center gap-2 text-sm text-slate-600">
                        <FileText className="h-4 w-4" />
                        <span>{file.name}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Notes */}
            <div>
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                placeholder="Additional notes..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={4}
              />
            </div>

            {/* Follow-up Date */}
            <div>
              <Label htmlFor="followUpDate">Follow-up Date (Optional)</Label>
              <Input
                id="followUpDate"
                type="date"
                value={followUpDate}
                onChange={(e) => setFollowUpDate(e.target.value)}
              />
            </div>

            {/* Submit Button */}
            <div className="flex gap-3">
              <Button type="submit" disabled={loading} className="flex-1">
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Medical Record'
                )}
              </Button>
              <Button type="button" variant="outline" onClick={onBack}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
