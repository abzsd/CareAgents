import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import {
  MessageSquare,
  Send,
  Loader2,
  User,
  Activity,
  AlertTriangle,
  Sparkles,
  TrendingUp,
  FileText,
  Calendar,
  Heart
} from 'lucide-react';
import { doctorChatService, type ChatMessage } from '../services/doctorChatService';
import { medicalHistoryService } from '../services/medicalHistoryService';
import { patientService, type PatientData } from '../services/patientService';

interface DoctorPatientChatViewProps {
  patientId: string;
}

export function DoctorPatientChatView({ patientId }: DoctorPatientChatViewProps) {
  const [patient, setPatient] = useState<PatientData | null>(null);
  const [medicalHistory, setMedicalHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Chat state
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
  const [input, setInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Summary state
  const [summary, setSummary] = useState<string | null>(null);
  const [summaryType, setSummaryType] = useState<'comprehensive' | 'brief' | 'recent' | 'medications'>('comprehensive');
  const [summaryLoading, setSummaryLoading] = useState(false);

  // Risk analysis state
  const [riskAnalysis, setRiskAnalysis] = useState<any | null>(null);
  const [riskLoading, setRiskLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Quick action prompts
  const quickActions = [
    { label: 'Latest Visit Summary', query: 'Summarize the most recent medical visit' },
    { label: 'Current Medications', query: 'List all current medications with dosages' },
    { label: 'Chronic Conditions', query: 'What chronic conditions does this patient have?' },
    { label: 'Allergies & Warnings', query: 'List all allergies and any contraindications' },
    { label: 'Recent Lab Results', query: 'Summarize recent lab results and vital signs' },
  ];

  useEffect(() => {
    loadPatientData();
  }, [patientId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadPatientData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load patient demographics
      const patientData = await patientService.getPatient(patientId);
      setPatient(patientData);

      // Load medical history
      const historyData = await medicalHistoryService.getPatientMedicalHistory(patientId);
      setMedicalHistory(historyData.records || []);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load patient data');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || chatLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      setChatLoading(true);

      // Convert messages to conversation history format
      const conversationHistory: ChatMessage[] = messages.map(msg => ({
        role: msg.role === 'user' ? 'user' : 'model',
        parts: [{ text: msg.content }]
      }));

      // Send to AI
      const response = await doctorChatService.chat(
        userMessage,
        patientId,
        conversationHistory
      );

      // Add assistant response
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat failed');
      // Remove user message if failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setChatLoading(false);
    }
  };

  const handleQuickAction = (query: string) => {
    setInput(query);
  };

  const loadSummary = async (type: typeof summaryType) => {
    try {
      setSummaryLoading(true);
      setSummaryType(type);

      const response = await doctorChatService.getSummary(patientId, type);
      setSummary(response.summary);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load summary');
    } finally {
      setSummaryLoading(false);
    }
  };

  const loadRiskAnalysis = async () => {
    try {
      setRiskLoading(true);

      const analysis = await doctorChatService.getRiskAnalysis(patientId);
      setRiskAnalysis(analysis);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load risk analysis');
    } finally {
      setRiskLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!patient) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>Patient not found</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left Column - Patient Info & Summary */}
      <div className="lg:col-span-1 space-y-6">
        {/* Patient Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Patient Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="text-xl font-semibold">
                {patient.first_name} {patient.last_name}
              </h3>
              <p className="text-sm text-gray-600">{patient.email}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Age:</span>
                <p className="font-medium">{patient.age} years</p>
              </div>
              <div>
                <span className="text-gray-600">Gender:</span>
                <p className="font-medium">{patient.gender}</p>
              </div>
              <div>
                <span className="text-gray-600">Blood Type:</span>
                <p className="font-medium">{patient.blood_type || 'N/A'}</p>
              </div>
              <div>
                <span className="text-gray-600">Phone:</span>
                <p className="font-medium">{patient.phone || 'N/A'}</p>
              </div>
            </div>

            {patient.allergies && patient.allergies.length > 0 && (
              <div>
                <p className="text-sm text-gray-600 mb-2">Allergies:</p>
                <div className="flex flex-wrap gap-2">
                  {patient.allergies.map((allergy, i) => (
                    <Badge key={i} variant="destructive">{allergy}</Badge>
                  ))}
                </div>
              </div>
            )}

            {patient.chronic_conditions && patient.chronic_conditions.length > 0 && (
              <div>
                <p className="text-sm text-gray-600 mb-2">Chronic Conditions:</p>
                <div className="flex flex-wrap gap-2">
                  {patient.chronic_conditions.map((condition, i) => (
                    <Badge key={i} variant="secondary">{condition}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Summary Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-600" />
              AI-Generated Summary
            </CardTitle>
            <CardDescription>
              Get intelligent patient summaries
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {['comprehensive', 'brief', 'recent', 'medications'].map((type) => (
                <Button
                  key={type}
                  variant={summaryType === type ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => loadSummary(type as typeof summaryType)}
                  disabled={summaryLoading}
                  className="capitalize"
                >
                  {type}
                </Button>
              ))}
            </div>

            {summaryLoading ? (
              <div className="flex items-center justify-center p-4">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : summary ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm whitespace-pre-wrap">{summary}</p>
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center py-4">
                Select a summary type to generate
              </p>
            )}
          </CardContent>
        </Card>

        {/* Risk Analysis Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-orange-600" />
              Risk Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!riskAnalysis ? (
              <Button
                onClick={loadRiskAnalysis}
                disabled={riskLoading}
                className="w-full"
              >
                {riskLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Analyze Risk Factors
                  </>
                )}
              </Button>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Risk Level:</span>
                  <Badge variant={
                    riskAnalysis.risk_level === 'high' ? 'destructive' :
                    riskAnalysis.risk_level === 'moderate' ? 'default' : 'secondary'
                  } className="capitalize">
                    {riskAnalysis.risk_level}
                  </Badge>
                </div>

                {riskAnalysis.risk_factors && riskAnalysis.risk_factors.length > 0 && (
                  <div>
                    <p className="text-sm font-medium mb-2">Risk Factors:</p>
                    <ul className="list-disc list-inside text-sm space-y-1">
                      {riskAnalysis.risk_factors.map((factor: string, i: number) => (
                        <li key={i}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {riskAnalysis.summary && (
                  <p className="text-sm bg-gray-50 p-3 rounded border">
                    {riskAnalysis.summary}
                  </p>
                )}

                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadRiskAnalysis}
                  className="w-full"
                >
                  Refresh Analysis
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Right Column - AI Chat Interface */}
      <div className="lg:col-span-2">
        <Card className="h-[calc(100vh-12rem)]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              AI Patient Summary Chat
            </CardTitle>
            <CardDescription>
              Ask questions about this patient's medical history
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col h-[calc(100%-5rem)]">
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Quick Actions */}
            {messages.length === 0 && (
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">Quick Actions:</p>
                <div className="flex flex-wrap gap-2">
                  {quickActions.map((action, i) => (
                    <Button
                      key={i}
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickAction(action.query)}
                    >
                      {action.label}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.length === 0 && (
                <div className="flex items-center justify-center h-full text-center">
                  <div>
                    <Sparkles className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500">
                      Ask me anything about this patient's medical history
                    </p>
                  </div>
                </div>
              )}

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))}

              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <Loader2 className="h-5 w-5 animate-spin text-gray-600" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="flex gap-2">
              <Input
                placeholder="Ask about this patient..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                disabled={chatLoading}
              />
              <Button
                onClick={handleSendMessage}
                disabled={!input.trim() || chatLoading}
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
