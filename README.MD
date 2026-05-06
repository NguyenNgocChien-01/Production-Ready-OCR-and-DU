# Production-Ready OCR & Document Understanding Mastery Challenge
# Sumary
## STEP 1
- ORC: Image/PDF to text (TesseratORC, PaddleORC…)
- Document Understanding: Image/PDF to Structured Data
- Support document types: Invoice, Passport, ID Card…
- Setup GCP project and create HuggingFace account.
- OCR supported document types: invoice, id_card, driver_license, passport, certificate.

# STEP 2
- JSON schema design for each document type

# STEP 3
- Faker + ReportLab to dummy data.
- Generate balenced dummy datasets for invoice, id_card, driver_license, passport, certificate.
  ![System Architecture](sample_invoice.pdf)
- Upload dataset to HF
  [dummy-dataset-documents-ocr](https://huggingface.co/datasets/Chino-01/dummy-dataset-documents-ocr)
