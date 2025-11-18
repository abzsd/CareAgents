import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { userApi, onboardingApi } from '../services/api';
import { patientService } from '../services/patientService';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, User, Stethoscope } from 'lucide-react';

type OnboardingStep = 'role-selection' | 'doctor-onboarding' | 'patient-onboarding';

export const UnifiedOnboarding: React.FC = () => {
  const { user, userProfile, setUserProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('role-selection');
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
      
      // Move to the appropriate onboarding form
      if (role === 'doctor') {
        setCurrentStep('doctor-onboarding');
      } else {
        setCurrentStep('patient-onboarding');
      }
    } catch (err: any) {
      console.error('Role selection error:', err);
      setError(err.message || 'Failed to select role');
      setSelectedRole('');
    } finally {
      setLoading(false);
    }
  };

  const handleOnboardingComplete = async () => {
    try {
      if (!userProfile) {
        throw new Error('User profile not found');
      }

      // Mark user as onboarded
      const updatedUser = await userApi.updateUser(userProfile.user_id, {
        is_onboarded: true
      });

      setUserProfile(updatedUser);
    } catch (err: any) {
      console.error('Onboarding completion error:', err);
      setError(err.message || 'Failed to complete onboarding');
    }
  };

  if (!user) {
    return null;
  }

  // Doctor Onboarding Form Component
  const DoctorOnboardingForm = () => {
    const [formData, setFormData] = useState({
      firstName: user?.displayName?.split(' ')[0] || '',
      lastName: user?.displayName?.split(' ').slice(1).join(' ') || '',
      phone: '',
      specialization: '',
      licenseNumber: '',
      licenseState: '',
      yearsOfExperience: '',
      qualifications: [{ degree: '', institution: '', year: '' }]
    });

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      const { name, value } = e.target;
      setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSelectChange = (value: string) => {
      setFormData(prev => ({ ...prev, specialization: value }));
    };

    const handleQualificationChange = (index: number, field: string, value: string) => {
      const newQualifications = [...formData.qualifications];
      newQualifications[index] = { ...newQualifications[index], [field]: value };
      setFormData(prev => ({ ...prev, qualifications: newQualifications }));
    };

    const addQualification = () => {
      setFormData(prev => ({
        ...prev,
        qualifications: [...prev.qualifications, { degree: '', institution: '', year: '' }]
      }));
    };

    const removeQualification = (index: number) => {
      if (formData.qualifications.length > 1) {
        const newQualifications = formData.qualifications.filter((_, i) => i !== index);
        setFormData(prev => ({ ...prev, qualifications: newQualifications }));
      }
    };

    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      setLoading(true);
      setError(null);

      try {
        if (!userProfile) {
          throw new Error('User profile not found');
        }

        // Validate required fields
        if (!formData.specialization) {
          throw new Error('Please select a medical specialization');
        }
        if (!formData.licenseNumber) {
          throw new Error('Please enter your medical license number');
        }

        // Prepare education data
        const education = formData.qualifications
          .filter(q => q.degree || q.institution || q.year)
          .map(q => ({
            degree: q.degree,
            institution: q.institution,
            year: q.year ? parseInt(q.year) : undefined
          }));

        // Validate license state
        if (!formData.licenseState) {
          throw new Error('Please enter your license state/country');
        }

        // Create doctor record via onboarding API
        const onboardingResult = await onboardingApi.onboardDoctor({
          user_id: userProfile.user_id,
          first_name: formData.firstName,
          last_name: formData.lastName,
          specialization: formData.specialization,
          license_number: formData.licenseNumber,
          license_state: formData.licenseState,
          phone: formData.phone || undefined,
          email: user?.email || undefined,
          experience_years: formData.yearsOfExperience ? parseInt(formData.yearsOfExperience) : undefined,
          education: education.length > 0 ? education : undefined
        });

        console.log('Doctor onboarding successful:', onboardingResult);

        // Update user profile with display name
        const updatedUser = await userApi.updateUser(userProfile.user_id, {
          display_name: `${formData.firstName} ${formData.lastName}`
        });

        setUserProfile(updatedUser);

      } catch (err: any) {
        console.error('Onboarding error:', err);
        setError(err.message || 'Failed to complete onboarding');
      } finally {
        setLoading(false);
      }
    };

    return (
      <>
        <CardHeader>
          <CardTitle className="text-2xl">Doctor Onboarding</CardTitle>
          <CardDescription>
            Please complete your profile to access the doctor dashboard
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={user?.email || ''}
                disabled
                className="bg-slate-100"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="specialization">Medical Specialization</Label>
              <Select
                value={formData.specialization}
                onValueChange={handleSelectChange}
              >
                <SelectTrigger className="bg-white">
                  <SelectValue placeholder="Select specialization" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="cardiology">Cardiology</SelectItem>
                  <SelectItem value="neurology">Neurology</SelectItem>
                  <SelectItem value="oncology">Oncology</SelectItem>
                  <SelectItem value="pediatrics">Pediatrics</SelectItem>
                  <SelectItem value="orthopedics">Orthopedics</SelectItem>
                  <SelectItem value="dermatology">Dermatology</SelectItem>
                  <SelectItem value="general-practice">General Practice</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="licenseNumber">Medical License Number</Label>
                <Input
                  id="licenseNumber"
                  name="licenseNumber"
                  value={formData.licenseNumber}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="licenseState">License State/Country</Label>
                <Input
                  id="licenseState"
                  name="licenseState"
                  value={formData.licenseState}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="yearsOfExperience">Years of Experience</Label>
              <Input
                id="yearsOfExperience"
                name="yearsOfExperience"
                type="number"
                value={formData.yearsOfExperience}
                onChange={handleInputChange}
                min="0"
                max="60"
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>Qualifications</Label>
                <Button type="button" variant="outline" size="sm" onClick={addQualification}>
                  Add Qualification
                </Button>
              </div>
              
              {formData.qualifications.map((qual, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 border rounded-lg">
                  <div className="space-y-2">
                    <Label>Degree</Label>
                    <Input
                      value={qual.degree}
                      onChange={(e) => handleQualificationChange(index, 'degree', e.target.value)}
                      placeholder="e.g., MD, MBBS"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Institution</Label>
                    <Input
                      value={qual.institution}
                      onChange={(e) => handleQualificationChange(index, 'institution', e.target.value)}
                      placeholder="University/College"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Year</Label>
                    <Input
                      value={qual.year}
                      onChange={(e) => handleQualificationChange(index, 'year', e.target.value)}
                      placeholder="e.g., 2020"
                      type="number"
                      min="1950"
                      max="2025"
                    />
                  </div>
                </div>
              ))}
            </div>
          </form>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={() => setCurrentStep('role-selection')}>
            Back
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : null}
            Complete Onboarding
          </Button>
        </CardFooter>
      </>
    );
  };

  // Patient Onboarding Form Component
  const PatientOnboardingForm = () => {
    const [formData, setFormData] = useState({
      firstName: user?.displayName?.split(' ')[0] || '',
      lastName: user?.displayName?.split(' ').slice(1).join(' ') || '',
      dateOfBirth: '',
      gender: '',
      phone: '',
      height: '',
      weight: '',
      bloodType: '',
      allergies: '',
      chronicConditions: ''
    });

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSelectChange = (name: string, value: string) => {
      setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      setLoading(true);
      setError(null);

      try {
        if (!userProfile) {
          throw new Error('User profile not found');
        }

        // Validate required fields
        if (!formData.gender) {
          throw new Error('Please select your gender');
        }

        if (!formData.dateOfBirth) {
          throw new Error('Please enter your date of birth');
        }

        // Create patient record with all collected data
        await patientService.createPatientForUser(userProfile.user_id, {
          first_name: formData.firstName,
          last_name: formData.lastName,
          date_of_birth: formData.dateOfBirth,
          gender: formData.gender,
          email: user?.email || '',
          phone: formData.phone,
          blood_type: formData.bloodType || undefined,
          allergies: formData.allergies ? formData.allergies.split(',').map(a => a.trim()).filter(a => a) : [],
          chronic_conditions: formData.chronicConditions ? formData.chronicConditions.split(',').map(c => c.trim()).filter(c => c) : [],
        });

        // Update user role to patient and mark as onboarded
        const updatedUser = await userApi.updateUser(userProfile.user_id, {
          role: 'patient',
          is_onboarded: true,
          first_name: formData.firstName,
          last_name: formData.lastName,
          phone: formData.phone,
          display_name: `${formData.firstName} ${formData.lastName}`
        });

        setUserProfile(updatedUser);
        handleOnboardingComplete();

      } catch (err: any) {
        console.error('Onboarding error:', err);
        setError(err.message || 'Failed to complete onboarding');
      } finally {
        setLoading(false);
      }
    };

    return (
      <>
        <CardHeader>
          <CardTitle className="text-2xl">Patient Onboarding</CardTitle>
          <CardDescription>
            Please complete your profile to access the patient dashboard
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={user?.email || ''}
                disabled
                className="bg-slate-100"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="dateOfBirth">Date of Birth</Label>
                <Input
                  id="dateOfBirth"
                  name="dateOfBirth"
                  type="date"
                  value={formData.dateOfBirth}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <Select
                  value={formData.gender}
                  onValueChange={(value: string) => handleSelectChange('gender', value)}
                >
                  <SelectTrigger className="bg-white">
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    <SelectItem value="Male">Male</SelectItem>
                    <SelectItem value="Female">Female</SelectItem>
                    <SelectItem value="Other">Other</SelectItem>
                    <SelectItem value="Prefer not to say">Prefer not to say</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="height">Height (cm)</Label>
                <Input
                  id="height"
                  name="height"
                  type="number"
                  value={formData.height}
                  onChange={handleInputChange}
                  placeholder="e.g., 175"
                  min="50"
                  max="300"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="weight">Weight (kg)</Label>
                <Input
                  id="weight"
                  name="weight"
                  type="number"
                  value={formData.weight}
                  onChange={handleInputChange}
                  placeholder="e.g., 70"
                  min="10"
                  max="500"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bloodType">Blood Type</Label>
                <Select
                  value={formData.bloodType}
                  onValueChange={(value: string) => handleSelectChange('bloodType', value)}
                >
                  <SelectTrigger className="bg-white">
                    <SelectValue placeholder="Select blood type" />
                  </SelectTrigger>
                  <SelectContent className="bg-white">
                    <SelectItem value="A+">A+</SelectItem>
                    <SelectItem value="A-">A-</SelectItem>
                    <SelectItem value="B+">B+</SelectItem>
                    <SelectItem value="B-">B-</SelectItem>
                    <SelectItem value="AB+">AB+</SelectItem>
                    <SelectItem value="AB-">AB-</SelectItem>
                    <SelectItem value="O+">O+</SelectItem>
                    <SelectItem value="O-">O-</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="allergies">Allergies (comma separated)</Label>
              <Input
                id="allergies"
                name="allergies"
                value={formData.allergies}
                onChange={handleInputChange}
                placeholder="e.g., Penicillin, Pollen, Shellfish"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="chronicConditions">Chronic Conditions (comma separated)</Label>
              <Input
                id="chronicConditions"
                name="chronicConditions"
                value={formData.chronicConditions}
                onChange={handleInputChange}
                placeholder="e.g., Diabetes, Hypertension, Asthma"
              />
            </div>
          </form>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={() => setCurrentStep('role-selection')}>
            Back
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : null}
            Complete Onboarding
          </Button>
        </CardFooter>
      </>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        {currentStep === 'role-selection' && (
          <>
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
          </>
        )}

        {currentStep === 'doctor-onboarding' && <DoctorOnboardingForm />}
        {currentStep === 'patient-onboarding' && <PatientOnboardingForm />}
      </Card>
    </div>
  );
};
