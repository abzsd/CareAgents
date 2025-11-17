import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { LandingPage } from "./components/LandingPage";
import { EnhancedDoctorDashboard } from "./components/EnhancedDoctorDashboard";
import { UnifiedOnboarding } from "./components/UnifiedOnboarding";
import { EnhancedPatientDashboard } from "./components/EnhancedPatientDashboard";
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

  // If user is not onboarded yet, use unified onboarding
  if (!userProfile.is_onboarded) {
    return <UnifiedOnboarding />;
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
        <EnhancedDoctorDashboard />
      ) : (
        <EnhancedPatientDashboard />
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
