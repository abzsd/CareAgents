-- Seed sample doctors into the database
-- Delete existing doctors first
DELETE FROM doctors;

-- Insert sample doctors
INSERT INTO doctors (
    doctor_id, first_name, last_name, email, phone,
    specialization, sub_specializations, license_number, license_state,
    qualifications, years_of_experience, consultation_fee,
    availability, languages_spoken, rating, total_patients_treated,
    is_active, created_at, updated_at
) VALUES
(
    gen_random_uuid(), 'Sarah', 'Johnson', 'sarah.johnson@hospital.com', '+1-555-0101',
    'Cardiology', '["Interventional Cardiology", "Heart Failure"]'::jsonb, 'MD-CA-123456', 'California',
    '[{"degree": "MD", "institution": "Stanford Medical School", "year": 2005}, {"degree": "Fellowship in Cardiology", "institution": "Mayo Clinic", "year": 2010}]'::jsonb,
    15, 250.00,
    '[{"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"}, {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"}, {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"}, {"day_of_week": "Thursday", "start_time": "09:00", "end_time": "17:00"}]'::jsonb,
    '["English", "Spanish"]'::jsonb, 4.8, 1500, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    gen_random_uuid(), 'Michael', 'Chen', 'michael.chen@hospital.com', '+1-555-0102',
    'Neurology', '["Epilepsy", "Movement Disorders"]'::jsonb, 'MD-CA-234567', 'California',
    '[{"degree": "MD", "institution": "Harvard Medical School", "year": 2008}, {"degree": "Fellowship in Neurology", "institution": "Johns Hopkins", "year": 2012}]'::jsonb,
    12, 275.00,
    '[{"day_of_week": "Monday", "start_time": "10:00", "end_time": "18:00"}, {"day_of_week": "Wednesday", "start_time": "10:00", "end_time": "18:00"}, {"day_of_week": "Friday", "start_time": "10:00", "end_time": "18:00"}]'::jsonb,
    '["English", "Mandarin"]'::jsonb, 4.9, 1200, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    gen_random_uuid(), 'Emily', 'Rodriguez', 'emily.rodriguez@hospital.com', '+1-555-0103',
    'Pediatrics', '["Neonatology", "Developmental Pediatrics"]'::jsonb, 'MD-CA-345678', 'California',
    '[{"degree": "MD", "institution": "UCSF Medical School", "year": 2010}, {"degree": "Fellowship in Pediatrics", "institution": "Children''s Hospital Boston", "year": 2014}]'::jsonb,
    10, 200.00,
    '[{"day_of_week": "Monday", "start_time": "08:00", "end_time": "16:00"}, {"day_of_week": "Tuesday", "start_time": "08:00", "end_time": "16:00"}, {"day_of_week": "Thursday", "start_time": "08:00", "end_time": "16:00"}, {"day_of_week": "Friday", "start_time": "08:00", "end_time": "14:00"}]'::jsonb,
    '["English", "Spanish", "Portuguese"]'::jsonb, 4.7, 2000, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    gen_random_uuid(), 'David', 'Patel', 'david.patel@hospital.com', '+1-555-0104',
    'Orthopedics', '["Sports Medicine", "Joint Replacement"]'::jsonb, 'MD-CA-456789', 'California',
    '[{"degree": "MD", "institution": "UCLA Medical School", "year": 2007}, {"degree": "Fellowship in Orthopedic Surgery", "institution": "Cleveland Clinic", "year": 2013}]'::jsonb,
    13, 300.00,
    '[{"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"}, {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"}, {"day_of_week": "Thursday", "start_time": "09:00", "end_time": "17:00"}]'::jsonb,
    '["English", "Hindi", "Gujarati"]'::jsonb, 4.6, 1800, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    gen_random_uuid(), 'Lisa', 'Williams', 'lisa.williams@hospital.com', '+1-555-0105',
    'Dermatology', '["Cosmetic Dermatology", "Skin Cancer"]'::jsonb, 'MD-CA-567890', 'California',
    '[{"degree": "MD", "institution": "USC Medical School", "year": 2009}, {"degree": "Fellowship in Dermatology", "institution": "NYU Langone", "year": 2013}]'::jsonb,
    11, 225.00,
    '[{"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"}, {"day_of_week": "Tuesday", "start_time": "09:00", "end_time": "17:00"}, {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "13:00"}, {"day_of_week": "Friday", "start_time": "09:00", "end_time": "17:00"}]'::jsonb,
    '["English"]'::jsonb, 4.9, 2500, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    gen_random_uuid(), 'James', 'Thompson', 'james.thompson@hospital.com', '+1-555-0106',
    'General Practice', '["Family Medicine", "Preventive Care"]'::jsonb, 'MD-CA-678901', 'California',
    '[{"degree": "MD", "institution": "UC San Diego Medical School", "year": 2012}, {"degree": "Residency in Family Medicine", "institution": "Kaiser Permanente", "year": 2015}]'::jsonb,
    8, 150.00,
    '[{"day_of_week": "Monday", "start_time": "08:00", "end_time": "18:00"}, {"day_of_week": "Tuesday", "start_time": "08:00", "end_time": "18:00"}, {"day_of_week": "Wednesday", "start_time": "08:00", "end_time": "18:00"}, {"day_of_week": "Thursday", "start_time": "08:00", "end_time": "18:00"}, {"day_of_week": "Friday", "start_time": "08:00", "end_time": "18:00"}]'::jsonb,
    '["English"]'::jsonb, 4.5, 3000, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    gen_random_uuid(), 'Rachel', 'Kim', 'rachel.kim@hospital.com', '+1-555-0107',
    'Psychiatry', '["Anxiety Disorders", "Depression", "ADHD"]'::jsonb, 'MD-CA-789012', 'California',
    '[{"degree": "MD", "institution": "Yale Medical School", "year": 2011}, {"degree": "Residency in Psychiatry", "institution": "Massachusetts General Hospital", "year": 2015}]'::jsonb,
    9, 280.00,
    '[{"day_of_week": "Monday", "start_time": "10:00", "end_time": "19:00"}, {"day_of_week": "Tuesday", "start_time": "10:00", "end_time": "19:00"}, {"day_of_week": "Thursday", "start_time": "10:00", "end_time": "19:00"}]'::jsonb,
    '["English", "Korean"]'::jsonb, 4.8, 800, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
),
(
    gen_random_uuid(), 'Robert', 'Martinez', 'robert.martinez@hospital.com', '+1-555-0108',
    'Gastroenterology', '["IBD", "Liver Diseases", "Endoscopy"]'::jsonb, 'MD-CA-890123', 'California',
    '[{"degree": "MD", "institution": "Columbia Medical School", "year": 2006}, {"degree": "Fellowship in Gastroenterology", "institution": "University of Michigan", "year": 2011}]'::jsonb,
    14, 260.00,
    '[{"day_of_week": "Monday", "start_time": "09:00", "end_time": "17:00"}, {"day_of_week": "Wednesday", "start_time": "09:00", "end_time": "17:00"}, {"day_of_week": "Friday", "start_time": "09:00", "end_time": "17:00"}]'::jsonb,
    '["English", "Spanish"]'::jsonb, 4.7, 1600, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Verify insertion
SELECT
    doctor_id,
    first_name,
    last_name,
    specialization,
    rating,
    total_patients_treated
FROM doctors
ORDER BY specialization;
