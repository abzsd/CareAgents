import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Badge } from "./ui/badge";
import {
  Brain,
  Calendar,
  Clock,
  User,
  Stethoscope,
  Loader2,
  CheckCircle,
  XCircle,
  ArrowRight,
  ArrowLeft,
  Star,
  Sparkles
} from "lucide-react";
import { aiAppointmentService, type SmartBookingResponse, type AppointmentSlot } from "../services/aiAppointmentService";
import { appointmentService } from "../services/appointmentService";

interface SmartAppointmentBookingProps {
  patientId: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function SmartAppointmentBooking({ patientId, onSuccess, onCancel }: SmartAppointmentBookingProps) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Step 1: Patient input
  const [reason, setReason] = useState("");
  const [symptomInput, setSymptomInput] = useState("");
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [timePreference, setTimePreference] = useState<string>("flexible");

  // Step 2: AI results
  const [aiResults, setAiResults] = useState<SmartBookingResponse | null>(null);

  // Step 3: Selected slot
  const [selectedSlot, setSelectedSlot] = useState<AppointmentSlot | null>(null);

  // Step 4: Booking confirmation
  const [bookedAppointment, setBookedAppointment] = useState<any>(null);

  const addSymptom = () => {
    if (symptomInput.trim() && !symptoms.includes(symptomInput.trim())) {
      setSymptoms([...symptoms, symptomInput.trim()]);
      setSymptomInput("");
    }
  };

  const removeSymptom = (symptom: string) => {
    setSymptoms(symptoms.filter(s => s !== symptom));
  };

  const handleSmartBooking = async () => {
    if (!reason.trim()) {
      setError("Please describe your reason for consultation");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await aiAppointmentService.bookSmart({
        patient_id: patientId,
        reason,
        symptoms: symptoms.length > 0 ? symptoms : undefined,
        patient_preference: timePreference !== 'flexible' ? timePreference : undefined
      });

      setAiResults(result);
      setStep(2);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process booking');
    } finally {
      setLoading(false);
    }
  };

  const handleSlotSelection = (slot: AppointmentSlot) => {
    setSelectedSlot(slot);
    setStep(3);
  };

  const confirmBooking = async () => {
    if (!aiResults || !selectedSlot) return;

    try {
      setLoading(true);
      setError(null);

      const appointment = await appointmentService.createAppointment({
        patient_id: patientId,
        doctor_id: aiResults.doctor_match.recommended_doctor_id,
        appointment_date: selectedSlot.date,
        appointment_time: selectedSlot.time,
        appointment_type: 'consultation',
        reason,
        notes: `AI-matched booking. Urgency: ${aiResults.analysis.urgency_level}. ${aiResults.analysis.pre_appointment_notes}`
      });

      setBookedAppointment(appointment);
      setStep(4);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to book appointment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center justify-center gap-2">
        {[1, 2, 3, 4].map((s) => (
          <div key={s} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step >= s
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-500'
              }`}
            >
              {s}
            </div>
            {s < 4 && (
              <div className={`w-12 h-1 ${step > s ? 'bg-blue-600' : 'bg-gray-200'}`} />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Describe Symptoms */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-600" />
              AI-Powered Appointment Booking
            </CardTitle>
            <CardDescription>
              Tell us about your health concern, and our AI will match you with the best doctor
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            <div>
              <Label htmlFor="reason">What brings you in today? *</Label>
              <Textarea
                id="reason"
                placeholder="Describe your symptoms or reason for consultation..."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={4}
                className="mt-2"
              />
            </div>

            <div>
              <Label>Any specific symptoms?</Label>
              <div className="flex gap-2 mt-2">
                <Input
                  placeholder="Add symptom (e.g., headache, fever)"
                  value={symptomInput}
                  onChange={(e) => setSymptomInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSymptom())}
                />
                <Button type="button" onClick={addSymptom} variant="outline">
                  Add
                </Button>
              </div>
              {symptoms.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {symptoms.map((symptom) => (
                    <Badge key={symptom} variant="secondary" className="cursor-pointer">
                      {symptom}
                      <XCircle
                        className="h-3 w-3 ml-1"
                        onClick={() => removeSymptom(symptom)}
                      />
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            <div>
              <Label>Preferred time of day</Label>
              <div className="grid grid-cols-4 gap-2 mt-2">
                {['flexible', 'morning', 'afternoon', 'evening'].map((pref) => (
                  <Button
                    key={pref}
                    variant={timePreference === pref ? 'default' : 'outline'}
                    onClick={() => setTimePreference(pref)}
                    className="capitalize"
                  >
                    {pref}
                  </Button>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <Button
                onClick={handleSmartBooking}
                disabled={loading}
                className="flex-1"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Finding best doctor...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4 mr-2" />
                    Find Best Doctor with AI
                  </>
                )}
              </Button>
              {onCancel && (
                <Button variant="outline" onClick={onCancel}>
                  Cancel
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: AI Doctor Match */}
      {step === 2 && aiResults && (
        <div className="space-y-4">
          {/* Analysis */}
          <Card className="border-blue-200 bg-blue-50">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Brain className="h-5 w-5 text-blue-600" />
                AI Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Urgency Level</p>
                  <Badge variant={
                    aiResults.analysis.urgency_level === 'emergency' ? 'destructive' :
                    aiResults.analysis.urgency_level === 'urgent' ? 'default' : 'secondary'
                  } className="mt-1 capitalize">
                    {aiResults.analysis.urgency_level}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Recommended Specialization</p>
                  <p className="font-medium">{aiResults.analysis.recommended_specialization}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600">AI Reasoning</p>
                <p className="text-sm mt-1">{aiResults.analysis.reasoning}</p>
              </div>
            </CardContent>
          </Card>

          {/* Doctor Match */}
          <Card className="border-green-200">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Stethoscope className="h-5 w-5 text-green-600" />
                  Recommended Doctor
                </span>
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm font-normal">
                    {aiResults.doctor_match.confidence_score}% match
                  </span>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="text-xl font-semibold">{aiResults.doctor_match.doctor_name}</h3>
                <p className="text-gray-600">{aiResults.doctor_match.specialization}</p>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm font-medium text-green-900 mb-2">Why this doctor?</p>
                <p className="text-sm text-green-800">{aiResults.doctor_match.reasoning}</p>
              </div>

              <Button onClick={() => setStep(3)} className="w-full">
                <Calendar className="h-4 w-4 mr-2" />
                View Available Times
              </Button>
            </CardContent>
          </Card>

          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setStep(1)}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </div>
        </div>
      )}

      {/* Step 3: Select Time Slot */}
      {step === 3 && aiResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              Select Appointment Time
            </CardTitle>
            <CardDescription>
              AI-suggested optimal times for you with {aiResults.doctor_match.doctor_name}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              {aiResults.suggested_slots.suggested_slots.map((slot, index) => (
                <div
                  key={index}
                  onClick={() => handleSlotSelection(slot)}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    selectedSlot === slot
                      ? 'border-blue-500 bg-blue-50'
                      : 'hover:border-blue-300 hover:bg-blue-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Calendar className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="font-medium">
                          {new Date(slot.date).toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric'
                          })}
                        </p>
                        <p className="text-sm text-gray-600">
                          {new Date(`2000-01-01T${slot.time}`).toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className="capitalize">
                        {slot.time_of_day}
                      </Badge>
                      {index === 0 && (
                        <p className="text-xs text-green-600 mt-1">Recommended</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-gray-50 border rounded-lg p-4">
              <p className="text-sm text-gray-700">
                <strong>Note:</strong> {aiResults.suggested_slots.notes}
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setStep(2)}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <Button
                onClick={confirmBooking}
                disabled={!selectedSlot || loading}
                className="flex-1"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Booking...
                  </>
                ) : (
                  <>
                    Confirm Booking
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 4: Confirmation */}
      {step === 4 && bookedAppointment && aiResults && (
        <Card className="border-green-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-700">
              <CheckCircle className="h-6 w-6" />
              Appointment Request Sent!
            </CardTitle>
            <CardDescription>
              Your appointment is pending doctor confirmation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Doctor</p>
                  <p className="font-medium">{aiResults.doctor_match.doctor_name}</p>
                  <p className="text-sm text-gray-600">{aiResults.doctor_match.specialization}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Date & Time</p>
                  <p className="font-medium">
                    {new Date(bookedAppointment.appointment_date).toLocaleDateString()}
                  </p>
                  <p className="text-sm text-gray-600">
                    {new Date(`2000-01-01T${bookedAppointment.appointment_time}`).toLocaleTimeString('en-US', {
                      hour: 'numeric',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-600">Reason</p>
                <p className="text-sm">{bookedAppointment.reason}</p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge variant="secondary">Pending Confirmation</Badge>
              </div>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-600 mb-4">
                You'll receive a notification once the doctor confirms your appointment
              </p>
              <Button onClick={onSuccess} className="w-full">
                View My Appointments
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
