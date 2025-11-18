# Onboarding with Optional Fields

## Overview
The onboarding system is designed to be **flexible** and accept **optional data**. You can send as much or as little information as you have available during onboarding.

## How Optional Fields Work

### ✅ Automatic Handling
- All optional fields use `exclude_none=True` when processing data
- If you don't send a field, it won't be included in the database insert
- Empty arrays like `[]` are preserved and stored correctly
- Nested objects (address, emergency_contact, insurance_info) are completely optional

---

## Patient Onboarding

### Minimum Required Fields
Only these fields are **required** for patient onboarding:
```json
{
  "user_id": "user-uuid",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male"
}
```

### All Optional Fields
You can include any of these fields as needed:

```json
{
  "user_id": "user-uuid",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male",

  // Optional basic info
  "phone": "+1234567890",
  "email": "john.doe@example.com",
  "blood_type": "A+",

  // Optional medical info
  "allergies": ["Penicillin", "Pollen"],
  "chronic_conditions": ["Hypertension", "Diabetes"],

  // Optional address (can send all or some fields)
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "country": "USA"
  },

  // Optional emergency contact (can send all or some fields)
  "emergency_contact": {
    "name": "Jane Doe",
    "relationship": "Spouse",
    "phone": "+1234567891"
  },

  // Optional insurance info (can send all or some fields)
  "insurance_info": {
    "provider": "Blue Cross",
    "policy_number": "BC123456",
    "group_number": "GRP789"
  }
}
```

### Examples of Valid Patient Onboarding Requests

#### Example 1: Minimum Required Only
```json
{
  "user_id": "abc-123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male"
}
```

#### Example 2: With Some Optional Fields
```json
{
  "user_id": "abc-123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male",
  "phone": "+1234567890",
  "email": "john@example.com"
}
```

#### Example 3: With Medical History
```json
{
  "user_id": "abc-123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male",
  "allergies": ["Penicillin"],
  "chronic_conditions": []
}
```

#### Example 4: With Partial Address
```json
{
  "user_id": "abc-123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male",
  "address": {
    "city": "New York",
    "state": "NY"
  }
}
```

#### Example 5: Complete Information
```json
{
  "user_id": "abc-123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male",
  "phone": "+1234567890",
  "email": "john@example.com",
  "blood_type": "A+",
  "allergies": ["Penicillin", "Pollen"],
  "chronic_conditions": ["Hypertension"],
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "country": "USA"
  },
  "emergency_contact": {
    "name": "Jane Doe",
    "relationship": "Spouse",
    "phone": "+1234567891"
  },
  "insurance_info": {
    "provider": "Blue Cross",
    "policy_number": "BC123456",
    "group_number": "GRP789"
  }
}
```

---

## Doctor Onboarding

### Minimum Required Fields
Only these fields are **required** for doctor onboarding:
```json
{
  "user_id": "user-uuid",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "specialization": "Cardiology",
  "license_number": "MD123456"
}
```

### All Optional Fields
You can include any of these fields as needed:

```json
{
  "user_id": "user-uuid",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "specialization": "Cardiology",
  "license_number": "MD123456",

  // Optional contact info
  "phone": "+1234567890",
  "email": "dr.johnson@hospital.com",

  // Optional professional info
  "experience_years": 10,

  // Optional address (can send all or some fields)
  "address": {
    "street": "456 Medical Plaza",
    "city": "New York",
    "state": "NY",
    "zip_code": "10002",
    "country": "USA"
  },

  // Optional education (array, can be empty or have multiple entries)
  "education": [
    {
      "degree": "MD",
      "institution": "Harvard Medical School",
      "year": 2010
    },
    {
      "degree": "Bachelor of Science",
      "institution": "MIT",
      "year": 2006
    }
  ],

  // Optional certifications (array, can be empty or have multiple entries)
  "certifications": [
    {
      "name": "Board Certified Cardiologist",
      "issuer": "American Board of Cardiology",
      "year": 2012
    }
  ]
}
```

### Examples of Valid Doctor Onboarding Requests

#### Example 1: Minimum Required Only
```json
{
  "user_id": "doc-456",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "specialization": "Cardiology",
  "license_number": "MD123456"
}
```

#### Example 2: With Contact Info
```json
{
  "user_id": "doc-456",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "specialization": "Cardiology",
  "license_number": "MD123456",
  "phone": "+1234567890",
  "email": "dr.johnson@hospital.com"
}
```

#### Example 3: With Education Only
```json
{
  "user_id": "doc-456",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "specialization": "Cardiology",
  "license_number": "MD123456",
  "education": [
    {
      "degree": "MD",
      "institution": "Harvard Medical School",
      "year": 2010
    }
  ]
}
```

#### Example 4: With Empty Arrays (Also Valid!)
```json
{
  "user_id": "doc-456",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "specialization": "Cardiology",
  "license_number": "MD123456",
  "education": [],
  "certifications": []
}
```

#### Example 5: Complete Information
```json
{
  "user_id": "doc-456",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "specialization": "Cardiology",
  "license_number": "MD123456",
  "phone": "+1234567890",
  "email": "dr.johnson@hospital.com",
  "experience_years": 10,
  "address": {
    "street": "456 Medical Plaza",
    "city": "New York",
    "state": "NY",
    "zip_code": "10002",
    "country": "USA"
  },
  "education": [
    {
      "degree": "MD",
      "institution": "Harvard Medical School",
      "year": 2010
    }
  ],
  "certifications": [
    {
      "name": "Board Certified Cardiologist",
      "issuer": "American Board of Cardiology",
      "year": 2012
    }
  ]
}
```

---

## Progressive Onboarding Strategy

You can implement a **multi-step onboarding flow** where you collect information gradually:

### Step 1: Basic Information (Required)
```json
POST /api/v1/onboarding/patient
{
  "user_id": "user-123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male"
}
```

### Step 2: Update with Contact Info (Later)
```json
PUT /api/v1/patients/{patient_id}
{
  "phone": "+1234567890",
  "email": "john@example.com"
}
```

### Step 3: Update with Medical Info (Even Later)
```json
PUT /api/v1/patients/{patient_id}
{
  "allergies": ["Penicillin"],
  "chronic_conditions": ["Hypertension"],
  "blood_type": "A+"
}
```

---

## Field Validation

### Gender Field
Accepts these values:
- `"Male"`
- `"Female"`
- `"Other"`
- `"Prefer not to say"`

Any other value defaults to `"Prefer not to say"`

### Blood Type Field (Optional)
Accepts these values:
- `"A+"`, `"A-"`
- `"B+"`, `"B-"`
- `"AB+"`, `"AB-"`
- `"O+"`, `"O-"`

Invalid values are ignored (field remains empty)

### Date of Birth
- Format: `"YYYY-MM-DD"`
- Example: `"1990-01-15"`
- Age is automatically calculated from date of birth

### Arrays (allergies, chronic_conditions, education, certifications)
- Can be `[]` (empty array)
- Can be omitted entirely
- Can contain one or more items

---

## Frontend Integration Examples

### Minimal Patient Onboarding
```typescript
const onboardPatient = async (userId: string, basicInfo: any) => {
  const response = await fetch('/api/v1/onboarding/patient', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      first_name: basicInfo.firstName,
      last_name: basicInfo.lastName,
      date_of_birth: basicInfo.dateOfBirth,
      gender: basicInfo.gender
      // That's it! No other fields required
    })
  });

  return await response.json();
};
```

### Progressive Patient Onboarding
```typescript
// Step 1: Basic info
const onboardBasic = async (userId: string, data: any) => {
  return await fetch('/api/v1/onboarding/patient', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      ...data  // Only send what you have
    })
  });
};

// Step 2: Add more info later
const updatePatient = async (patientId: string, additionalData: any) => {
  return await fetch(`/api/v1/patients/${patientId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(additionalData)
  });
};
```

### Flexible Form Handling
```typescript
const handleOnboarding = async (formData: any) => {
  // Build payload dynamically based on what user filled out
  const payload: any = {
    user_id: user.uid,
    first_name: formData.firstName,
    last_name: formData.lastName,
    date_of_birth: formData.dateOfBirth,
    gender: formData.gender
  };

  // Only add optional fields if they have values
  if (formData.phone) payload.phone = formData.phone;
  if (formData.email) payload.email = formData.email;
  if (formData.bloodType) payload.blood_type = formData.bloodType;

  // Arrays: only add if not empty
  if (formData.allergies?.length > 0) {
    payload.allergies = formData.allergies;
  }

  if (formData.chronicConditions?.length > 0) {
    payload.chronic_conditions = formData.chronicConditions;
  }

  // Nested objects: only add if any field is filled
  if (formData.address?.city || formData.address?.state) {
    payload.address = formData.address;
  }

  const response = await fetch('/api/v1/onboarding/patient', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  return await response.json();
};
```

---

## Error Handling

### Missing Required Fields
```json
// Request
{
  "user_id": "user-123",
  "first_name": "John"
  // Missing: last_name, date_of_birth, gender
}

// Response (422 Unprocessable Entity)
{
  "detail": [
    {
      "loc": ["body", "last_name"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "date_of_birth"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "gender"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Invalid Data Types
```json
// Request
{
  "user_id": "user-123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "invalid-date",
  "gender": "Male"
}

// Response (422 Unprocessable Entity)
{
  "detail": [
    {
      "loc": ["body", "date_of_birth"],
      "msg": "invalid date format",
      "type": "value_error.date"
    }
  ]
}
```

---

## Key Benefits

✅ **Flexibility**: Send only what you have
✅ **No Waste**: `exclude_none=True` prevents storing unnecessary null values
✅ **Progressive**: Can complete onboarding in multiple steps
✅ **Type Safe**: Pydantic validates all data types
✅ **User Friendly**: Users can skip optional fields without errors
✅ **Database Efficient**: Only stores provided data

---

## Summary

### Patient Onboarding
- **Required**: `user_id`, `first_name`, `last_name`, `date_of_birth`, `gender`
- **Optional**: Everything else (phone, email, blood_type, allergies, chronic_conditions, address, emergency_contact, insurance_info)

### Doctor Onboarding
- **Required**: `user_id`, `first_name`, `last_name`, `specialization`, `license_number`
- **Optional**: Everything else (phone, email, experience_years, address, education, certifications)

### Remember
- You can send **as little or as much** data as you have
- Empty arrays `[]` are valid and will be stored
- Omitted fields won't be included in the database
- Nested objects can have partial data
- You can always update the profile later with more information

---

## Quick Reference

```bash
# Minimum patient onboarding
curl -X POST http://localhost:8000/api/v1/onboarding/patient \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-15",
    "gender": "Male"
  }'

# Minimum doctor onboarding
curl -X POST http://localhost:8000/api/v1/onboarding/doctor \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "doc-456",
    "first_name": "Sarah",
    "last_name": "Johnson",
    "specialization": "Cardiology",
    "license_number": "MD123456"
  }'
```

That's it! The system is designed to work with whatever data you can provide. 🎉
