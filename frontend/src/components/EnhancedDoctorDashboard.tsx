import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Calendar, Users, Stethoscope, Clock, Activity } from 'lucide-react';
import { DoctorPatientList } from './DoctorPatientList';
import { PatientDetailView } from './PatientDetailView';
import { AddMedicalRecordForm } from './AddMedicalRecordForm';
import { DoctorPatientChatView } from './DoctorPatientChatView';

type ViewMode = 'dashboard' | 'patients' | 'patient-detail' | 'add-record' | 'patient-chat';

export const EnhancedDoctorDashboard = () => {
  const { user, userProfile } = useAuth();
  const [viewMode, setViewMode] = useState<ViewMode>('dashboard');
  const [selectedPatient, setSelectedPatient] = useState<any>(null);

  if (!user || !userProfile) {
    return null;
  }

  const doctorId = userProfile.doctor_id || userProfile.user_id;

  const stats = [
    { title: "Today's Appointments", value: '0', icon: Calendar, color: 'bg-blue-500' },
    { title: 'Total Patients', value: '-', icon: Users, color: 'bg-green-500' },
    { title: 'Active Cases', value: '0', icon: Stethoscope, color: 'bg-purple-500' },
    { title: 'This Week', value: '0', icon: Clock, color: 'bg-orange-500' }
  ];

  const handlePatientSelect = (patient: any) => {
    setSelectedPatient(patient);
    setViewMode('patient-detail');
  };

  const handleAddRecord = () => {
    setViewMode('add-record');
  };

  const handleOpenChat = () => {
    setViewMode('patient-chat');
  };

  const handleBackToPatients = () => {
    setViewMode('patients');
    setSelectedPatient(null);
  };

  const handleBackToPatientDetail = () => {
    setViewMode('patient-detail');
  };

  const handleRecordSuccess = () => {
    setViewMode('patient-detail');
    // Optionally refresh patient data here
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">
                Dr. {userProfile.display_name || user.displayName}
              </h1>
              <p className="text-slate-600">Medical Professional Dashboard</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                {userProfile.display_name?.charAt(0) || user.displayName?.charAt(0) || 'D'}
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex gap-4 mt-6 border-b">
            <button
              onClick={() => setViewMode('dashboard')}
              className={`pb-3 px-4 font-medium transition-colors ${
                viewMode === 'dashboard'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Activity className="inline h-4 w-4 mr-2" />
              Dashboard
            </button>
            <button
              onClick={() => setViewMode('patients')}
              className={`pb-3 px-4 font-medium transition-colors ${
                viewMode === 'patients' || viewMode === 'patient-detail' || viewMode === 'add-record' || viewMode === 'patient-chat'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Users className="inline h-4 w-4 mr-2" />
              Patients
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {viewMode === 'dashboard' && (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <Card key={index}>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                      <div className={`p-2 rounded-full ${stat.color}`}>
                        <Icon className="h-4 w-4 text-white" />
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stat.value}</div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Quick Access */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                  <CardDescription>Common tasks</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <button
                    onClick={() => setViewMode('patients')}
                    className="w-full flex items-center gap-3 p-3 border rounded-lg hover:bg-slate-50 transition-colors text-left"
                  >
                    <Users className="h-5 w-5 text-blue-600" />
                    <div>
                      <p className="font-medium">View All Patients</p>
                      <p className="text-sm text-slate-500">Access patient records and history</p>
                    </div>
                  </button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Latest updates</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-slate-500">
                    <Clock className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>No recent activity</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}

        {viewMode === 'patients' && (
          <DoctorPatientList doctorId={doctorId} onPatientSelect={handlePatientSelect} />
        )}

        {viewMode === 'patient-detail' && selectedPatient && (
          <PatientDetailView
            patient={selectedPatient}
            onBack={handleBackToPatients}
            onAddRecord={handleAddRecord}
            onOpenChat={handleOpenChat}
          />
        )}

        {viewMode === 'patient-chat' && selectedPatient && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">
                AI Chat - {selectedPatient.first_name} {selectedPatient.last_name}
              </h2>
              <div className="flex gap-2">
                <button
                  onClick={handleBackToPatientDetail}
                  className="px-4 py-2 text-sm border rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Back to Patient Details
                </button>
                <button
                  onClick={handleBackToPatients}
                  className="px-4 py-2 text-sm border rounded-lg hover:bg-slate-50 transition-colors"
                >
                  Back to Patients
                </button>
              </div>
            </div>
            <DoctorPatientChatView patientId={selectedPatient.patient_id} />
          </div>
        )}

        {viewMode === 'add-record' && selectedPatient && (
          <AddMedicalRecordForm
            patientId={selectedPatient.patient_id}
            patientName={`${selectedPatient.first_name} ${selectedPatient.last_name}`}
            onBack={() => setViewMode('patient-detail')}
            onSuccess={handleRecordSuccess}
          />
        )}
      </div>
    </div>
  );
};
