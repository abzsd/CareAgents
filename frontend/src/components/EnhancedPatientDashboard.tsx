import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Calendar, Clock, User, Stethoscope, MessageCircle, FileText, Activity } from "lucide-react";
import { PatientMedicalHistory } from "./PatientMedicalHistory";
import { SmartAppointmentBooking } from "./SmartAppointmentBooking";
import { patientService } from "../services/patientService";

export function EnhancedPatientDashboard() {
  const { user, userProfile } = useAuth();
  const [showChat, setShowChat] = useState(false);
  const [showBooking, setShowBooking] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'history'>('overview');
  const [patientId, setPatientId] = useState<string | null>(null);

  useEffect(() => {
    // Fetch patient data to get patient_id
    const loadPatientData = async () => {
      if (userProfile?.user_id) {
        try {
          const patient = await patientService.getPatientByUserId(userProfile.user_id);
          setPatientId(patient.patient_id || '');
        } catch (err) {
          console.error('Failed to load patient data:', err);
          // Fallback to user_id if patient record doesn't exist yet
          setPatientId(userProfile.user_id);
        }
      }
    };

    loadPatientData();
  }, [userProfile]);

  if (!user || !userProfile || !patientId) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">
                Welcome, {userProfile.display_name || user.displayName}
              </h1>
              <p className="text-slate-600">Manage your appointments and health records</p>
            </div>
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
              {userProfile.display_name?.charAt(0) || user.displayName?.charAt(0) || 'U'}
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex gap-4 mt-6 border-b">
            <button
              onClick={() => setActiveTab('overview')}
              className={`pb-3 px-4 font-medium transition-colors ${
                activeTab === 'overview'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Activity className="inline h-4 w-4 mr-2" />
              Overview
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`pb-3 px-4 font-medium transition-colors ${
                activeTab === 'history'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileText className="inline h-4 w-4 mr-2" />
              Medical History
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {activeTab === 'overview' ? (
          <>
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Next Appointment</CardTitle>
                  <Calendar className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">-</div>
                  <p className="text-xs text-slate-500">No upcoming appointments</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Medical Records</CardTitle>
                  <FileText className="h-4 w-4 text-green-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">-</div>
                  <p className="text-xs text-slate-500">View all records</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Health Status</CardTitle>
                  <Activity className="h-4 w-4 text-orange-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">Good</div>
                  <p className="text-xs text-slate-500">Overall health</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Last Visit</CardTitle>
                  <Clock className="h-4 w-4 text-purple-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">-</div>
                  <p className="text-xs text-slate-500">No visits yet</p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                  <CardDescription>Common tasks</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => setActiveTab('history')}
                  >
                    <FileText className="mr-2 h-4 w-4" />
                    View Medical History
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => setShowBooking(true)}
                  >
                    <Calendar className="mr-2 h-4 w-4" />
                    Schedule Appointment
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => setShowBooking(true)}
                  >
                    <Stethoscope className="mr-2 h-4 w-4" />
                    Find a Doctor
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Health Tips</CardTitle>
                  <CardDescription>Stay healthy</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-900 font-medium">Stay Hydrated</p>
                      <p className="text-xs text-blue-700 mt-1">Drink at least 8 glasses of water daily</p>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg">
                      <p className="text-sm text-green-900 font-medium">Regular Exercise</p>
                      <p className="text-xs text-green-700 mt-1">Aim for 30 minutes of activity daily</p>
                    </div>
                    <div className="p-3 bg-purple-50 rounded-lg">
                      <p className="text-sm text-purple-900 font-medium">Healthy Diet</p>
                      <p className="text-xs text-purple-700 mt-1">Include fruits and vegetables in meals</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        ) : (
          <PatientMedicalHistory patientId={patientId} />
        )}
      </div>

      {/* Chat Button - Fixed at bottom center */}
      <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2">
        <Button
          onClick={() => setShowChat(!showChat)}
          className="h-14 w-14 rounded-full shadow-lg bg-blue-600 hover:bg-blue-700 flex items-center justify-center"
          size="icon"
        >
          <MessageCircle className="w-6 h-6" />
        </Button>
      </div>

      {/* Chat Widget */}
      {showChat && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowChat(false)}></div>
          <div className="absolute bottom-0 left-0 right-0 h-3/4 bg-white rounded-t-2xl shadow-2xl">
            <div className="bg-blue-600 text-white p-4 rounded-t-2xl flex items-center justify-between">
              <h3 className="font-medium">Medical Assistant</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowChat(false)}
                className="text-white hover:bg-blue-700"
              >
                Close
              </Button>
            </div>

            <div className="h-full flex">
              <div className="w-64 bg-slate-100 border-r p-4">
                <h4 className="font-medium mb-4">Chat Options</h4>
                <div className="space-y-2">
                  <Button variant="ghost" className="w-full justify-start">
                    <MessageCircle className="w-4 h-4 mr-2" />
                    New Chat
                  </Button>
                  <Button variant="ghost" className="w-full justify-start">
                    <User className="w-4 h-4 mr-2" />
                    My Health Records
                  </Button>
                  <Button variant="ghost" className="w-full justify-start">
                    <Stethoscope className="w-4 h-4 mr-2" />
                    Appointment History
                  </Button>
                </div>
              </div>

              <div className="flex-1 flex items-center justify-center">
                <div className="text-center text-slate-500">
                  <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Start a conversation with your medical assistant</p>
                  <p className="text-sm mt-2">Ask questions about your health, appointments, or medications</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Smart Appointment Booking Modal */}
      {showBooking && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setShowBooking(false)}></div>
            <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between z-10">
                <h2 className="text-xl font-semibold">Book an Appointment</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowBooking(false)}
                >
                  Close
                </Button>
              </div>
              <div className="p-6">
                <SmartAppointmentBooking
                  patientId={patientId}
                  onSuccess={() => {
                    setShowBooking(false);
                    // Optionally refresh appointments list
                  }}
                  onCancel={() => setShowBooking(false)}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
