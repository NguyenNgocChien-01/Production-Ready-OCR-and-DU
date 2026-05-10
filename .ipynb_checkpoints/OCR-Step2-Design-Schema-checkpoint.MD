# Production-Ready OCR & Document Understanding Mastery Challenge

# Step 2: Define Supported Documents & Extraction Schemas

---

# Overview

Research/Learn: JSON schema design for each document type, handling
variations (different states/countries, formats).
Actions: Create formal JSON schemas for all supported documents.
Milestone: Complete schema library + “unknown” fallback logic documented.

---

# Table of Contents

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
    "description": "Image the front side of the document",
    "items": {
      "type": "string",
      "description": "Image path, URL, or base64 string"
    },
    "required": true
  },

  "document_back": {
    "type": "array",
    "title": "Document Back Photo",
    "description": "Image the back side of the document",
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


![Passport](img/passport.jpg)

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

![Driver](img/driver-licence.jpg)

## Driver Licence Schema

```json
{
  "title": "Driver Licence",
  "description": "Structured extraction schema for driver licences",
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

Healthcare identification card used for accessing Medicare services.

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

![Medicare](img/medicare.jpg)


## Medicare Card Schema

```json
{
  "title": "Medicare Card",
  "description": "Structured extraction schema for Medicare cards",
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

![WWC](img/wwc.jpg)


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
      "description": "State issuing the WWC card",
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
- centre Number
- candidate Number
- candidate ID
- name
- date of Birth
- nationality
- first Language
- individual skill scores
- CEFR level
- validation stamp
- cheme code
- report form number

---

![ielts](img/ielts.png)
## IELTS Schema

```json
{
  "title": "IELTS Test Report Form",
  "description": "Production-ready extraction schema for IELTS certificates",
  "type": "object",

  "properties": {

    "ielts_candidate_first_name": {
      "type": "string",
      "title": "Candidate First Name",
      "description": "Candidate given name(s)",
      "required": true
    },

    "ielts_candidate_last_name": {
      "type": "string",
      "title": "Candidate Last Name",
      "description": "Candidate family name",
      "required": true
    },

    "ielts_candidate_id": {
      "type": ["string", "null"],
      "title": "Candidate ID",
      "description": "Candidate identification number shown on certificate",
      "required": false
    },

    "ielts_candidate_number": {
      "type": ["string", "null"],
      "title": "Candidate Number",
      "description": "Internal IELTS candidate number",
      "required": false
    },

    "ielts_centre_number": {
      "type": ["string", "null"],
      "title": "Centre Number",
      "description": "IELTS testing centre number",
      "required": false
    },

    "ielts_test_date": {
      "type": "string",
      "format": "date",
      "title": "Test Date",
      "description": "Official IELTS examination date",
      "required": true
    },

    "ielts_report_date": {
      "type": ["string", "null"],
      "format": "date",
      "title": "Report Issue Date",
      "description": "Date the report form was issued",
      "required": false
    },

    "ielts_date_of_birth": {
      "type": ["string", "null"],
      "format": "date",
      "title": "Date of Birth",
      "description": "Candidate birth date",
      "required": false
    },

    "ielts_gender": {
      "type": ["string", "null"],
      "enum": ["M", "F", "Other", null],
      "title": "Gender",
      "description": "Candidate gender",
      "required": false
    },

    "ielts_country_of_nationality": {
      "type": ["string", "null"],
      "title": "Country of Nationality",
      "description": "Candidate nationality",
      "required": false
    },

    "ielts_first_language": {
      "type": ["string", "null"],
      "title": "First Language",
      "description": "Candidate first language",
      "required": false
    },

    "ielts_test_type": {
      "type": "string",
      "enum": [
        "Academic",
        "General Training",
        "UKVI Academic",
        "UKVI General Training",
        "Life Skills",
        "Unknown"
      ],
      "title": "Test Type",
      "description": "IELTS examination type",
      "required": true
    },

    "ielts_scheme_code": {
      "type": ["string", "null"],
      "title": "Scheme Code",
      "description": "IELTS scheme or registration category",
      "required": false
    },

    "ielts_listening_score": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 9,
      "title": "Listening Score",
      "description": "IELTS listening band score",
      "required": false
    },

    "ielts_reading_score": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 9,
      "title": "Reading Score",
      "description": "IELTS reading band score",
      "required": false
    },

    "ielts_writing_score": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 9,
      "title": "Writing Score",
      "description": "IELTS writing band score",
      "required": false
    },

    "ielts_speaking_score": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 9,
      "title": "Speaking Score",
      "description": "IELTS speaking band score",
      "required": false
    },

    "ielts_overall_band_score": {
      "type": "number",
      "minimum": 0,
      "maximum": 9,
      "title": "Overall Band Score",
      "description": "Overall IELTS band score",
      "required": true
    },

    "ielts_cefr_level": {
      "type": ["string", "null"],
      "title": "CEFR Level",
      "description": "Mapped CEFR proficiency level",
      "required": false
    },

    "ielts_trf_number": {
      "type": "string",
      "title": "TRF Number",
      "description": "Unique IELTS Test Report Form number",
      "required": true
    },

    "ielts_administrator_comments": {
      "type": ["string", "null"],
      "title": "Administrator Comments",
      "description": "Optional comments section",
      "required": false
    },

    "ielts_has_validation_stamp": {
      "type": ["boolean", "null"],
      "title": "Validation Stamp Present",
      "description": "Whether validation stamp exists",
      "required": false
    },

    "ielts_candidate_photo_present": {
      "type": ["boolean", "null"],
      "title": "Candidate Photo Present",
      "description": "Whether candidate photo is detected",
      "required": false
    },

    "document_front": {
      "type": "array",
      "title": "IELTS Front Image",
      "description": "Front side image of IELTS certificate",
      "items": {
        "type": "string"
      },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "IELTS Back Image",
      "description": "Back side image of IELTS certificate",
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
- billing verification
- payment reconciliation
- onboarding and KYC workflows

Australian energy bills may contain:
- account information
- service address
- billing period
- payment details
- utility identifiers
- usage summaries
- tax information
- barcode and BPAY references

Different providers use different layouts and terminology, so OCR extraction should support flexible optional fields.

---

## Important Extraction Fields

### Core Identity Fields

- provider name
- account holder name
- account number
- service address

### Billing Fields

- issue date
- due date
- billing period
- total amount due
- account balance

### Utility Identifiers

- NMI
- MIRN
- meter number

### Payment Fields

- BPAY code
- BPAY reference
- payment reference
- payment plan indicator

### Consumption Fields

- electricity usage (kWh)
- gas usage (MJ)
- supply charge
- usage charge

---

## OCR Extraction Notes

### Required Fields

The following fields are considered high-priority and should normally be extracted:

- provider name
- account holder name
- account number
- service address
- due date
- total amount due

### Optional Fields

Many energy bill layouts vary significantly between providers.

Optional fields may be:
- missing
- renamed
- positioned differently
- unavailable on some bill types

Because of this:
- non-critical fields should remain optional
- OCR failures should not invalidate the entire extraction

---

![Bill](img/bill.png)

## Energy Bill Schema

```json
{
  "title": "Energy Bill",
  "description": "Production-ready extraction schema for electricity and gas utility bills",
  "type": "object",

  "properties": {

    "energy_bill_provider_name": {
      "type": "string",
      "title": "Energy Provider Name",
      "description": "Name of the electricity or gas retailer issuing the bill",
      "required": true
    },

    "energy_bill_provider_bn": {
      "type": ["string", "null"],
      "title": "Provider BN",
      "description": "Business Number of the energy provider",
      "required": false
    },

    "energy_bill_account_holder_name": {
      "type": "string",
      "title": "Account Holder Name",
      "description": "Full name of the primary account holder",
      "required": true
    },

    "energy_bill_account_number": {
      "type": "string",
      "title": "Account Number",
      "description": "Customer utility account number",
      "required": true
    },

    "energy_bill_invoice_number": {
      "type": ["string", "null"],
      "title": "Invoice Number",
      "description": "Unique invoice or bill reference number",
      "required": false
    },

    "energy_bill_nmi": {
      "type": ["string", "null"],
      "title": "National Metering Identifier (NMI)",
      "description": "Unique electricity meter identifier used",
      "required": false
    },

    "energy_bill_mirn": {
      "type": ["string", "null"],
      "title": "Meter Installation Registration Number (MIRN)",
      "description": "Unique gas meter identifier used",
      "required": false
    },

    "energy_bill_meter_number": {
      "type": ["string", "null"],
      "title": "Meter Number",
      "description": "Physical utility meter serial number",
      "required": false
    },

    "energy_bill_service_address": {
      "type": "string",
      "title": "Service Address",
      "description": "Address where electricity or gas service is supplied",
      "required": true
    },

    "energy_bill_postal_address": {
      "type": ["string", "null"],
      "title": "Postal Address",
      "description": "Mailing address used for bill delivery",
      "required": false
    },

    "energy_bill_issue_date": {
      "type": ["string", "null"],
      "format": "date",
      "title": "Bill Issue Date",
      "description": "Date the utility bill was issued",
      "required": false
    },

    "energy_bill_due_date": {
      "type": "string",
      "format": "date",
      "title": "Payment Due Date",
      "description": "Final payment due date for the bill",
      "required": true
    },

    "energy_bill_billing_period_start": {
      "type": ["string", "null"],
      "format": "date",
      "title": "Billing Period Start Date",
      "description": "Start date of the billing cycle",
      "required": false
    },

    "energy_bill_billing_period_end": {
      "type": ["string", "null"],
      "format": "date",
      "title": "Billing Period End Date",
      "description": "End date of the billing cycle",
      "required": false
    },

    "energy_bill_total_amount_due": {
      "type": "number",
      "title": "Total Amount Due",
      "description": "Total payable amount shown on the bill",
      "required": true
    },

    "energy_bill_account_balance": {
      "type": ["number", "null"],
      "title": "Account Balance",
      "description": "Current account balance displayed on the bill",
      "required": false
    },

    "energy_bill_supply_charge": {
      "type": ["number", "null"],
      "title": "Supply Charge",
      "description": "Fixed daily supply charge amount",
      "required": false
    },

    "energy_bill_usage_charge": {
      "type": ["number", "null"],
      "title": "Usage Charge",
      "description": "Variable charge based on energy consumption",
      "required": false
    },

    "energy_bill_usage_kwh": {
      "type": ["number", "null"],
      "title": "Electricity Usage (kWh)",
      "description": "Electricity usage measured in kilowatt-hours",
      "required": false
    },

    "energy_bill_usage_mj": {
      "type": ["number", "null"],
      "title": "Gas Usage (MJ)",
      "description": "Gas usage measured in megajoules",
      "required": false
    },

    "energy_bill_tariff_type": {
      "type": ["string", "null"],
      "title": "Tariff Type",
      "description": "Energy tariff or pricing plan type",
      "required": false
    },

    "energy_bill_gst_amount": {
      "type": ["number", "null"],
      "title": "GST Amount",
      "description": "Goods and Services Tax (GST) amount included in the bill",
      "required": false
    },

    "energy_bill_bpay_code": {
      "type": ["string", "null"],
      "title": "BPAY Biller Code",
      "description": "BPAY biller code used for payments",
      "required": false
    },

    "energy_bill_bpay_reference": {
      "type": ["string", "null"],
      "title": "BPAY Reference Number",
      "description": "Customer BPAY payment reference number",
      "required": false
    },

    "energy_bill_payment_reference": {
      "type": ["string", "null"],
      "title": "Payment Reference",
      "description": "Reference number used for payment processing",
      "required": false
    },

    "energy_bill_payment_plan": {
      "type": ["boolean", "null"],
      "title": "Payment Plan Indicator",
      "description": "Whether the customer is enrolled in a payment plan",
      "required": false
    },

    "energy_bill_concession_applied": {
      "type": ["boolean", "null"],
      "title": "Concession Applied",
      "description": "Whether a government concession or discount has been applied",
      "required": false
    },

    "energy_bill_document_type": {
      "type": ["string", "null"],
      "enum": [
        "electricity",
        "gas",
        "combined",
        null
      ],
      "title": "Energy Bill Type",
      "description": "Type of utility bill document",
      "required": false
    },

    "energy_bill_barcode_present": {
      "type": ["boolean", "null"],
      "title": "Barcode Present",
      "description": "Whether a payment barcode is detected on the bill",
      "required": false
    },

    "document_front": {
      "type": "array",
      "title": "Energy Bill Front Images",
      "description": "Front page images of the utility bill",
      "items": {
        "type": "string",
        "description": "Image path, URL, or base64 encoded image"
      },
      "required": true
    },

    "document_back": {
      "type": "array",
      "title": "Energy Bill Additional Images",
      "description": "Additional pages or back-side images of the utility bill",
      "items": {
        "type": "string",
        "description": "Image path, URL, or base64 encoded image"
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

