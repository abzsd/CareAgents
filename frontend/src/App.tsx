import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { LandingPage } from "./components/LandingPage";
import { PatientDashboard } from "./components/PatientDashboard";
import { DoctorDashboard } from "./components/DoctorDashboard";
import { DoctorOnboarding } from "./components/DoctorOnboarding";
import { PatientOnboarding } from "./components/PatientOnboarding";
import { RoleSelection } from "./components/RoleSelection";
import { Button } from "./components/ui/button";
import { Loader2 } from "lucide-react";

function AppContent() {
  const { user, userProfile, logout, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto" />
          <p className="mt-2 text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LandingPage />;
  }

  // If user profile doesn't exist, something went wrong
  if (!userProfile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center p-6">
          <div className="text-red-500 text-xl font-semibold">Error</div>
          <p className="mt-2 text-slate-600">Failed to load user profile</p>
          <Button onClick={logout} className="mt-4">Logout</Button>
        </div>
      </div>
    );
  }

  // If user hasn't selected a role yet
  if (!userProfile.role || (userProfile.role !== 'doctor' && userProfile.role !== 'patient')) {
    return <RoleSelection />;
  }

  // If user is not onboarded yet
  if (!userProfile.is_onboarded) {
    if (userProfile.role === 'doctor') {
      return <DoctorOnboarding />;
    } else {
      return <PatientOnboarding />;
    }
  }

  // User is fully onboarded - show appropriate dashboard
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="absolute top-4 right-4">
        <Button onClick={logout} variant="outline" size="sm">
          Logout
        </Button>
      </div>
      {userProfile.role === 'doctor' ? (
        <DoctorDashboard />
      ) : (
        <PatientDashboard />
      )}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
