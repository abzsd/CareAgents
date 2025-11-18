# Onboarding API Guide

## Overview
The onboarding system allows users to create their patient or doctor profiles and link them to their user accounts. **All fields except required ones are optional**, allowing for flexible onboarding flows.

---

## Patient Onboarding

### Endpoint
```
POST /api/v1/onboarding/patient
```

### Required Fields (Minimal)
Only these fields are **required** for patient onboarding:

```json
{
  "user_id": "user-uuid-from-firebase",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "gender": "Male"
}
```

**Gender Options**: `"Male"`, `"Female"`, `"Other"`, `"Prefer not to say"`

### All Optional Fields
```json
{
  "phone": "+1234567890",
  "email": "john.doe@example.com",
  "blood_type": "A+",
  "allergies": ["Penicillin", "Peanuts"],
  "chronic_conditions": ["Hypertension", "Diabetes"],
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

### Endpoint
```
POST /api/v1/onboarding/doctor
```

### Required Fields (Minimal)
```json
{
  "user_id": "user-uuid-from-firebase",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "specialization": "Cardiology",
  "license_number": "MD123456"
}
```

### All Optional Fields
```json
{
  "phone": "+1234567890",
  "email": "dr.johnson@hospital.com",
  "experience_years": 10,
  "address": {
    "street": "456 Medical Plaza",
    "city": "New York",
    "state": "NY",
    "zip_code": "10002"
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
      "year": 2015
    }
  ]
}
```

---

## Check Onboarding Status

### Endpoint
```
GET /api/v1/onboarding/status/{user_id}
```

### Response
```json
{
  "is_onboarded": true,
  "user": { ... },
  "profile": { ... }
}
```

---

## Summary

### Patient Required Fields
- `user_id`, `first_name`, `last_name`, `date_of_birth`, `gender`

### Doctor Required Fields
- `user_id`, `first_name`, `last_name`, `specialization`, `license_number`

**Everything else is optional!** The backend uses `exclude_none=True` to ignore null/undefined values.
