import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userApi } from '../services/api';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, User, Stethoscope } from 'lucide-react';

export const RoleSelection: React.FC = () => {
  const { user, userProfile, setUserProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRole, setSelectedRole] = useState<string>('');

  const handleRoleSelect = async (role: string) => {
    setSelectedRole(role);
    setLoading(true);
    setError(null);

    try {
      if (!userProfile) {
        throw new Error('User profile not found');
      }

      // Update user role
      const updatedUser = await userApi.updateUser(userProfile.user_id, {
        role: role
      });

      setUserProfile(updatedUser);
    } catch (err: any) {
      console.error('Role selection error:', err);
      setError(err.message || 'Failed to select role');
      setSelectedRole('');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">Welcome to CareAgent</CardTitle>
          <CardDescription>
            Please select your role to continue
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-4">
            <Button
              onClick={() => handleRoleSelect('doctor')}
              disabled={loading}
              className="w-full h-20 text-lg justify-start"
              variant={selectedRole === 'doctor' ? 'default' : 'outline'}
            >
              <Stethoscope className="mr-3 h-6 w-6" />
              <div className="text-left">
                <div className="font-semibold">Doctor</div>
                <div className="text-sm text-muted-foreground">Access doctor dashboard and patient records</div>
              </div>
            </Button>

            <Button
              onClick={() => handleRoleSelect('patient')}
              disabled={loading}
              className="w-full h-20 text-lg justify-start"
              variant={selectedRole === 'patient' ? 'default' : 'outline'}
            >
              <User className="mr-3 h-6 w-6" />
              <div className="text-left">
                <div className="font-semibold">Patient</div>
                <div className="text-sm text-muted-foreground">Access your health records and appointments</div>
              </div>
            </Button>
          </div>

          {loading && (
            <div className="flex justify-center">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          )}
        </CardContent>
        <CardFooter className="text-center text-sm text-slate-500">
          <p>You can change your role later in settings</p>
        </CardFooter>
      </Card>
    </div>
  );
};
