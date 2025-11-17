import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Heart, Shield, Clock, Users, Mail, Loader2, MessageSquare, Stethoscope, Activity, Calendar } from 'lucide-react';
import { GuestChat } from './GuestChat';

export const LandingPage: React.FC = () => {
  const { googleSignIn } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError(null);
    try {
      await googleSignIn();
    } catch (error: any) {
      console.error('Google sign-in error:', error);
      setError(error.message || 'Failed to sign in with Google');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Heart className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-medium text-slate-900">
                CareAgent
              </span>
            </div>
            <Button
              onClick={handleGoogleSignIn}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {loading ? (
                <Loader2 className="mr-2 h-4 w-4" />
              ) : (
                <Mail className="mr-2 h-4 w-4" />
              )}
              Sign In
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-white h-screen">
        <div className="container mx-auto px-6 py-16">
          <div className="flex justify-center gap-8 h-dvh">
            {/* Hero Content */}
            <div className="flex flex-col justify-center gap-8 max-w-lg">
              <div className="inline-flex items-center gap-2 bg-blue-100
               text-blue-700 px-4 py-2 rounded-full text-sm font-medium">
                <Activity className="h-4 w-4" />
                <span>AI-Powered Healthcare Platform</span>
              </div>

              <h1 className="text-4xl md:text-5xl font-medium text-slate-900">
                Your Health,
                <br />
                <span className="text-blue-600">Our Priority</span>
              </h1>

              <p className="text-lg text-slate-600">
                Connect with healthcare professionals, manage your health records, and get AI-powered insights - all in one secure platform.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  onClick={handleGoogleSignIn}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white py-6 text-base"
                >
                  {loading ? (
                    <Loader2 className="mr-2 h-5 w-5" />
                  ) : (
                    <Mail className="mr-2 h-5 w-5" />
                  )}
                  Login
                </Button>
                <Button
                  variant="outline"
                  className="border-blue-600 text-blue-600 hover:bg-blue-50 py-6 text-base"
                  onClick={() => {
                    const chatElement = document.getElementById('guest-chat');
                    chatElement?.scrollIntoView({ behavior: 'smooth' });
                  }}
                >
                  <MessageSquare className="mr-2 h-5 w-5" />
                  Try Guest Chat
                </Button>
              </div>

              {error && (
                <div className="bg-red-100 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <div className="flex items-center gap-8 pt-4">
                <div className="flex items-center gap-2">
                  <Stethoscope className="h-5 w-5 text-blue-600" />
                  <span className="text-sm text-slate-600 font-medium">100+ Doctors</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-blue-600" />
                  <span className="text-sm text-slate-600 font-medium">500+ Patients</span>
                </div>
              </div>
            </div>

            {/* Hero Card */}
            <div>
              <Card className="shadow-2xl border-slate-200">
                <CardContent className="p-6 space-y-4">
                  <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center">
                        <Stethoscope className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">Dr. Sarah Johnson</p>
                        <p className="text-sm text-slate-500">Cardiologist</p>
                      </div>
                    </div>
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Calendar className="h-5 w-5 text-blue-600" />
                        <span className="text-sm font-medium">Next Appointment</span>
                      </div>
                      <span className="text-sm text-slate-600">Today, 3:00 PM</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-green-100 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Activity className="h-5 w-5 text-green-600" />
                        <span className="text-sm font-medium">Health Score</span>
                      </div>
                      <span className="text-sm font-medium text-green-600">92/100</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-red-100 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Heart className="h-5 w-5 text-red-600" />
                        <span className="text-sm font-medium">Heart Rate</span>
                      </div>
                      <span className="text-sm font-medium text-red-600">72 bpm</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-slate-50 py-16">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-medium text-slate-800 mb-4">
              Why Choose <span className="text-blue-600">CareAgent?</span>
            </h2>
            <p className="text-lg text-slate-600">Everything you need for modern healthcare management</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
              <CardContent className="p-6 space-y-4">
                <div className="w-14 h-14 bg-blue-500 rounded-lg flex items-center justify-center">
                  <Shield className="h-7 w-7 text-white" />
                </div>
                <h3 className="text-xl font-medium text-slate-800">Secure & Private</h3>
                <p className="text-slate-600">
                  Your health data is encrypted and protected with enterprise-grade security. HIPAA compliant.
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
              <CardContent className="p-6 space-y-4">
                <div className="w-14 h-14 bg-blue-500 rounded-lg flex items-center justify-center">
                  <Clock className="h-7 w-7 text-white" />
                </div>
                <h3 className="text-xl font-medium text-slate-800">24/7 AI Support</h3>
                <p className="text-slate-600">
                  Get instant answers to your health queries with our AI-powered chatbot, available anytime.
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
              <CardContent className="p-6 space-y-4">
                <div className="w-14 h-14 bg-blue-500 rounded-lg flex items-center justify-center">
                  <Users className="h-7 w-7 text-white" />
                </div>
                <h3 className="text-xl font-medium text-slate-800">Expert Doctors</h3>
                <p className="text-slate-600">
                  Connect with certified healthcare professionals across various specializations.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-blue-600 py-16">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center text-white">
            <div>
              <div className="text-4xl font-medium mb-2">500+</div>
              <div className="text-blue-100">Active Patients</div>
            </div>
            <div>
              <div className="text-4xl font-medium mb-2">100+</div>
              <div className="text-blue-100">Healthcare Professionals</div>
            </div>
            <div>
              <div className="text-4xl font-medium mb-2">10k+</div>
              <div className="text-blue-100">Consultations</div>
            </div>
            <div>
              <div className="text-4xl font-medium mb-2">98%</div>
              <div className="text-blue-100">Satisfaction Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-white py-16">
        <div className="container mx-auto px-6">
          <Card className="border-blue-600 shadow-2xl bg-blue-600 text-white">
            <CardContent className="p-12 text-center space-y-6">
              <h2 className="text-3xl font-medium">Ready to Transform Your Healthcare Experience?</h2>
              <p className="text-lg text-blue-100 max-w-2xl mx-auto">
                Join thousands of patients and doctors who trust CareAgent for their healthcare needs.
              </p>
              <Button
                onClick={handleGoogleSignIn}
                disabled={loading}
                className="bg-white text-blue-600 hover:bg-blue-50 py-6 px-8"
              >
                {loading ? (
                  <Loader2 className="mr-2 h-5 w-5" />
                ) : (
                  <Mail className="mr-2 h-5 w-5" />
                )}
                Login
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Heart className="h-5 w-5 text-white" />
              </div>
              <span className="text-lg font-medium text-white">CareAgent</span>
            </div>
            <div className="text-center">
              <p>© 2025 CareAgent - All rights reserved</p>
            </div>
            <div className="flex gap-6">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Guest Chat */}
      <GuestChat />
    </div>
  );
};
