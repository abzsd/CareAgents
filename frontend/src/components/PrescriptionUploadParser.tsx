import { useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import {
  Upload,
  FileImage,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  X,
  Edit3,
  Save,
  Eye
} from 'lucide-react';
import { prescriptionParserService, type ParsedPrescription } from '../services/prescriptionParserService';

interface PrescriptionUploadParserProps {
  patientId?: string;
  onSave?: (prescription: ParsedPrescription) => void;
}

export function PrescriptionUploadParser({ patientId, onSave }: PrescriptionUploadParserProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [parsing, setParsing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [parsedData, setParsedData] = useState<ParsedPrescription | null>(null);
  const [editableText, setEditableText] = useState<string>('');
  const [viewMode, setViewMode] = useState<'structured' | 'text'>('structured');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please select a valid image file (JPEG, PNG, or WebP)');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setSelectedFile(file);
    setError(null);
    setParsedData(null);

    // Create preview URL
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleParse = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    try {
      setParsing(true);
      setError(null);

      const result = await prescriptionParserService.parseImage(selectedFile);

      if (result.error) {
        setError(result.error);
        return;
      }

      setParsedData(result);

      // Generate editable text
      const text = await prescriptionParserService.convertToText(result);
      setEditableText(text);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse prescription');
    } finally {
      setParsing(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setParsedData(null);
    setEditableText('');
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSave = () => {
    if (parsedData && onSave) {
      onSave(parsedData);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            Upload Prescription Image
          </CardTitle>
          <CardDescription>
            Upload a photo of the prescription. AI will extract and structure the data.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {!selectedFile ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp"
                onChange={handleFileSelect}
                className="hidden"
              />
              <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-sm text-gray-600 mb-4">
                Drag and drop or click to select prescription image
              </p>
              <Button onClick={() => fileInputRef.current?.click()}>
                Select Image
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Image Preview */}
              <div className="relative border rounded-lg overflow-hidden">
                <img
                  src={previewUrl || ''}
                  alt="Prescription preview"
                  className="w-full max-h-96 object-contain bg-gray-50"
                />
                <Button
                  variant="destructive"
                  size="sm"
                  className="absolute top-2 right-2"
                  onClick={handleClear}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={handleParse}
                  disabled={parsing}
                  className="flex-1"
                >
                  {parsing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Parsing...
                    </>
                  ) : (
                    <>
                      <Edit3 className="h-4 w-4 mr-2" />
                      Parse with AI
                    </>
                  )}
                </Button>
                <Button variant="outline" onClick={handleClear}>
                  Clear
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Parsed Results */}
      {parsedData && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                Extracted Prescription Data
              </CardTitle>
              <div className="flex gap-2">
                <Button
                  variant={viewMode === 'structured' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('structured')}
                >
                  Structured
                </Button>
                <Button
                  variant={viewMode === 'text' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('text')}
                >
                  <Eye className="h-4 w-4 mr-1" />
                  Text
                </Button>
              </div>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-sm text-gray-600">Confidence Score:</span>
              <Badge variant={parsedData.confidence_score >= 80 ? 'default' : 'secondary'}>
                {parsedData.confidence_score}%
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {viewMode === 'structured' ? (
              <>
                {/* Doctor Info */}
                <div>
                  <h3 className="font-semibold mb-3">Doctor Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Name</Label>
                      <Input value={parsedData.doctor.name} readOnly className="mt-1" />
                    </div>
                    <div>
                      <Label>License</Label>
                      <Input value={parsedData.doctor.license} readOnly className="mt-1" />
                    </div>
                    <div>
                      <Label>Clinic</Label>
                      <Input value={parsedData.doctor.clinic} readOnly className="mt-1" />
                    </div>
                    <div>
                      <Label>Contact</Label>
                      <Input value={parsedData.doctor.contact} readOnly className="mt-1" />
                    </div>
                  </div>
                </div>

                {/* Patient Info */}
                <div>
                  <h3 className="font-semibold mb-3">Patient Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Name</Label>
                      <Input value={parsedData.patient.name} readOnly className="mt-1" />
                    </div>
                    <div>
                      <Label>Age</Label>
                      <Input value={parsedData.patient.age} readOnly className="mt-1" />
                    </div>
                    <div>
                      <Label>Gender</Label>
                      <Input value={parsedData.patient.gender} readOnly className="mt-1" />
                    </div>
                    <div>
                      <Label>Patient ID</Label>
                      <Input value={parsedData.patient.id} readOnly className="mt-1" />
                    </div>
                  </div>
                </div>

                {/* Date & Diagnosis */}
                <div>
                  <h3 className="font-semibold mb-3">Consultation Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Date</Label>
                      <Input value={parsedData.date} readOnly className="mt-1" />
                    </div>
                    <div>
                      <Label>Diagnosis</Label>
                      <Input value={parsedData.diagnosis} readOnly className="mt-1" />
                    </div>
                  </div>
                </div>

                {/* Medications */}
                <div>
                  <h3 className="font-semibold mb-3">Medications ({parsedData.medications.length})</h3>
                  <div className="space-y-4">
                    {parsedData.medications.map((med, index) => (
                      <div key={index} className="p-4 border rounded-lg space-y-3">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium">{index + 1}. {med.name}</h4>
                          {med.brand_name && (
                            <Badge variant="outline">{med.brand_name}</Badge>
                          )}
                        </div>
                        <div className="grid grid-cols-3 gap-3 text-sm">
                          <div>
                            <span className="text-gray-600">Dosage:</span>
                            <p className="font-medium">{med.dosage}</p>
                          </div>
                          <div>
                            <span className="text-gray-600">Frequency:</span>
                            <p className="font-medium">{med.frequency}</p>
                          </div>
                          <div>
                            <span className="text-gray-600">Duration:</span>
                            <p className="font-medium">{med.duration}</p>
                          </div>
                        </div>
                        {med.instructions && (
                          <div className="text-sm">
                            <span className="text-gray-600">Instructions:</span>
                            <p className="mt-1">{med.instructions}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Warnings */}
                {parsedData.warnings && parsedData.warnings.length > 0 && (
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <p className="font-semibold mb-2">Warnings:</p>
                      <ul className="list-disc list-inside space-y-1">
                        {parsedData.warnings.map((warning, i) => (
                          <li key={i}>{warning}</li>
                        ))}
                      </ul>
                    </AlertDescription>
                  </Alert>
                )}

                {/* Unclear Portions */}
                {parsedData.unclear_portions && parsedData.unclear_portions.length > 0 && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <p className="font-semibold mb-2">Unclear Portions (Please Review):</p>
                      <ul className="list-disc list-inside space-y-1">
                        {parsedData.unclear_portions.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </AlertDescription>
                  </Alert>
                )}
              </>
            ) : (
              /* Text View */
              <div>
                <Label>Editable Prescription Text</Label>
                <Textarea
                  value={editableText}
                  onChange={(e) => setEditableText(e.target.value)}
                  rows={20}
                  className="mt-2 font-mono text-sm"
                />
              </div>
            )}

            {/* Save Button */}
            <div className="flex gap-3 pt-4">
              {onSave && (
                <Button onClick={handleSave} className="flex-1">
                  <Save className="h-4 w-4 mr-2" />
                  Save Prescription
                </Button>
              )}
              <Button variant="outline" onClick={() => window.print()}>
                Print
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
