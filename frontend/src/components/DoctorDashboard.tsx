import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Calendar, Users, Stethoscope, Clock } from 'lucide-react';

export const DoctorDashboard: React.FC = () => {
  const { user, userProfile } = useAuth();

  // Mock data for demonstration
  const stats = [
    { title: 'Today\'s Appointments', value: '8', icon: Calendar, color: 'bg-blue-500' },
    { title: 'Active Patients', value: '42', icon: Users, color: 'bg-green-500' },
    { title: 'Specializations', value: '3', icon: Stethoscope, color: 'bg-purple-500' },
    { title: 'This Week', value: '24', icon: Clock, color: 'bg-orange-500' }
  ];

  const upcomingAppointments = [
    { id: 1, patient: 'Sarah Johnson', time: '09:00 AM', condition: 'Routine Checkup', status: 'confirmed' },
    { id: 2, patient: 'Michael Chen', time: '10:30 AM', condition: 'Follow-up', status: 'confirmed' },
    { id: 3, patient: 'Emily Rodriguez', time: '02:00 PM', condition: 'Consultation', status: 'pending' },
    { id: 4, patient: 'James Wilson', time: '04:15 PM', condition: 'Prescription Renewal', status: 'confirmed' }
  ];

  if (!user || !userProfile) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Doctor Dashboard</h1>
          <p className="text-slate-600 mt-2">
            Welcome, Dr. {userProfile.display_name || user.displayName}
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {stat.title}
                  </CardTitle>
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

        {/* Upcoming Appointments */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Appointments</CardTitle>
              <CardDescription>
                Today's scheduled appointments
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {upcomingAppointments.map((appointment) => (
                  <div key={appointment.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-medium">{appointment.patient}</h3>
                      <p className="text-sm text-slate-500">{appointment.condition}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{appointment.time}</p>
                      <Badge variant={appointment.status === 'confirmed' ? 'default' : 'secondary'}>
                        {appointment.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common tasks and actions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button className="w-full justify-start" variant="outline">
                <Calendar className="mr-2 h-4 w-4" />
                Schedule New Appointment
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Users className="mr-2 h-4 w-4" />
                View Patient Records
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Stethoscope className="mr-2 h-4 w-4" />
                Add New Prescription
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Clock className="mr-2 h-4 w-4" />
                View Schedule
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
