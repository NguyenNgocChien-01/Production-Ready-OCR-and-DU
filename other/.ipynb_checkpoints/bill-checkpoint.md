# Sample

[PDF](ocr-project/other/aus_energy_bill_00001.pdf)

# Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Australian Energy Bill",
  "type": "object",
  "properties": {

    "document_type": {
      "type": "string",
      "title": "Document Type",
      "description": "Always AUS_ELECTRICITY_BILL.",
      "enum": ["AUS_ELECTRICITY_BILL"],
      "required": true
    },

    "provider_name": {
      "type": "string",
      "title": "Provider Name",
      "description": "Trading name of the energy retailer as shown on the bill (e.g. 'AGL', 'EnergyAustralia').",
      "required": true
    },

    "provider_abn": {
      "type": ["string", "null"],
      "title": "Provider ABN",
      "description": "Australian Business Number of the energy retailer (e.g. '11 222 333 444').",
      "required": false
    },

    "account_holder_name": {
      "type": "string",
      "title": "Account Holder Name",
      "description": "Full name of the account holder as shown on the bill (e.g. 'Jane Citizen').",
      "required": true
    },

    "account_number": {
      "type": ["string", "null"],
      "title": "Account Number",
      "description": "Customer account number as shown on the bill (e.g. '123456').",
      "required": false
    },

    "nmi": {
      "type": ["string", "null"],
      "title": "National Metering Identifier (NMI)",
      "description": "10-digit electricity meter identifier (e.g. '0123456789'). Electricity only.",
      "required": false
    },


    "service_address_street": {
      "type": "string",
      "title": "Service Address - Street",
      "description": "Street number and name of the supply address (e.g. '1 Street Road').",
      "required": true
    },

    "service_address_suburb": {
      "type": "string",
      "title": "Service Address - Suburb",
      "description": "Suburb or locality of the supply address (e.g. 'ANYTOWN').",
      "required": true
    },

    "service_address_state": {
      "type": "string",
      "title": "Service Address - State",
      "description": "Australian state or territory abbreviation (e.g. 'VIC').",
      "enum": ["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"],
      "required": true
    },

    "service_address_postcode": {
      "type": "string",
      "title": "Service Address - Postcode",
      "description": "4-digit Australian postcode (e.g. '0000').",
      "required": true
    },

    "bill_issue_date": {
      "type": ["string", "null"],
      "title": "Bill Issue Date",
      "description": "Date the bill was issued (YYYY-MM-DD) (e.g. '2022-04-01').",
      "format": "date",
      "required": false
    },

    "bill_due_date": {
      "type": ["string", "null"],
      "title": "Bill Due Date",
      "description": "Payment due date (YYYY-MM-DD) (e.g. '2022-04-27').",
      "format": "date",
      "required": false
    },

    "billing_period_start": {
      "type": "string",
      "title": "Billing Period Start",
      "description": "Start date of the billing period (YYYY-MM-DD) (e.g. '2022-03-01').",
      "format": "date",
      "required": true
    },

    "billing_period_end": {
      "type": "string",
      "title": "Billing Period End",
      "description": "End date of the billing period (YYYY-MM-DD) (e.g. '2022-03-31').",
      "format": "date",
      "required": true
    },

    "electricity_kwh": {
      "type": ["number", "null"],
      "title": "Electricity Usage (kWh)",
      "description": "Total electricity consumed in the billing period in kWh (e.g. 567.0). Electricity only.",
      "required": false
    },

    "average_daily_usage_kwh": {
    "type": ["number", "null"],
    "title": "Average Daily Usage",
    "description": "Average daily energy usage as printed on the bill (e.g. 31.66 kWh/day). Directly readable by OCR.",
    "required": false
    },

    "previous_balance": {
      "type": "number",
      "title": "Previous Balance",
      "description": "Opening balance carried forward from previous bill in AUD (e.g. 114.87).",
      "required": true
    },

    "payments_received": {
      "type": "number",
      "title": "Payments Received",
      "description": "Total payments received since last bill in AUD (e.g. 35.00).",
      "required": true
    },

    "supply_charge": {
      "type": ["number", "null"],
      "title": "Supply Charge",
      "description": "Fixed daily supply or connection charge for the billing period in AUD (e.g. 31.62).",
      "required": false
    },

    "usage_charges": {
      "type": "number",
      "title": "Usage Charges",
      "description": "Total energy usage charges before discounts and credits in AUD (e.g. 156.11).",
      "required": true
    },

    "solar_feed_in_credit": {
      "type": ["number", "null"],
      "title": "Solar Feed-in Credit",
      "description": "Credit from solar energy exported to the grid in AUD (e.g. 41.67). Null if no solar.",
      "required": false
    },

    "concession": {
      "type": ["number", "null"],
      "title": "Government Concession / Rebate",
      "description": "Government energy rebate or concession applied to the bill in AUD (e.g. 24.20). Null if none.",
      "required": false
    },

    "total_discount": {
      "type": ["number", "null"],
      "title": "Total Discounts",
      "description": "Total retailer discounts applied (usage discount, pay-on-time, etc.) in AUD (e.g. 25.76). Null if none.",
      "required": false
    },

    "gst": {
      "type": "number",
      "title": "GST",
      "description": "GST component of the total bill amount in AUD (e.g. 18.77).",
      "required": true
    },

    "amount_due": {
      "type": "number",
      "title": "Amount Due",
      "description": "Total amount payable including GST in AUD (e.g. 79.87).",
      "required": true
    },

    "document_pages": {
      "type": "array",
      "title": "Document Pages",
      "description": "Ordered list of image file paths for each page of the bill.",
      "required": true,
      "items": {
        "type": "string",
        "title": "Page Image Path",
        "description": "Relative file path to a bill page image (e.g. 'aus_energy_bill_00001_page1.png')."
      }
    }

  }
}
```


# Label

```json
{
  "document_type": "AUS_ELECTRICITY_BILL",

  "provider_name": "AGL",
  "provider_abn": "88 090 538 337",

  "account_holder_name": "Thi Khoi Anh Phan",
  "account_number": "7095 004 987",
  "nmi": "41029727986"

  "service_address_street": "2A Eyre Street",
  "service_address_suburb": "CHIFLEY",
  "service_address_state": "NSW",
  "service_address_postcode": "2036",

  "bill_issue_date": "2024-09-25",
  "bill_due_date": "2024-10-15",

  "billing_period_start": "2024-06-27",
  "billing_period_end": "2024-09-23",

  "electricity_kwh": null,
  "average_daily_usage_kwh": 31.66,


  "previous_balance": 853.83,
  "payments_received": 853.83,
  "supply_charge": 75.37,
  "usage_charges": 844.36,
  "solar_feed_in_credit": null,
  "concession": null,
  "total_discount": null,
  "gst": 84.44,
  "amount_due": 928.80,

  "document_pages": [
    "aus_energy_bill_00001_page1.png",
    "aus_energy_bill_00001_page2.png",
    "aus_energy_bill_00001_page3.png",
    "aus_energy_bill_00001_page4.png"
  ]
}

```


