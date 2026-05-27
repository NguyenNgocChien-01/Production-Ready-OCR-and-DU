## Classify - Choose Models - Finetune

- [Step 4: Classify](#step-4-classify)
- [Step 5: Choose model](#step-5-choose-model)
- [STEP 6: Fine-tune](#step-6)

# Step 4: Classify
- For Step 4, I do not use standalone base models. Instead, I will use a fine-tuned Large Language Model for document classification. This LLM processes OCR text and spatial data simultaneously to output accurate labels.
# Step 5: Choose model
update later.

# Step 6:
# Fine-Tuning Report: Document Information Extraction
- My notebook to fine-tune: [NotebookColab](https://colab.research.google.com/drive/1TNgAs_IInByV5f4pLvdbI3YwLIsJbSRe#scrollTo=tP3LSL97N2wx)
  
Model: Qwen2-VL-2B-Instruct
Framework: swift
Platform: Google Colab

# 01 - Dataset Preparation
- I have used the data at [synthetic-doc-generator-data](https://github.com/NguyenNgocChien-01/synthetic-doc-generator/tree/main/dataset).

- Folder strcuture:

```
data/
├── documents/
|──────aus_passport/
|──────aus_medicare_card/green/, ...
|
└── labels/  (mirrors documents)
```

- Now, I have ~10 image + json sample per passport, vic driver license, vic wwc, 3 type medicare card = ~ 70 sample.
-  Schema json each type: [Step 2](ocr-project/OCR-Step2-Design-Schema.MD)
  
# 02 -  Create Custom Dataset Swift Format [02_create_custom_dataset_swift_local.ipynb](https://drive.google.com/file/d/1BmtN3q8E-xjYm96ZBzOxnfXOVGZuIh8m/view?usp=drive_link)

## Goal: convert raw images and JSON labels into SWIFT training format.
**1. Load data from local:** load_local_data(doc_dir, label_dir, skip_stems)
Scans labels/ recursively for .json files. For each label finds the matching image (.jpg/.png/.pdf). Returns a list of records containing filename, doc_type, target_data, and doc_bytes.

**2. Split data:** 

- **If** *n_sample* < 3 ==> no split.
- **Else** ==> Stratified by doc type, 80% train / 10% dev / 10% test, random seed 42. Types with fewer than 3 samples go entirely to train.
- 
```text
Distribution by document type:
doc_type
aus_driver_license/act       1
aus_driver_license/nsw       1
aus_driver_license/nt        1
aus_driver_license/qld       1
aus_driver_license/sa        1
aus_driver_license/tas       1
aus_driver_license/vic      11
aus_driver_license/wa        1
aus_medicare_card/blue      13
aus_medicare_card/green     11
aus_medicare_card/yellow    11
aus_passport                11
aus_wwc_card/vic            10

Total: 74 samples, 13 types

 Document Type                              Total  Train    Dev   Test
----------------------------------------------------------------------
aus_driver_license/act                          1      1      0      0  (insufficient samples)
aus_driver_license/nsw                          1      1      0      0  (insufficient samples)
aus_driver_license/nt                           1      1      0      0  (insufficient samples)
aus_driver_license/qld                          1      1      0      0  (insufficient samples)
aus_driver_license/sa                           1      1      0      0  (insufficient samples)
aus_driver_license/tas                          1      1      0      0  (insufficient samples)
aus_driver_license/vic                         11      9      1      1
aus_driver_license/wa                           1      1      0      0  (insufficient samples)
aus_medicare_card/blue                         13     11      1      1
aus_medicare_card/green                        11      9      1      1
aus_medicare_card/yellow                       11      9      1      1
aus_passport                                   11      9      1      1
aus_wwc_card/vic                               10      8      1      1
----------------------------------------------------------------------
 TOTAL                                         74     62      6      6
```

**3. Extract images & create swift format:**
- **If** *is PDF n page* ==> to n PNG
- **Else** (is 1 image) ==> to PNG
- Save at:
```
swift_dataset/images/
├── bill_00001_page000.png 
|── bill_00001_page001.png 
└── passport_00001.png
```

- Normalizes field names using label_to_schema_mapping.json. Supports dot-notation for nested fields like person.name
- Builds one training sample in SWIFT conversational format:

```
return {
    'messages': [
        {'role': 'system', 'content': 'You are a document processing expert skilled in extracting information from official documents.'},
        {'role': 'user', 'content': f'Document: {"<image>" * num_images}\nProcess all document pages and extract the following information in JSON format: {", ".join(field_names)}'},
        {'role': 'assistant', 'content': json.dumps(formatted_data, ensure_ascii=False)}
    ],
    'images': image_paths
}

```

Such as:

```
    "messages": [
      {
        "role": "system",
        "content": "You are a document processing expert skilled in extracting information from official documents."
      },
      {
        "role": "user",
        "content": "Document: <image>\nProcess all document pages and extract the following information in JSON format: document_type, australian_passport_number, australian_passport_last_name, australian_passport_first_name, australian_passport_nationality, australian_passport_date_of_birth, australian_passport_gender, australian_passport_date_of_issue, australian_passport_expiry_date, australian_passport_place_of_birth, australian_passport_authority, australian_passport_mrz_line1, australian_passport_mrz_line2"
      },
      {
        "role": "assistant",
        "content": "{\"document_type\": \"AUS_PASSPORT\", \"australian_passport_number\": \"SP2450814\", \"australian_passport_last_name\": \"GRANT\", \"australian_passport_first_name\": \"KEITH\", \"australian_passport_nationality\": \"AUSTRALIAN\", \"australian_passport_date_of_birth\": \"1992-01-09\", \"australian_passport_gender\": \"M\", \"australian_passport_date_of_issue\": \"2012-03-03\", \"australian_passport_expiry_date\": \"2022-03-03\", \"australian_passport_place_of_birth\": \"NE JANDON\", \"australian_passport_authority\": \"CANBERRA\", \"australian_passport_mrz_line1\": \"P<AUSGRANT<<KEITH<<<<<<<<<<<<<<<<<<<<<<<<<<<\", \"australian_passport_mrz_line2\": \"SP2450814<AUS920109M291023<<<<<<<<<<<<<<<<09\"}"
      }
    ],
    "images": [
      "/content/drive/MyDrive/INTERN-BIWOCO/sample-for-multi-modal-document-to-json-with-sagemaker-ai/data/swift_dataset/images/aus_passport_00012.png"
    ]
  },
  
```

# 03 - Fine-tune
- Method: LoRA applied to all linear layers. ViT and aligner are frozen. Only the LLM weights are trained.
- I have changed some parameters so that it can run on Colab (GPU T4 - 15GB):
  - model: Qwen2.5-VL-3N --> Qwen2-VL-2B
  - max_length: 4096 --> 1500 (This model just use < 1500 token, reduce to save VRAM)
  - add max_pixels: resize image to 262144 (512x512)
  - per_device_train_batch_size: 4 --> 1. Trade-off beetwen Vram and time...

```python
  
  argv = [
    "--model_type", "qwen2_vl",
    "--model", "Qwen/Qwen2-VL-2B-Instruct",
    "--tuner_type", "lora",
    "--use_dora", "", # true
    "--output_dir", output_dir,
    "--max_length", "1500",
    "--max_pixels", "262144",  
    "--dataset", train_dataset,
    "--val_dataset", val_dataset,
    "--save_steps", "10",
    "--logging_steps","5",
    "--num_train_epochs", "5",
    "--lora_dtype", "bfloat16",
    "--per_device_train_batch_size", "1", 
    "--per_device_eval_batch_size", "1",
    "--learning_rate", "1e-4",
    "--target_modules", "all-linear",
    "--use_hf", "true",
    "--warmup_ratio","0.05",
    "--save_total_limit","3",
    "--gradient_accumulation_steps","8", 
    "--freeze_vit", "true", 
    "--freeze_llm", "false", 
    "--freeze_aligner", "true",
    "--gradient_checkpointing", "true"
]

```


- *--model = qwen2_vl*  load from Qwen/Qwen2-VL-2B-Instruct.
- *--tuner_type = "lora"*: LoRA adds low-rank matrices to the model, training only them instead of all the weights.
- *--use_dora*: 
- *--max_length*: Maximum number of tokens (prompt + output)
- *--max_pixels*: Maximun size of image.
- *--save_steps*: save checkpoint after 50 steps
- *--logging_steps*: print log after 5 steps
- *--num_train_epochs*: number of epochs
- *--lora_dtype*: data type for LoRA, float16 saves VRAM compared to float32.
- *--per_device_train_batch_size*: sample/batch
- *--per_device_eval_batch_size*: sample/batch
- *--learning_rate*
- *--target_modules*: Apply LoRA to all linear layers of the LLM.
- *--use_hf*
- *--warmup_ratio*: percent begin steps used to up lr from 0 --> lr used
- *--save_total_limit*: keep a max of n checkpoints, delete the oldest one.
- *--gradient_accumulation_steps*: update weight after each batch
- *--freeze_vit*: Learn encode image --> vector, model Qwen good this part. No use.
- *--freeze_llm*: Goal.
- *--freeze_aligner*: vector --> LLM Space.
- *--gradient_checkpointing*: true -> down Vram, up time backward. Default = flase 

```
Train:   0%|          | 0/40 [00:00<?, ?it/s][INFO:swift] use_logits_to_keep: True

Train:   2%|▎         | 1/40 [01:08<44:41, 68.75s/it]{'loss': '0.3605', 'grad_norm': '1.021', 'learning_rate': '5e-05', 'token_acc': '0.9222', 'epoch': '0.129', 'global_step/max_steps': '1/40', 'elapsed_time': '1m 9s', 'remaining_time': '44m 41s', 'memory(GiB)': '11.15', 'train_speed(s/it)': '68.75'}

Train:  12%|█▎        | 5/40 [06:05<43:34, 74.69s/it]{'loss': '0.3135', 'grad_norm': '0.5845', 'learning_rate': '9.847e-05', 'token_acc': '0.9275', 'epoch': '0.6452', 'global_step/max_steps': '5/40', 'elapsed_time': '6m 5s', 'remaining_time': '42m 38s', 'memory(GiB)': '11.17', 'train_speed(s/it)': '73.07'}

...

Train: 100%|██████████| 40/40 [46:24<00:00, 66.13s/it]{'loss': '0.03774', 'grad_norm': '0.2161', 'learning_rate': '0', 'token_acc': '0.9921', 'epoch': '5', 'global_step/max_steps': '40/40', 'elapsed_time': '46m 24s', 'remaining_time': '0s', 'memory(GiB)': '11.5', 'train_speed(s/it)': '69.6'}

Val: 100%|██████████| 6/6 [00:13<00:00,  2.18s/it]
{'eval_loss': '0.0723', 'eval_runtime': '17.57', 'eval_samples_per_second': '0.341', 'eval_steps_per_second': '0.341', 'eval_token_acc': '0.9747', 'epoch': '5', 'global_step/max_steps': '40/40', 'elapsed_time': '46m 42s', 'remaining_time': '0s', 'memory(GiB)': '11.5', 'train_speed(s/it)': '70.05'}

```


# 04 - Inference

```python
infer_argv = [
    "--model_type", "qwen2_vl",
    "--model", "Qwen/Qwen2-VL-2B-Instruct",
    "--adapters", "/content/drive/MyDrive/INTERN-BIWOCO/sample-for-multi-modal-document-to-json-with-sagemaker-ai/models/finetune/v25-20260523-153314/checkpoint-40",
    "--max_pixels", "262144",
    "--max_new_tokens", "512",
    "--stream", "false", 
]

infer_main(infer_argv)


<<< <<image>>. extract follow json output:...
{
  "document_type": "",
  "issuing_country": "",
  "document_number": "",
  "family_name": "",
  "given_names": "",
  "nationality": "",
  "date_of_birth": "",
  "sex": "F",
  "date_of_issue": "",
  "date_of_expiry": "",
  "place_of_birth": "",
  "authority": "",
  "mrz_line1": "",
  "mrz_line2": ""
}

Input an image path or URL <<< /content/template.jpg

{
    "document_type": "AUS_PASSPORT", 
    "issuing_country": "AUSTRALIA", 
    "document_number": "J8962842", 
    "family_name": "NICHOLAS",
    "given_names": "MICHAEL", 
    "nationality": "AUSTRALIAN",
    "date_of_birth": "1996-03-05", 
    "sex": "F", 
    "date_of_issue": "2025-01-23", 
    "date_of_expiry": "2035-01-23", 
    "place_of_birth": "LONDON", 
    "authority": "AUSTRALIAN", 
    "mrz_line1": "P<AUSFIGUEROA<MICHAEL<NICHOLAS<<<<<<<<<<<<<<<<<<<<<<<<<<<         J8962842<6AUS9603057M3501232<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<00",
    "mrz_line2": ""}
```
--> Have wrong.

# 05 - Evalution
![Evalution](img/evalution-model.png)

