# Production-Ready OCR & Document Understanding Mastery Challenge [PDF](Production-Ready_OCR__Document_Understanding_Mastery_Challenge.pdf)

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

The architecture requires ingesting a base image combined with a text prompt to render a new image with replaced data while maintaining the original layout.
The standardized payload consumes approximately 4000 input tokens and 1300 output tokens.  

### Google Gemini 2.5 Flash Image
- Priced at $0.30 per 1M input (text + image) tokens and $30.00 per 1M output tokens
- Official pricing reference: [Agent Platform Pricing | Google Cloud](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing#standard_1)
- Calculates to  ~$0.04 per image
  
### OpenAI GPT-Image-2
- Priced at $8.00 per 1M image input tokens, $5.00 per 1M text input tokens, and $30.00 per 1M output tokens  
- Official pricing reference: [OpenAI API Pricing | OpenAI](https://openai.com/api/pricing/)
  
### Claude
- Technical: Non-compliant (Analyzes input images only but cannot generate output images)
- Reference: [Vision - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/vision)

### OpenAI DALL-E
- Technical: Operates strictly on a Text-to-Image mechanism without accepting base image inputs
- Reference: [DALL·E 3 | OpenAI](https://openai.com/index/dall-e-3/)




Gemini ensures full technical compliance while reducing API costs compared to OpenAI --> Chose **Gemini-2.5-flash-image**


Having some generated sample data at: [synthetic-doc-generator-data](https://github.com/NguyenNgocChien-01/synthetic-doc-generator/tree/main/dataset) (~10 sample).
- passport
- medicare card(3 type)
- driver license (state vic)
- working with children check (state vic)


### Step 4-5-6: Classify - Choose model - Finetune

- I don't used classtify model base. I'll combine both the classification and extraction steps into a single LLM model because this approach can reduce pipeline complexity.

- The fine-tune process will be based on: [Fine-tune VLMs](https://aws.amazon.com/blogs/machine-learning/fine-tune-vlms-for-multipage-document-to-json-with-sagemaker-ai-and-swift/#:~:text=Developing%20an%20evaluation%20framework%20to,and%20deploy%20models%20at%20scale)

- My notebook to fine-tune: [Notebook Colab](https://colab.research.google.com/drive/1TNgAs_IInByV5f4pLvdbI3YwLIsJbSRe#scrollTo=tP3LSL97N2wx)

- My report: [Step4-5-6](OCR-Step4-5-6.md)