# Production-Ready OCR & Document Understanding Mastery Challenge

# Step 2: Define Supported Documents & Extraction Schemas

## Overview

# Table of Contents

- [Overview](#overview)
- [1. Parent Response Schema](#1-parent-response-schema)
- [2. Standard Image Fields](#2-standard-image-fields)
- [3. Supported Documents](#3-supported-documents)
  - [3.1 Passport](#31-passport)
  - [3.2 Driver Licence](#32-driver-licence)
  - [3.3 Medicare Card](#33-medicare-card)
  - [3.4 Working With Children (WWC)](#34-working-with-children-wwc)
  - [3.5 IELTS Certificate](#35-ielts-certificate)
  - [3.6 Energy Bill](#36-energy-bill)
  - [3.7 Unknown Document](#37-unknown-document)

---

This section defines the supported document types and extraction schemas used in the OCR pipeline.

The schemas are designed to:
- standardize extracted outputs
- simplify backend validation
- support document classification
- improve OCR consistency
- reduce unnecessary complexity

---

# 1. Parent Response Schema

## Purpose

All OCR outputs must follow a common parent structure.

This allows:
- unified API responses
- easier frontend integration
- centralized error handling
- scalable multi-document support

## Parent Schema

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "partial", "failed", "unknown"],
      "title": "Processing Status",
      "required": true
    },

    "doc_type": {
      "type": "string",
      "title": "Document Type",
      "required": true
    },

    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "title": "Classification Confidence",
      "required": false
    },

    "message": {
      "type": "string",
      "title": "Message",
      "required": false
    },

    "error": {
      "type": ["string", "null"],
      "title": "Error Detail",
      "required": false
    },

    "data": {
      "type": ["object", "null"],
      "title": "Extracted Data",
      "required": true
    }
  }
}
```

---

# 2. Standard Image Fields

## Purpose

To keep all schemas consistent, every document should contain the same image field structure.

## Required Standard

```json
{
  "document_front": {
    "type": "array",
    "title": "Document Front Photo",
    "description": "Photo of the front side of the document",
    "items": { "type": "string" },
    "required": true
  },

  "document_back": {
    "type": "array",
    "title": "Document Back Photo",
    "description": "Photo of the back side of the document",
    "items": { "type": "string" },
    "required": false
  }
}
```

## Notes

Previous field names such as:
- commencement_document_front
- secondary_document_front
- unknown_document_front

should be standardized into:
- document_front
- document_back

Benefits:
- reusable frontend upload components
- simpler backend validation
- cleaner dataset structure
- easier maintenance

---

# 3. Supported Documents

---

# 3.1 Passport

## Description

International government-issued travel document.

## Important Fields

- identity information
- passport number
- nationality
- MRZ lines
- expiry date

## Schema

```json
{
  "title": "Passport",
  "type": "object",
  "properties": {
    "passport_first_name": {
      "type": "string",
      "title": "First Name",
      "required": true
    },

    "passport_middle_name": {
      "type": ["string", "null"],
      "title": "Middle Name",
      "required": false
    },

    "passport_last_name": {
      "type": "string",
      "title": "Last Name",
      "required": true
    },

    "passport_number": {
      "type": "string",
      "title": "Passport Number",
      "required": true
    },

    "passport_date_of_birth": {
      "type": "string",
      "format": "date",
      "required": true
    },

    "passport_expiry_date": {
      "type": "string",
      "format": "date",
      "required": true
    },

    "passport_nationality": {
      "type": "string",
      "required": true
    },

    "passport_gender": {
      "type": "string",
      "required": true
    },

    "passport_place_of_birth": {
      "type": "string",
      "required": true
    },

    "passport_mrz_line1": {
      "type": ["string", "null"],
      "required": false
    },

    "passport_mrz_line2": {
      "type": ["string", "null"],
      "required": false
    },

    "document_front": {
      "type": "array",
      "title": "Document Front Photo",
      "description": "Photo of the passport front page",
      "items": { "type": "string" },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Document Back Photo",
      "description": "Photo of the passport back page",
      "items": { "type": "string" },
      "required": false
    }
  }
}
```

---

# 3.2 Driver Licence

## Description

Official licence allowing a person to drive vehicles.

## Notes

Optional fields with low OCR value can be removed:
- licence conditions
- card number
- licence type

These fields can be generated or handled later in backend systems.

## Schema

```json
{
  "title": "Australian Driver Licence",
  "type": "object",
  "properties": {
    "driver_licence_first_name": {
      "type": "string",
      "required": true
    },

    "driver_licence_middle_name": {
      "type": ["string", "null"],
      "required": false
    },

    "driver_licence_last_name": {
      "type": "string",
      "required": true
    },

    "driver_licence_number": {
      "type": "string",
      "required": true
    },

    "driver_licence_date_of_birth": {
      "type": "string",
      "format": "date",
      "required": true
    },

    "driver_licence_expiry_date": {
      "type": "string",
      "format": "date",
      "required": true
    },

    "driver_licence_state": {
      "type": "string",
      "required": true
    },

    "driver_licence_address": {
      "type": ["string", "null"],
      "required": false
    },

    "document_front": {
      "type": "array",
      "title": "Document Front Photo",
      "description": "Photo of the front of the driver's licence",
      "items": { "type": "string" },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Document Back Photo",
      "description": "Photo of the back of the driver's licence",
      "items": { "type": "string" },
      "required": false
    }
  }
}
```

---

# 3.3 Medicare Card

## Description

Australian healthcare identification card.

## Notes

Non-essential fields may be removed:
- card colour

## Schema

```json
{
  "title": "Medicare Card",
  "type": "object",
  "properties": {
    "medicare_card_number": {
      "type": "string",
      "required": true
    },

    "medicare_card_first_name": {
      "type": "string",
      "required": true
    },

    "medicare_card_last_name": {
      "type": "string",
      "required": true
    },

    "medicare_card_expiry_date": {
      "type": "string",
      "required": true
    },

    "medicare_card_position": {
      "type": "string",
      "required": true
    },

    "document_front": {
      "type": "array",
      "title": "Document Front Photo",
      "description": "Photo of the Medicare card front side",
      "items": { "type": "string" },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Document Back Photo",
      "description": "Photo of the Medicare card back side",
      "items": { "type": "string" },
      "required": false
    }
  }
}
```

---

# 3.4 Working With Children (WWC)

## Description

Background-check clearance card.

## Schema

```json
{
  "title": "Working With Children (WWC) Card",
  "type": "object",
  "properties": {
    "wwc_first_name": {
      "type": "string",
      "required": true
    },

    "wwc_last_name": {
      "type": "string",
      "required": true
    },

    "wwc_card_number": {
      "type": "string",
      "required": true
    },

    "wwc_expiry_date": {
      "type": "string",
      "required": true
    },

    "wwc_state": {
      "type": "string",
      "required": true
    },

    "document_front": {
      "type": "array",
      "title": "Document Front Photo",
      "description": "Photo of the WWC card front side",
      "items": { "type": "string" },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Document Back Photo",
      "description": "Photo of the WWC card back side",
      "items": { "type": "string" },
      "required": false
    }
  }
}
```

---

# 3.5 IELTS Certificate

## Description

English language proficiency certificate.

## Notes

Detailed skill scores may be optional for MVP extraction.

## Schema

```json
{
  "title": "IELTS Test Report Form",
  "type": "object",
  "properties": {
    "ielts_first_name": {
      "type": "string",
      "required": true
    },

    "ielts_last_name": {
      "type": "string",
      "required": true
    },

    "ielts_test_date": {
      "type": "string",
      "required": true
    },

    "ielts_trf_number": {
      "type": "string",
      "required": true
    },

    "ielts_test_type": {
      "type": "string",
      "required": true
    },

    "ielts_overall_band": {
      "type": "number",
      "required": true
    },

    "document_front": {
      "type": "array",
      "title": "Document Front Photo",
      "description": "Photo of the IELTS certificate front side",
      "items": { "type": "string" },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Document Back Photo",
      "description": "Photo of the IELTS certificate back side",
      "items": { "type": "string" },
      "required": false
    }
  }
}
```

---

# 3.6 Energy Bill

## Description

Household electricity or gas bill.

## Notes

Highly detailed billing fields can be removed to simplify OCR extraction.

## Schema

```json
{
  "title": "Australian Household Energy Bill",
  "type": "object",
  "properties": {
    "energy_bill_account_holder_name": {
      "type": "string",
      "required": true
    },

    "energy_bill_account_number": {
      "type": "string",
      "required": true
    },

    "energy_bill_retailer_name": {
      "type": "string",
      "required": true
    },

    "energy_bill_service_address": {
      "type": "string",
      "required": true
    },

    "energy_bill_due_date": {
      "type": "string",
      "required": true
    },

    "energy_bill_total_amount_due": {
      "type": "number",
      "required": true
    },

    "document_front": {
      "type": "array",
      "title": "Document Front Photo",
      "description": "Photo of the energy bill front page",
      "items": { "type": "string" },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Document Back Photo",
      "description": "Photo of additional bill pages",
      "items": { "type": "string" },
      "required": false
    }
  }
}
```

---

# 3.7 Unknown Document

## Description

Fallback schema for unsupported or failed document classification.

## Schema

```json
{
  "title": "Unknown Document",
  "type": "object",
  "properties": {
    "unknown_raw_text": {
      "type": ["string", "null"],
      "required": true
    },

    "unknown_reason": {
      "type": "string",
      "required": true
    },

    "unknown_classifier_top_guess": {
      "type": ["string", "null"],
      "required": false
    },

    "unknown_classifier_confidence": {
      "type": ["number", "null"],
      "required": false
    },

    "document_front": {
      "type": "array",
      "title": "Document Front Photo",
      "description": "Photo of the unknown document front side",
      "items": { "type": "string" },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Document Back Photo",
      "description": "Photo of the unknown document back side",
      "items": { "type": "string" },
      "required": false
    }
  }
}
```

---
