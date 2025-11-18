-- Fix: Create doctor record for user who is marked as onboarded but missing doctor profile
INSERT INTO doctors (doctor_id, user_id, first_name, last_name, specialization, license_number, email, is_active, created_at, updated_at)
VALUES (
  '91019b11-11cd-496f-86dc-c1a252a0c6ab',
  '91019b11-11cd-496f-86dc-c1a252a0c6ab',
  'K',
  'Mani',
  'General Practice',
  'MD910191',
  'manideepk70@gmail.com',
  true,
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
);

SELECT 'Doctor record created successfully!' as message;
