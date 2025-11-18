-- ========================================================================
-- Safe Dummy Data Artifact for CareAgents Healthcare Platform
-- ========================================================================
-- This script contains ONLY fictional, safe dummy data
-- NO real PII or sensitive information is included
-- All names, emails, phone numbers, and addresses are completely fabricated
-- ========================================================================

-- Clear existing data (in reverse order to respect foreign key constraints)
DELETE FROM medical_reports;
DELETE FROM prescriptions;
DELETE FROM health_vitals;
DELETE FROM medical_history;
DELETE FROM appointments;
DELETE FROM doctors;
DELETE FROM patients;
DELETE FROM organizations;
DELETE FROM users;

-- ========================================================================
-- ORGANIZATIONS - Fictional Healthcare Facilities
-- ========================================================================

INSERT INTO organizations (organization_id, name, type, address, phone, email, website, license_number, is_active, created_at, updated_at)
VALUES
(
    gen_random_uuid(),
    'Bay Area Medical Center',
    'Hospital',
    '{"street": "1234 Healthcare Blvd", "city": "San Francisco", "state": "CA", "zip_code": "94102", "country": "USA"}'::jsonb,
    '+1-800-555-0100',
    'info@bayareamedical.example.com',
    'https://bayareamedical.example.com',
    'HOSP-CA-001122',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'Sunshine Community Clinic',
    'Clinic',
    '{"street": "567 Wellness Way", "city": "Oakland", "state": "CA", "zip_code": "94607", "country": "USA"}'::jsonb,
    '+1-800-555-0200',
    'contact@sunshineclinic.example.com',
    'https://sunshineclinic.example.com',
    'CLIN-CA-002233',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'Advanced Diagnostics Lab',
    'Laboratory',
    '{"street": "890 Research Park Dr", "city": "Berkeley", "state": "CA", "zip_code": "94720", "country": "USA"}'::jsonb,
    '+1-800-555-0300',
    'results@advdiagnostics.example.com',
    'https://advdiagnostics.example.com',
    'LAB-CA-003344',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- ========================================================================
-- USERS - Fictional User Accounts (Doctors, Patients, Admin)
-- ========================================================================

INSERT INTO users (user_id, email, display_name, photo_url, role, is_onboarded, firebase_uid, provider_id, last_login_at, is_active, created_at, updated_at)
VALUES
-- Doctors
(
    'user-doc-001',
    'dr.alexandra.rivers@careagents.example',
    'Dr. Alexandra Rivers',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=alexandra',
    'doctor',
    true,
    'firebase-uid-doc-001',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '2 hours',
    true,
    CURRENT_TIMESTAMP - INTERVAL '90 days',
    CURRENT_TIMESTAMP
),
(
    'user-doc-002',
    'dr.benjamin.stone@careagents.example',
    'Dr. Benjamin Stone',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=benjamin',
    'doctor',
    true,
    'firebase-uid-doc-002',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '5 hours',
    true,
    CURRENT_TIMESTAMP - INTERVAL '120 days',
    CURRENT_TIMESTAMP
),
(
    'user-doc-003',
    'dr.catherine.wong@careagents.example',
    'Dr. Catherine Wong',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=catherine',
    'doctor',
    true,
    'firebase-uid-doc-003',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '1 day',
    true,
    CURRENT_TIMESTAMP - INTERVAL '200 days',
    CURRENT_TIMESTAMP
),
(
    'user-doc-004',
    'dr.david.kumar@careagents.example',
    'Dr. David Kumar',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=david',
    'doctor',
    true,
    'firebase-uid-doc-004',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '3 hours',
    true,
    CURRENT_TIMESTAMP - INTERVAL '150 days',
    CURRENT_TIMESTAMP
),
(
    'user-doc-005',
    'dr.elena.martinez@careagents.example',
    'Dr. Elena Martinez',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=elena',
    'doctor',
    true,
    'firebase-uid-doc-005',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '6 hours',
    true,
    CURRENT_TIMESTAMP - INTERVAL '180 days',
    CURRENT_TIMESTAMP
),
-- Patients
(
    'user-pat-001',
    'alex.demo@example.com',
    'Alex Demo',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=alex',
    'patient',
    true,
    'firebase-uid-pat-001',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '1 hour',
    true,
    CURRENT_TIMESTAMP - INTERVAL '60 days',
    CURRENT_TIMESTAMP
),
(
    'user-pat-002',
    'sam.test@example.com',
    'Sam Test',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=sam',
    'patient',
    true,
    'firebase-uid-pat-002',
    'email',
    CURRENT_TIMESTAMP - INTERVAL '4 hours',
    true,
    CURRENT_TIMESTAMP - INTERVAL '45 days',
    CURRENT_TIMESTAMP
),
(
    'user-pat-003',
    'jordan.sample@example.com',
    'Jordan Sample',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=jordan',
    'patient',
    true,
    'firebase-uid-pat-003',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '8 hours',
    true,
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    CURRENT_TIMESTAMP
),
(
    'user-pat-004',
    'morgan.example@example.com',
    'Morgan Example',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=morgan',
    'patient',
    true,
    'firebase-uid-pat-004',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '12 hours',
    true,
    CURRENT_TIMESTAMP - INTERVAL '75 days',
    CURRENT_TIMESTAMP
),
(
    'user-pat-005',
    'taylor.dummy@example.com',
    'Taylor Dummy',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=taylor',
    'patient',
    true,
    'firebase-uid-pat-005',
    'email',
    CURRENT_TIMESTAMP - INTERVAL '2 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '20 days',
    CURRENT_TIMESTAMP
),
(
    'user-pat-006',
    'casey.placeholder@example.com',
    'Casey Placeholder',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=casey',
    'patient',
    true,
    'firebase-uid-pat-006',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '5 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '10 days',
    CURRENT_TIMESTAMP
),
-- Admin
(
    'user-admin-001',
    'admin@careagents.example',
    'System Administrator',
    'https://api.dicebear.com/7.x/avataaars/svg?seed=admin',
    'admin',
    true,
    'firebase-uid-admin-001',
    'google.com',
    CURRENT_TIMESTAMP - INTERVAL '30 minutes',
    true,
    CURRENT_TIMESTAMP - INTERVAL '365 days',
    CURRENT_TIMESTAMP
);

-- ========================================================================
-- DOCTORS - Fictional Doctor Profiles
-- ========================================================================

INSERT INTO doctors (doctor_id, user_id, first_name, last_name, specialization, license_number, phone, email, address, experience_years, education, certifications, is_active, created_at, updated_at)
VALUES
(
    'doc-001',
    'user-doc-001',
    'Alexandra',
    'Rivers',
    'Cardiology',
    'MD-CA-111111',
    '+1-555-0001',
    'dr.alexandra.rivers@careagents.example',
    '{"street": "100 Medical Plaza Suite 200", "city": "San Francisco", "state": "CA", "zip_code": "94102", "country": "USA"}'::jsonb,
    15,
    '[{"degree": "MD", "institution": "Fictional Medical School", "year": 2009}, {"degree": "Fellowship in Cardiology", "institution": "Example Heart Institute", "year": 2013}]'::jsonb,
    '["Board Certified - Cardiology", "Advanced Cardiac Life Support"]'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '90 days',
    CURRENT_TIMESTAMP
),
(
    'doc-002',
    'user-doc-002',
    'Benjamin',
    'Stone',
    'Pediatrics',
    'MD-CA-222222',
    '+1-555-0002',
    'dr.benjamin.stone@careagents.example',
    '{"street": "200 Children Way Suite 150", "city": "Oakland", "state": "CA", "zip_code": "94607", "country": "USA"}'::jsonb,
    12,
    '[{"degree": "MD", "institution": "Sample University Medical School", "year": 2012}, {"degree": "Residency in Pediatrics", "institution": "Demo Children Hospital", "year": 2015}]'::jsonb,
    '["Board Certified - Pediatrics", "Pediatric Advanced Life Support"]'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '120 days',
    CURRENT_TIMESTAMP
),
(
    'doc-003',
    'user-doc-003',
    'Catherine',
    'Wong',
    'Neurology',
    'MD-CA-333333',
    '+1-555-0003',
    'dr.catherine.wong@careagents.example',
    '{"street": "300 Brain Center Blvd", "city": "Berkeley", "state": "CA", "zip_code": "94720", "country": "USA"}'::jsonb,
    18,
    '[{"degree": "MD", "institution": "Test Medical College", "year": 2006}, {"degree": "Fellowship in Neurology", "institution": "Placeholder Neuro Institute", "year": 2011}]'::jsonb,
    '["Board Certified - Neurology", "Epilepsy Specialist"]'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '200 days',
    CURRENT_TIMESTAMP
),
(
    'doc-004',
    'user-doc-004',
    'David',
    'Kumar',
    'Orthopedics',
    'MD-CA-444444',
    '+1-555-0004',
    'dr.david.kumar@careagents.example',
    '{"street": "400 Bone Health Dr", "city": "San Jose", "state": "CA", "zip_code": "95110", "country": "USA"}'::jsonb,
    10,
    '[{"degree": "MD", "institution": "Example State Medical School", "year": 2014}, {"degree": "Orthopedic Surgery Residency", "institution": "Sample Orthopedic Center", "year": 2019}]'::jsonb,
    '["Board Certified - Orthopedic Surgery", "Sports Medicine Certified"]'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '150 days',
    CURRENT_TIMESTAMP
),
(
    'doc-005',
    'user-doc-005',
    'Elena',
    'Martinez',
    'Dermatology',
    'MD-CA-555555',
    '+1-555-0005',
    'dr.elena.martinez@careagents.example',
    '{"street": "500 Skin Care Ave", "city": "Palo Alto", "state": "CA", "zip_code": "94301", "country": "USA"}'::jsonb,
    14,
    '[{"degree": "MD", "institution": "Dummy Medical School", "year": 2010}, {"degree": "Dermatology Residency", "institution": "Placeholder Dermatology Institute", "year": 2014}]'::jsonb,
    '["Board Certified - Dermatology", "Cosmetic Procedures Certified"]'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '180 days',
    CURRENT_TIMESTAMP
);

-- ========================================================================
-- PATIENTS - Fictional Patient Profiles
-- ========================================================================

INSERT INTO patients (patient_id, user_id, first_name, last_name, date_of_birth, age, gender, email, phone, address, emergency_contact, blood_type, allergies, chronic_conditions, insurance_info, is_active, created_at, updated_at)
VALUES
(
    'pat-001',
    'user-pat-001',
    'Alex',
    'Demo',
    '1985-06-15',
    39,
    'Male',
    'alex.demo@example.com',
    '+1-555-1001',
    '{"street": "1010 Test Street Apt 5A", "city": "San Francisco", "state": "CA", "zip_code": "94103", "country": "USA"}'::jsonb,
    '{"name": "Jamie Demo", "relationship": "Sibling", "phone": "+1-555-1002"}'::jsonb,
    'O+',
    '["None Known"]'::jsonb,
    '["Well Controlled Hypertension"]'::jsonb,
    '{"provider": "Example Health Insurance", "policy_number": "EXM-123456", "group_number": "GRP-001"}'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '60 days',
    CURRENT_TIMESTAMP
),
(
    'pat-002',
    'user-pat-002',
    'Sam',
    'Test',
    '1992-03-22',
    32,
    'Female',
    'sam.test@example.com',
    '+1-555-1003',
    '{"street": "2020 Sample Ave Apt 12B", "city": "Oakland", "state": "CA", "zip_code": "94610", "country": "USA"}'::jsonb,
    '{"name": "Riley Test", "relationship": "Spouse", "phone": "+1-555-1004"}'::jsonb,
    'A+',
    '["Penicillin - Mild Rash"]'::jsonb,
    '[]'::jsonb,
    '{"provider": "Demo Insurance Co", "policy_number": "DMO-789012", "group_number": "GRP-002"}'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '45 days',
    CURRENT_TIMESTAMP
),
(
    'pat-003',
    'user-pat-003',
    'Jordan',
    'Sample',
    '1978-11-08',
    46,
    'Non-binary',
    'jordan.sample@example.com',
    '+1-555-1005',
    '{"street": "3030 Placeholder Rd", "city": "Berkeley", "state": "CA", "zip_code": "94702", "country": "USA"}'::jsonb,
    '{"name": "Avery Sample", "relationship": "Partner", "phone": "+1-555-1006"}'::jsonb,
    'B+',
    '["Latex", "Sulfa Drugs"]'::jsonb,
    '["Type 2 Diabetes - Diet Controlled"]'::jsonb,
    '{"provider": "Sample Care Insurance", "policy_number": "SMP-345678", "group_number": "GRP-003"}'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    CURRENT_TIMESTAMP
),
(
    'pat-004',
    'user-pat-004',
    'Morgan',
    'Example',
    '1995-09-30',
    29,
    'Female',
    'morgan.example@example.com',
    '+1-555-1007',
    '{"street": "4040 Dummy Lane", "city": "San Jose", "state": "CA", "zip_code": "95112", "country": "USA"}'::jsonb,
    '{"name": "Quinn Example", "relationship": "Parent", "phone": "+1-555-1008"}'::jsonb,
    'AB+',
    '["Peanuts", "Tree Nuts"]'::jsonb,
    '["Asthma - Well Controlled"]'::jsonb,
    '{"provider": "Test Health Plan", "policy_number": "TST-901234", "group_number": "GRP-004"}'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '75 days',
    CURRENT_TIMESTAMP
),
(
    'pat-005',
    'user-pat-005',
    'Taylor',
    'Dummy',
    '1988-12-17',
    36,
    'Male',
    'taylor.dummy@example.com',
    '+1-555-1009',
    '{"street": "5050 Fiction Blvd Apt 3C", "city": "Palo Alto", "state": "CA", "zip_code": "94303", "country": "USA"}'::jsonb,
    '{"name": "Drew Dummy", "relationship": "Spouse", "phone": "+1-555-1010"}'::jsonb,
    'O-',
    '[]'::jsonb,
    '["High Cholesterol"]'::jsonb,
    '{"provider": "Placeholder Insurance", "policy_number": "PLC-567890", "group_number": "GRP-005"}'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '20 days',
    CURRENT_TIMESTAMP
),
(
    'pat-006',
    'user-pat-006',
    'Casey',
    'Placeholder',
    '2000-04-25',
    24,
    'Female',
    'casey.placeholder@example.com',
    '+1-555-1011',
    '{"street": "6060 Mock Street", "city": "Mountain View", "state": "CA", "zip_code": "94040", "country": "USA"}'::jsonb,
    '{"name": "Skyler Placeholder", "relationship": "Sibling", "phone": "+1-555-1012"}'::jsonb,
    'A-',
    '["Shellfish"]'::jsonb,
    '[]'::jsonb,
    '{"provider": "Mock Insurance Group", "policy_number": "MCK-234567", "group_number": "GRP-006"}'::jsonb,
    true,
    CURRENT_TIMESTAMP - INTERVAL '10 days',
    CURRENT_TIMESTAMP
);

-- ========================================================================
-- APPOINTMENTS - Fictional Appointments (Past & Future)
-- ========================================================================

INSERT INTO appointments (appointment_id, patient_id, doctor_id, appointment_date, appointment_time, appointment_type, status, reason, notes, location, duration_minutes, is_active, created_at, updated_at)
VALUES
-- Completed past appointments
(
    gen_random_uuid(),
    'pat-001',
    'doc-001',
    CURRENT_DATE - INTERVAL '15 days',
    '10:00:00',
    'consultation',
    'completed',
    'Annual cardiology checkup',
    'Patient doing well, BP normal, continue current medications',
    'Bay Area Medical Center',
    45,
    true,
    CURRENT_TIMESTAMP - INTERVAL '15 days',
    CURRENT_TIMESTAMP - INTERVAL '15 days'
),
(
    gen_random_uuid(),
    'pat-002',
    'doc-002',
    CURRENT_DATE - INTERVAL '7 days',
    '14:30:00',
    'routine_checkup',
    'completed',
    'Child wellness visit',
    'Development on track, all vaccinations current',
    'Sunshine Community Clinic',
    30,
    true,
    CURRENT_TIMESTAMP - INTERVAL '7 days',
    CURRENT_TIMESTAMP - INTERVAL '7 days'
),
(
    gen_random_uuid(),
    'pat-003',
    'doc-003',
    CURRENT_DATE - INTERVAL '30 days',
    '11:00:00',
    'follow_up',
    'completed',
    'Migraine follow-up',
    'Medication adjustment effective, fewer episodes reported',
    'Bay Area Medical Center',
    30,
    true,
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    CURRENT_TIMESTAMP - INTERVAL '30 days'
),
-- Upcoming scheduled appointments
(
    gen_random_uuid(),
    'pat-004',
    'doc-004',
    CURRENT_DATE + INTERVAL '3 days',
    '09:00:00',
    'consultation',
    'scheduled',
    'Knee pain evaluation',
    NULL,
    'Bay Area Medical Center',
    45,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-005',
    'doc-005',
    CURRENT_DATE + INTERVAL '7 days',
    '15:00:00',
    'consultation',
    'confirmed',
    'Skin lesion examination',
    'Patient confirmed via SMS',
    'Sunshine Community Clinic',
    30,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-006',
    'doc-002',
    CURRENT_DATE + INTERVAL '14 days',
    '10:30:00',
    'routine_checkup',
    'scheduled',
    'Annual physical examination',
    NULL,
    'Sunshine Community Clinic',
    60,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-001',
    'doc-001',
    CURRENT_DATE + INTERVAL '90 days',
    '10:00:00',
    'follow_up',
    'scheduled',
    'Cardiology follow-up',
    NULL,
    'Bay Area Medical Center',
    30,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- ========================================================================
-- MEDICAL HISTORY - Fictional Medical Visit Records
-- ========================================================================

INSERT INTO medical_history (history_id, patient_id, doctor_id, doctor_name, visit_date, diagnosis, prescriptions, health_status, blood_pressure, symptoms, notes, follow_up_date, is_active, created_at, updated_at)
VALUES
(
    gen_random_uuid(),
    'pat-001',
    'doc-001',
    'Dr. Alexandra Rivers',
    CURRENT_DATE - INTERVAL '15 days',
    'Essential Hypertension - Well Controlled',
    '[{"medication_name": "Lisinopril", "dosage": "10mg", "frequency": "Once daily", "duration": "90 days", "instructions": "Take in the morning"}]'::jsonb,
    'Stable',
    '125/82',
    '[]'::jsonb,
    'Patient adherent to medication. BP well controlled. Continue current regimen.',
    CURRENT_DATE + INTERVAL '90 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '15 days',
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-003',
    'doc-003',
    'Dr. Catherine Wong',
    CURRENT_DATE - INTERVAL '30 days',
    'Migraine without Aura',
    '[{"medication_name": "Sumatriptan", "dosage": "50mg", "frequency": "As needed for migraine", "duration": "90 days", "instructions": "Take at onset of migraine symptoms"}]'::jsonb,
    'Improving',
    '118/76',
    '["Occasional headache"]'::jsonb,
    'Frequency of migraines reduced from 8/month to 2/month. Continue current treatment.',
    CURRENT_DATE + INTERVAL '60 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-004',
    'doc-005',
    'Dr. Elena Martinez',
    CURRENT_DATE - INTERVAL '45 days',
    'Mild Eczema',
    '[{"medication_name": "Hydrocortisone Cream", "dosage": "1%", "frequency": "Twice daily", "duration": "30 days", "instructions": "Apply to affected areas"}]'::jsonb,
    'Resolved',
    '120/78',
    '[]'::jsonb,
    'Eczema completely cleared. Advised on proper skin care routine.',
    NULL,
    true,
    CURRENT_TIMESTAMP - INTERVAL '45 days',
    CURRENT_TIMESTAMP
);

-- ========================================================================
-- PRESCRIPTIONS - Fictional Prescription Records
-- ========================================================================

INSERT INTO prescriptions (prescription_id, patient_id, doctor_id, medications, diagnosis, notes, prescribed_date, valid_until, is_active, created_at, updated_at)
VALUES
(
    gen_random_uuid(),
    'pat-001',
    'doc-001',
    '[
        {"name": "Lisinopril", "dosage": "10mg", "frequency": "Once daily", "duration": "90 days", "instructions": "Take in the morning with water"},
        {"name": "Aspirin", "dosage": "81mg", "frequency": "Once daily", "duration": "90 days", "instructions": "Take with food"}
    ]'::jsonb,
    'Essential Hypertension',
    'Continue current medication regimen. Monitor BP at home weekly.',
    CURRENT_DATE - INTERVAL '15 days',
    CURRENT_DATE + INTERVAL '75 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '15 days',
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-003',
    'doc-003',
    '[
        {"name": "Sumatriptan", "dosage": "50mg", "frequency": "As needed", "duration": "90 days", "instructions": "Take at onset of migraine. Max 200mg/day"}
    ]'::jsonb,
    'Migraine without Aura',
    'Keep headache diary. Avoid known triggers.',
    CURRENT_DATE - INTERVAL '30 days',
    CURRENT_DATE + INTERVAL '60 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-005',
    'doc-001',
    '[
        {"name": "Atorvastatin", "dosage": "20mg", "frequency": "Once daily", "duration": "90 days", "instructions": "Take in the evening"}
    ]'::jsonb,
    'Hyperlipidemia',
    'Recheck lipid panel in 3 months. Continue low-fat diet.',
    CURRENT_DATE - INTERVAL '20 days',
    CURRENT_DATE + INTERVAL '70 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '20 days',
    CURRENT_TIMESTAMP
);

-- ========================================================================
-- HEALTH VITALS - Fictional Vital Sign Measurements
-- ========================================================================

INSERT INTO health_vitals (vital_id, patient_id, recorded_by, vital_type, value, unit, recorded_at, notes, is_active, created_at, updated_at)
VALUES
-- Patient pat-001 vitals
(gen_random_uuid(), 'pat-001', 'user-doc-001', 'blood_pressure', '125/82', 'mmHg', CURRENT_TIMESTAMP - INTERVAL '15 days', 'Normal range', true, CURRENT_TIMESTAMP - INTERVAL '15 days', CURRENT_TIMESTAMP),
(gen_random_uuid(), 'pat-001', 'user-doc-001', 'heart_rate', '72', 'bpm', CURRENT_TIMESTAMP - INTERVAL '15 days', 'Regular rhythm', true, CURRENT_TIMESTAMP - INTERVAL '15 days', CURRENT_TIMESTAMP),
(gen_random_uuid(), 'pat-001', 'user-doc-001', 'temperature', '98.4', '°F', CURRENT_TIMESTAMP - INTERVAL '15 days', 'Normal', true, CURRENT_TIMESTAMP - INTERVAL '15 days', CURRENT_TIMESTAMP),
(gen_random_uuid(), 'pat-001', 'user-doc-001', 'weight', '175', 'lbs', CURRENT_TIMESTAMP - INTERVAL '15 days', 'Stable', true, CURRENT_TIMESTAMP - INTERVAL '15 days', CURRENT_TIMESTAMP),
(gen_random_uuid(), 'pat-001', 'user-doc-001', 'oxygen_saturation', '98', '%', CURRENT_TIMESTAMP - INTERVAL '15 days', 'Excellent', true, CURRENT_TIMESTAMP - INTERVAL '15 days', CURRENT_TIMESTAMP),

-- Patient pat-002 vitals
(gen_random_uuid(), 'pat-002', 'user-doc-002', 'blood_pressure', '118/75', 'mmHg', CURRENT_TIMESTAMP - INTERVAL '7 days', 'Normal', true, CURRENT_TIMESTAMP - INTERVAL '7 days', CURRENT_TIMESTAMP),
(gen_random_uuid(), 'pat-002', 'user-doc-002', 'heart_rate', '68', 'bpm', CURRENT_TIMESTAMP - INTERVAL '7 days', 'Normal', true, CURRENT_TIMESTAMP - INTERVAL '7 days', CURRENT_TIMESTAMP),
(gen_random_uuid(), 'pat-002', 'user-doc-002', 'temperature', '98.6', '°F', CURRENT_TIMESTAMP - INTERVAL '7 days', 'Normal', true, CURRENT_TIMESTAMP - INTERVAL '7 days', CURRENT_TIMESTAMP),
(gen_random_uuid(), 'pat-002', 'user-doc-002', 'weight', '145', 'lbs', CURRENT_TIMESTAMP - INTERVAL '7 days', 'Healthy weight', true, CURRENT_TIMESTAMP - INTERVAL '7 days', CURRENT_TIMESTAMP),

-- Patient pat-003 vitals
(gen_random_uuid(), 'pat-003', 'user-doc-003', 'blood_pressure', '118/76', 'mmHg', CURRENT_TIMESTAMP - INTERVAL '30 days', 'Normal', true, CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP),
(gen_random_uuid(), 'pat-003', 'user-doc-003', 'heart_rate', '75', 'bpm', CURRENT_TIMESTAMP - INTERVAL '30 days', 'Normal', true, CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP),
(gen_random_uuid(), 'pat-003', 'user-doc-003', 'blood_glucose', '105', 'mg/dL', CURRENT_TIMESTAMP - INTERVAL '30 days', 'Good control', true, CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP);

-- ========================================================================
-- MEDICAL REPORTS - Fictional Medical Test Reports
-- ========================================================================

INSERT INTO medical_reports (report_id, patient_id, doctor_id, report_type, title, content, file_url, report_date, is_active, created_at, updated_at)
VALUES
(
    gen_random_uuid(),
    'pat-001',
    'doc-001',
    'Blood Test',
    'Comprehensive Metabolic Panel - November 2024',
    'All values within normal limits. Glucose: 92 mg/dL, Creatinine: 0.9 mg/dL, eGFR: >60 mL/min',
    'https://storage.example.com/reports/cmp-001.pdf',
    CURRENT_DATE - INTERVAL '15 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '15 days',
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-001',
    'doc-001',
    'ECG',
    'Electrocardiogram Results',
    'Normal sinus rhythm. Rate 72 bpm. No ST-T wave changes. No arrhythmias detected.',
    'https://storage.example.com/reports/ecg-001.pdf',
    CURRENT_DATE - INTERVAL '15 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '15 days',
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-003',
    'doc-003',
    'MRI Scan',
    'Brain MRI - Headache Evaluation',
    'No acute intracranial abnormality. No mass effect. Ventricles normal in size.',
    'https://storage.example.com/reports/mri-001.pdf',
    CURRENT_DATE - INTERVAL '35 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '35 days',
    CURRENT_TIMESTAMP
),
(
    gen_random_uuid(),
    'pat-005',
    'doc-001',
    'Blood Test',
    'Lipid Panel Results',
    'Total Cholesterol: 245 mg/dL (High), LDL: 165 mg/dL (High), HDL: 45 mg/dL, Triglycerides: 175 mg/dL',
    'https://storage.example.com/reports/lipid-001.pdf',
    CURRENT_DATE - INTERVAL '20 days',
    true,
    CURRENT_TIMESTAMP - INTERVAL '20 days',
    CURRENT_TIMESTAMP
);

-- ========================================================================
-- VERIFICATION QUERIES
-- ========================================================================

-- Count records in each table
SELECT
    'organizations' as table_name, COUNT(*) as record_count FROM organizations
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'doctors', COUNT(*) FROM doctors
UNION ALL
SELECT 'patients', COUNT(*) FROM patients
UNION ALL
SELECT 'appointments', COUNT(*) FROM appointments
UNION ALL
SELECT 'medical_history', COUNT(*) FROM medical_history
UNION ALL
SELECT 'prescriptions', COUNT(*) FROM prescriptions
UNION ALL
SELECT 'health_vitals', COUNT(*) FROM health_vitals
UNION ALL
SELECT 'medical_reports', COUNT(*) FROM medical_reports;

-- Display sample data
SELECT
    first_name,
    last_name,
    specialization,
    email
FROM doctors
ORDER BY last_name;

SELECT
    first_name,
    last_name,
    gender,
    age,
    email
FROM patients
ORDER BY last_name;

-- ========================================================================
-- END OF SAFE DUMMY DATA ARTIFACT
-- ========================================================================
