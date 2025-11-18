import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Calendar, Clock, User, Stethoscope, MessageCircle, Mic } from "lucide-react";
import { ChatWidget } from "./ChatWidget";
import { VoiceChat } from "./VoiceChat";

export function PatientAppointmentDashboard() {
  const { user, userProfile } = useAuth();
  const [showChat, setShowChat] = useState(false);
  const [showVoiceChat, setShowVoiceChat] = useState(false);

  // Mock appointment data
  const upcomingAppointments = [
    {
      id: 1,
      doctor: "Dr. Sarah Johnson",
      specialty: "Cardiologist",
      date: "Today",
      time: "10:30 AM",
      location: "Room 204, Main Building",
      status: "confirmed"
    },
    {
      id: 2,
      doctor: "Dr. Michael Chen",
      specialty: "General Practitioner",
      date: "Nov 22, 2025",
      time: "02:00 PM",
      location: "Teleconsultation",
      status: "scheduled"
    }
  ];

  const recentHealthData = {
    lastVisit: "Nov 10, 2025",
    nextAppointment: "Nov 20, 2025",
    medications: 3,
    pendingTests: 1
  };

  if (!user || !userProfile) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Welcome, {userProfile.display_name || user.displayName}</h1>
              <p className="text-slate-600">Manage your appointments and health records</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-slate-500">Next appointment</p>
                <p className="font-medium">Today at 10:30 AM</p>
              </div>
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                {userProfile.display_name?.charAt(0) || user.displayName?.charAt(0) || 'U'}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Next Appointment</CardTitle>
              <Calendar className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">Today</div>
              <p className="text-xs text-slate-500">10:30 AM</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Medications</CardTitle>
              <User className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{recentHealthData.medications}</div>
              <p className="text-xs text-slate-500">View details</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Tests</CardTitle>
              <Stethoscope className="h-4 w-4 text-orange-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{recentHealthData.pendingTests}</div>
              <p className="text-xs text-slate-500">Awaiting results</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Last Visit</CardTitle>
              <Clock className="h-4 w-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{recentHealthData.lastVisit}</div>
              <p className="text-xs text-slate-500">3 days ago</p>
            </CardContent>
          </Card>
        </div>

        {/* Upcoming Appointments */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Appointments</CardTitle>
              <CardDescription>Your scheduled appointments</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {upcomingAppointments.map((appointment) => (
                  <div key={appointment.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <Stethoscope className="h-6 w-6 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-medium">{appointment.doctor}</h3>
                        <p className="text-sm text-slate-500">{appointment.specialty}</p>
                        <p className="text-xs text-slate-400">{appointment.location}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{appointment.date}</p>
                      <p className="text-sm text-slate-600">{appointment.time}</p>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        appointment.status === 'confirmed' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {appointment.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Health Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Health Summary</CardTitle>
              <CardDescription>Recent health information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                      <User className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">Blood Pressure</p>
                      <p className="text-xs text-slate-500">Normal range</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">120/80</p>
                    <p className="text-xs text-green-600">Normal</p>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <Stethoscope className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">Heart Rate</p>
                      <p className="text-xs text-slate-500">Beats per minute</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">72 bpm</p>
                    <p className="text-xs text-blue-600">Normal</p>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                      <Clock className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">Last Checkup</p>
                      <p className="text-xs text-slate-500">Routine visit</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">Nov 10</p>
                    <p className="text-xs text-orange-600">1 week ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Chat and Voice Buttons - Fixed at bottom center */}
      <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-4">
        <Button
          onClick={() => {
            setShowChat(!showChat);
            setShowVoiceChat(false);
          }}
          className="h-14 w-14 rounded-full shadow-lg bg-blue-600 hover:bg-blue-700 flex items-center justify-center"
          size="icon"
          title="Text Chat"
        >
          <MessageCircle className="w-6 h-6" />
        </Button>

        <Button
          onClick={() => {
            setShowVoiceChat(!showVoiceChat);
            setShowChat(false);
          }}
          className="h-14 w-14 rounded-full shadow-lg bg-green-600 hover:bg-green-700 flex items-center justify-center"
          size="icon"
          title="Voice Chat"
        >
          <Mic className="w-6 h-6" />
        </Button>
      </div>

      {/* Chat Widget */}
      {showChat && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowChat(false)}></div>
          <div className="absolute bottom-0 left-0 right-0 h-3/4 bg-white rounded-t-2xl shadow-2xl">
            {/* Chat Header */}
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

            {/* Chat Content - Blank except sidebar */}
            <div className="h-full flex">
              {/* Sidebar */}
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

              {/* Main Chat Area - Blank */}
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

      {/* Voice Chat Widget */}
      {showVoiceChat && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowVoiceChat(false)}></div>
          <div className="absolute bottom-0 left-0 right-0 h-3/4 bg-white rounded-t-2xl shadow-2xl">
            {/* Voice Chat Header */}
            <div className="bg-green-600 text-white p-4 rounded-t-2xl flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Mic className="w-5 h-5" />
                <h3 className="font-medium">Voice Medical Assistant</h3>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowVoiceChat(false)}
                className="text-white hover:bg-green-700"
              >
                Close
              </Button>
            </div>

            {/* Voice Chat Content */}
            <div className="h-full overflow-y-auto">
              <VoiceChat onClose={() => setShowVoiceChat(false)} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
