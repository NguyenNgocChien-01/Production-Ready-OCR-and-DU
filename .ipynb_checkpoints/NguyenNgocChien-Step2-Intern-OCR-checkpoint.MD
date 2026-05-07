# Production-Ready OCR & Document Understanding Mastery Challenge

# Step 2: Define Supported Documents & Extraction Schemas

---

# Overview

This document defines all supported document types and standardized extraction schemas used in the OCR and Document Understanding pipeline.

The goal of these schemas is to create a scalable, production-ready OCR architecture that supports:
- standardized API outputs
- simplified backend validation
- reliable frontend integration
- document classification
- structured data extraction
- OCR quality consistency
- easier future expansion

All extracted outputs must follow a common response structure to ensure consistency across all document types.

---

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

# 1. Parent Response Schema

## Purpose

All OCR outputs must follow a shared parent schema.

This provides:
- unified API responses
- easier frontend rendering
- centralized error handling
- scalable document support
- easier monitoring and debugging
- simplified downstream processing

The `data` field contains the extracted fields for the detected document type.

---

# Parent Response Schema

```json
{
  "type": "object",
  "title": "OCR Parent Response",
  "description": "Standard response structure for all OCR document extraction outputs",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "partial", "failed", "unknown"],
      "title": "Processing Status",
      "description": "Overall extraction status returned by the OCR pipeline",
      "required": true
    },

    "doc_type": {
      "type": "string",
      "title": "Document Type",
      "description": "Detected document classification label",
      "required": true
    },

    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "title": "Classification Confidence",
      "description": "Confidence score returned by the document classifier",
      "required": false
    },

    "message": {
      "type": "string",
      "title": "Processing Message",
      "description": "Optional informational message returned during processing",
      "required": false
    },

    "error": {
      "type": ["string", "null"],
      "title": "Error Detail",
      "description": "Detailed error message when extraction fails",
      "required": false
    },

    "data": {
      "type": ["object", "null"],
      "title": "Extracted Data",
      "description": "Structured extracted fields based on the detected document schema",
      "required": true
    }
  }
}
```

---

# 2. Standard Image Fields

## Purpose

To maintain consistency across all document schemas, every document must use the same image field structure.

These fields store image references, uploaded image paths, cloud storage URLs, or base64 image data depending on system architecture.

---

# Standard Image Field Schema

```json
{
  "document_front": {
    "type": "array",
    "title": "Document Front Photo",
    "description": "Image list containing the front side of the document",
    "items": {
      "type": "string",
      "description": "Image path, URL, or base64 string"
    },
    "required": true
  },

  "document_back": {
    "type": "array",
    "title": "Document Back Photo",
    "description": "Image list containing the back side of the document",
    "items": {
      "type": "string",
      "description": "Image path, URL, or base64 string"
    },
    "required": false
  }
}
```

---

# 3. Supported Documents

---

# 3.1 Passport

## Description

A passport is an official government-issued international travel and identity document.

Passports are commonly used for:
- identity verification
- international travel
- visa applications
- KYC verification
- onboarding workflows

The OCR system should prioritize high-confidence extraction of identity fields and MRZ information.

---

## Important Extraction Fields

- first name
- middle name
- last name
- passport number
- nationality
- gender
- date of birth
- expiry date
- place of birth
- MRZ lines

---

## Passport Schema

```json
{
  "title": "Passport",
  "description": "Structured extraction schema for international passports",
  "type": "object",
  "properties": {
    "passport_first_name": {
      "type": "string",
      "title": "First Name",
      "description": "Passport holder first name",
      "required": true
    },

    "passport_middle_name": {
      "type": ["string", "null"],
      "title": "Middle Name",
      "description": "Passport holder middle name",
      "required": false
    },

    "passport_last_name": {
      "type": "string",
      "title": "Last Name",
      "description": "Passport holder last name",
      "required": true
    },

    "passport_number": {
      "type": "string",
      "title": "Passport Number",
      "description": "Unique passport identification number",
      "required": true
    },

    "passport_date_of_birth": {
      "type": "string",
      "format": "date",
      "title": "Date of Birth",
      "description": "Passport holder birth date",
      "required": true
    },

    "passport_expiry_date": {
      "type": "string",
      "format": "date",
      "title": "Expiry Date",
      "description": "Passport expiration date",
      "required": true
    },

    "passport_nationality": {
      "type": "string",
      "title": "Nationality",
      "description": "Country nationality shown on passport",
      "required": true
    },

    "passport_gender": {
      "type": "string",
      "title": "Gender",
      "description": "Gender shown on passport",
      "required": true
    },

    "passport_place_of_birth": {
      "type": "string",
      "title": "Place of Birth",
      "description": "Birth place shown on passport",
      "required": true
    },

    "passport_mrz_line1": {
      "type": ["string", "null"],
      "title": "MRZ Line 1",
      "description": "First machine-readable zone line",
      "required": false
    },

    "passport_mrz_line2": {
      "type": ["string", "null"],
      "title": "MRZ Line 2",
      "description": "Second machine-readable zone line",
      "required": false
    },

    "document_front": {
      "type": "array",
      "title": "Passport Front Image",
      "description": "Image list containing the passport information page",
      "items": {
        "type": "string"
      },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Passport Back Image",
      "description": "Optional additional passport images",
      "items": {
        "type": "string"
      },
      "required": false
    }
  }
}
```

---

# 3.2 Driver Licence

## Description

An official government-issued licence allowing a person to legally operate vehicles.

Driver licences are widely used for:
- identity verification
- age verification
- onboarding systems
- address verification
- KYC workflows

Optional low-value OCR fields may be excluded during MVP implementation to simplify extraction complexity.

---

## Important Extraction Fields

- licence holder name
- licence number
- date of birth
- expiry date
- issuing state
- residential address

---

## Driver Licence Schema

```json
{
  "title": "Australian Driver Licence",
  "description": "Structured extraction schema for Australian driver licences",
  "type": "object",
  "properties": {
    "driver_licence_first_name": {
      "type": "string",
      "title": "First Name",
      "description": "Driver first name",
      "required": true
    },

    "driver_licence_middle_name": {
      "type": ["string", "null"],
      "title": "Middle Name",
      "description": "Driver middle name",
      "required": false
    },

    "driver_licence_last_name": {
      "type": "string",
      "title": "Last Name",
      "description": "Driver last name",
      "required": true
    },

    "driver_licence_number": {
      "type": "string",
      "title": "Licence Number",
      "description": "Unique driver licence number",
      "required": true
    },

    "driver_licence_date_of_birth": {
      "type": "string",
      "format": "date",
      "title": "Date of Birth",
      "description": "Driver birth date",
      "required": true
    },

    "driver_licence_expiry_date": {
      "type": "string",
      "format": "date",
      "title": "Expiry Date",
      "description": "Licence expiration date",
      "required": true
    },

    "driver_licence_state": {
      "type": "string",
      "title": "Issuing State",
      "description": "Australian state or territory issuing the licence",
      "required": true
    },

    "driver_licence_address": {
      "type": ["string", "null"],
      "title": "Residential Address",
      "description": "Residential address shown on licence",
      "required": false
    },

    "document_front": {
      "type": "array",
      "title": "Licence Front Image",
      "description": "Front side image of the driver licence",
      "items": {
        "type": "string"
      },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Licence Back Image",
      "description": "Back side image of the driver licence",
      "items": {
        "type": "string"
      },
      "required": false
    }
  }
}
```

---

# 3.3 Medicare Card

## Description

An Australian healthcare identification card used for accessing Medicare services.

Medicare cards are commonly used for:
- healthcare verification
- identity validation
- government service onboarding

Non-essential appearance-related fields can be removed to reduce OCR complexity.

---

## Important Extraction Fields

- card number
- holder name
- expiry date
- individual reference position

---

## Medicare Card Schema

```json
{
  "title": "Medicare Card",
  "description": "Structured extraction schema for Australian Medicare cards",
  "type": "object",
  "properties": {
    "medicare_card_number": {
      "type": "string",
      "title": "Card Number",
      "description": "Unique Medicare card number",
      "required": true
    },

    "medicare_card_first_name": {
      "type": "string",
      "title": "First Name",
      "description": "Card holder first name",
      "required": true
    },

    "medicare_card_last_name": {
      "type": "string",
      "title": "Last Name",
      "description": "Card holder last name",
      "required": true
    },

    "medicare_card_expiry_date": {
      "type": "string",
      "title": "Expiry Date",
      "description": "Medicare card expiration date",
      "required": true
    },

    "medicare_card_position": {
      "type": "string",
      "title": "Reference Position",
      "description": "Individual reference number position on the card",
      "required": true
    },

    "document_front": {
      "type": "array",
      "title": "Medicare Front Image",
      "description": "Front side image of the Medicare card",
      "items": {
        "type": "string"
      },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Medicare Back Image",
      "description": "Back side image of the Medicare card",
      "items": {
        "type": "string"
      },
      "required": false
    }
  }
}
```

---

# 3.4 Working With Children (WWC)

## Description

A Working With Children (WWC) card is a government-issued background-check clearance document.

It is commonly required for:
- education roles
- childcare positions
- volunteer programs
- regulated employment

---

## Important Extraction Fields

- holder name
- WWC card number
- expiry date
- issuing state

---

## WWC Schema

```json
{
  "title": "Working With Children (WWC) Card",
  "description": "Structured extraction schema for Working With Children clearance cards",
  "type": "object",
  "properties": {
    "wwc_first_name": {
      "type": "string",
      "title": "First Name",
      "description": "WWC card holder first name",
      "required": true
    },

    "wwc_last_name": {
      "type": "string",
      "title": "Last Name",
      "description": "WWC card holder last name",
      "required": true
    },

    "wwc_card_number": {
      "type": "string",
      "title": "WWC Card Number",
      "description": "Unique Working With Children card number",
      "required": true
    },

    "wwc_expiry_date": {
      "type": "string",
      "title": "Expiry Date",
      "description": "WWC card expiration date",
      "required": true
    },

    "wwc_state": {
      "type": "string",
      "title": "Issuing State",
      "description": "Australian state issuing the WWC card",
      "required": true
    },

    "document_front": {
      "type": "array",
      "title": "WWC Front Image",
      "description": "Front side image of the WWC card",
      "items": {
        "type": "string"
      },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "WWC Back Image",
      "description": "Back side image of the WWC card",
      "items": {
        "type": "string"
      },
      "required": false
    }
  }
}
```

---

# 3.5 IELTS Certificate

## Description

An IELTS Test Report Form (TRF) is an official English proficiency certificate.

It is commonly used for:
- university applications
- migration
- employment verification
- visa applications

Detailed subsection scores may optionally be extracted in later versions.

---

## Important Extraction Fields

- candidate name
- TRF number
- test date
- test type
- overall band score

---

## IELTS Schema

```json
{
  "title": "IELTS Test Report Form",
  "description": "Structured extraction schema for IELTS certificates",
  "type": "object",
  "properties": {
    "ielts_first_name": {
      "type": "string",
      "title": "First Name",
      "description": "Candidate first name",
      "required": true
    },

    "ielts_last_name": {
      "type": "string",
      "title": "Last Name",
      "description": "Candidate last name",
      "required": true
    },

    "ielts_test_date": {
      "type": "string",
      "title": "Test Date",
      "description": "IELTS examination date",
      "required": true
    },

    "ielts_trf_number": {
      "type": "string",
      "title": "TRF Number",
      "description": "Unique IELTS Test Report Form number",
      "required": true
    },

    "ielts_test_type": {
      "type": "string",
      "title": "Test Type",
      "description": "IELTS Academic or General Training",
      "required": true
    },

    "ielts_overall_band": {
      "type": "number",
      "title": "Overall Band Score",
      "description": "Overall IELTS band score",
      "required": true
    },

    "document_front": {
      "type": "array",
      "title": "IELTS Front Image",
      "description": "Front side image of the IELTS certificate",
      "items": {
        "type": "string"
      },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "IELTS Back Image",
      "description": "Back side image of the IELTS certificate",
      "items": {
        "type": "string"
      },
      "required": false
    }
  }
}
```

---

# 3.6 Energy Bill

## Description

An energy bill is a utility document issued by an electricity or gas retailer.

Energy bills are commonly used for:
- proof of address
- customer verification
- utility account validation

Complex billing breakdowns may be omitted during MVP extraction.

---

## Important Extraction Fields

- account holder
- account number
- retailer name
- service address
- due date
- total amount due

---

## Energy Bill Schema

```json
{
  "title": "Australian Household Energy Bill",
  "description": "Structured extraction schema for Australian electricity and gas bills",
  "type": "object",
  "properties": {
    "energy_bill_account_holder_name": {
      "type": "string",
      "title": "Account Holder Name",
      "description": "Name of the account holder",
      "required": true
    },

    "energy_bill_account_number": {
      "type": "string",
      "title": "Account Number",
      "description": "Utility account number",
      "required": true
    },

    "energy_bill_retailer_name": {
      "type": "string",
      "title": "Retailer Name",
      "description": "Energy retailer or provider name",
      "required": true
    },

    "energy_bill_service_address": {
      "type": "string",
      "title": "Service Address",
      "description": "Property service address",
      "required": true
    },

    "energy_bill_due_date": {
      "type": "string",
      "title": "Due Date",
      "description": "Bill payment due date",
      "required": true
    },

    "energy_bill_total_amount_due": {
      "type": "number",
      "title": "Total Amount Due",
      "description": "Total payable amount on the bill",
      "required": true
    },

    "document_front": {
      "type": "array",
      "title": "Energy Bill Front Image",
      "description": "Front page image of the energy bill",
      "items": {
        "type": "string"
      },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Energy Bill Additional Pages",
      "description": "Additional bill pages or back-side images",
      "items": {
        "type": "string"
      },
      "required": false
    }
  }
}
```

---

# 3.7 Unknown Document

## Description

Fallback schema used when:
- document classification fails
- OCR confidence is too low
- unsupported document types are uploaded
- corrupted or unreadable files are detected

This schema helps preserve raw OCR outputs for debugging and future model improvement.

---

## Important Extraction Fields

- raw extracted text
- failure reason
- classifier top prediction
- classifier confidence

---

## Unknown Document Schema

```json
{
  "title": "Unknown Document",
  "description": "Fallback schema for unsupported or failed document classification",
  "type": "object",
  "properties": {
    "unknown_raw_text": {
      "type": ["string", "null"],
      "title": "Raw OCR Text",
      "description": "Raw text extracted from the document",
      "required": true
    },

    "unknown_reason": {
      "type": "string",
      "title": "Unknown Reason",
      "description": "Reason why the document could not be classified or processed",
      "required": true
    },

    "unknown_classifier_top_guess": {
      "type": ["string", "null"],
      "title": "Classifier Top Guess",
      "description": "Best predicted document type returned by classifier",
      "required": false
    },

    "unknown_classifier_confidence": {
      "type": ["number", "null"],
      "title": "Classifier Confidence",
      "description": "Confidence score of the classifier prediction",
      "required": false
    },

    "document_front": {
      "type": "array",
      "title": "Unknown Document Front Image",
      "description": "Front side image of the uploaded document",
      "items": {
        "type": "string"
      },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Unknown Document Back Image",
      "description": "Back side image of the uploaded document",
      "items": {
        "type": "string"
      },
      "required": false
    }
  }
}
```

