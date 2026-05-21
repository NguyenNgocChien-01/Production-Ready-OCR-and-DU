# Production-Ready OCR & Document Understanding Mastery Challenge

## Abtracts

### Step 1: Environment Setup & OCR Fundamentals
- OCR: Image/PDF to text (Tesseract OCR, PaddleOCR…)
- Document Understanding: Image/PDF to structured data (JSON)
- Supported document types: invoice, ID card, driver license, passport, certificate
- Set up GCP project and create Hugging Face account

---

### Step 2: Schema Design [Step 2](NguyenNgocChien-Step2-Intern-OCR.MD)
- Design JSON schema for each document type 

---

### Step 3: Synthetic Data Generation
- Use Faker + ReportLab to generate dummy data
- Generate balanced datasets for:
  - driver_license
  - passport
  - ielts certificate
  - medicare card
  - Working with children
  - engery bill

## Use Augraphy
![Augraphy](augmentation.png)
<!-- #### Sample Output

![Sample Invoice](sample_invoice_1.jpg)

---

### Dataset
- Hugging Face Dataset:
[dummy-dataset-documents-ocr](https://huggingface.co/datasets/Chino-01/dummy-dataset-documents-ocr) -->

## Generate data
Having some generated sample data (passport + medicare card) at: [synthetic-doc-generator-data](https://github.com/NguyenNgocChien-01/synthetic-doc-generator/tree/main/dataset)