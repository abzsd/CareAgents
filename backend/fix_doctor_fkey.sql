-- Fix foreign key constraint for medical_history.doctor_id
-- Make doctor_id nullable to allow medical history creation without a doctor record

-- Drop the existing foreign key constraint
ALTER TABLE medical_history
DROP CONSTRAINT IF EXISTS medical_history_doctor_id_fkey;

-- Re-add the foreign key constraint but make the column nullable
ALTER TABLE medical_history
ALTER COLUMN doctor_id DROP NOT NULL;

-- Add back the foreign key constraint (will be null-safe)
ALTER TABLE medical_history
ADD CONSTRAINT medical_history_doctor_id_fkey
FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id);

-- Display confirmation
SELECT 'Foreign key constraint updated successfully. doctor_id is now nullable.' AS status;
