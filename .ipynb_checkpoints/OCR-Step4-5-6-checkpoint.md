# Classify - Finetune

- [Classify](#classify)
- [Fine-tune](#Fine-Tuning-Report-Document-Information-Extraction)
  - [01 - Dataset Preparation](#01-Dataset-Preparation)
  - [02 -  Create Custom Dataset Swift Format](#02-Create-Custom-Dataset-Swift-Format)
  - [03 - Fine-tune](#03-Fine-tune)
  - [# 04 - Inference](#04-Inference)

# Classify
- For Step 4, I do not use standalone base models. Instead, I will use a fine-tuned Large Language Model for document classification. This LLM processes OCR text and spatial data simultaneously to output accurate labels.
- 
# Fine-Tuning Report: Document Information Extraction
- My notebook to fine-tune: [NotebookColab](https://colab.research.google.com/drive/1a24_laFE-8eGvCojM0z3_UMh_O7SQx8k?authuser=3#scrollTo=tP3LSL97N2wx)
  
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

- Now, I have ~20 image + json sample per passport, vic driver license, vic wwc, 3 type medicare card = ~ 100 sample.
-  Schema json each type: [Step 2](ocr-project/OCR-Step2-Design-Schema.MD)
  
# 02 -  Create Custom Dataset Swift Format
<!-- (https://drive.google.com/file/d/1BmtN3q8E-xjYm96ZBzOxnfXOVGZuIh8m/view?usp=drive_link) -->
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
aus_driver_license/vic      16
aus_driver_license/wa        1
aus_medicare_card/blue      13
aus_medicare_card/green     11
aus_medicare_card/yellow    11
aus_passport                26
aus_wwc_card/vic            25

Total: 109 samples, 13 types
 Document Type                              Total  Train    Dev   Test
----------------------------------------------------------------------
aus_driver_license/act                          1      1      0      0  (insufficient samples)
aus_driver_license/nsw                          1      1      0      0  (insufficient samples)
aus_driver_license/nt                           1      1      0      0  (insufficient samples)
aus_driver_license/qld                          1      1      0      0  (insufficient samples)
aus_driver_license/sa                           1      1      0      0  (insufficient samples)
aus_driver_license/tas                          1      1      0      0  (insufficient samples)
aus_driver_license/vic                         16     14      1      1
aus_driver_license/wa                           1      1      0      0  (insufficient samples)
aus_medicare_card/blue                         13     11      1      1
aus_medicare_card/green                        11      9      1      1
aus_medicare_card/yellow                       11      9      1      1
aus_passport                                   26     22      2      2
aus_wwc_card/vic                               25     21      2      2
----------------------------------------------------------------------
 TOTAL                                        109     93      8      8
 
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

--> Run:
```
[INFO:swift] model_parameter_info: PeftModelForCausalLM: 2218.2180M Params (9.2324M Trainable [0.4162%]), 0.0001M Buffers.
[INFO:swift] use_reentrant: True
[INFO:swift] The logging file will be saved in: /content/drive/MyDrive/INTERN-BIWOCO/sample-for-multi-modal-document-to-json-with-sagemaker-ai/models/finetune/v6-20260528-021630/logging.jsonl
[INFO:swift] Successfully registered post_encode hook: ['PeftModelForCausalLM'].
[transformers] The tokenizer has new PAD/BOS/EOS tokens that differ from the model config and generation config. The model config and generation config were aligned accordingly, being updated with the tokenizer's values. Updated tokens: {'eos_token_id': 151645, 'bos_token_id': None, 'pad_token_id': 151643}.
Train:   0%|          | 0/60 [00:00<?, ?it/s][INFO:swift] use_logits_to_keep: True
Train:   2%|▏         | 1/60 [00:42<41:47, 42.51s/it]{'loss': '0.3713', 'grad_norm': '0.8901', 'learning_rate': '3.333e-05', 'token_acc': '0.921', 'epoch': '0.08602', 'global_step/max_steps': '1/60', 'elapsed_time': '43s', 'remaining_time': '41m 48s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '42.51'}
Train:   8%|▊         | 5/60 [03:52<43:40, 47.64s/it]{'loss': '0.2992', 'grad_norm': '0.6541', 'learning_rate': '9.97e-05', 'token_acc': '0.9285', 'epoch': '0.4301', 'global_step/max_steps': '5/60', 'elapsed_time': '3m 53s', 'remaining_time': '42m 43s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '46.6'}
Train:  17%|█▋        | 10/60 [07:55<40:14, 48.30s/it]{'loss': '0.1605', 'grad_norm': '0.4602', 'learning_rate': '9.632e-05', 'token_acc': '0.9575', 'epoch': '0.8602', 'global_step/max_steps': '10/60', 'elapsed_time': '7m 56s', 'remaining_time': '39m 38s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '47.56'}
Train:  25%|██▌       | 15/60 [11:27<33:24, 44.53s/it]{'loss': '0.08331', 'grad_norm': '0.3851', 'learning_rate': '8.946e-05', 'token_acc': '0.9808', 'epoch': '1.258', 'global_step/max_steps': '15/60', 'elapsed_time': '11m 28s', 'remaining_time': '34m 24s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '45.86'}
Train:  33%|███▎      | 20/60 [15:20<30:25, 45.63s/it]{'loss': '0.06889', 'grad_norm': '0.494', 'learning_rate': '7.961e-05', 'token_acc': '0.9834', 'epoch': '1.688', 'global_step/max_steps': '20/60', 'elapsed_time': '15m 20s', 'remaining_time': '30m 41s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '46.01'}
Train:  42%|████▏     | 25/60 [18:57<24:59, 42.84s/it]{'loss': '0.05346', 'grad_norm': '0.2599', 'learning_rate': '6.753e-05', 'token_acc': '0.9874', 'epoch': '2.086', 'global_step/max_steps': '25/60', 'elapsed_time': '18m 58s', 'remaining_time': '26m 33s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '45.51'}
Train:  50%|█████     | 30/60 [22:49<22:48, 45.60s/it]{'loss': '0.02927', 'grad_norm': '0.1722', 'learning_rate': '5.413e-05', 'token_acc': '0.9924', 'epoch': '2.516', 'global_step/max_steps': '30/60', 'elapsed_time': '22m 50s', 'remaining_time': '22m 50s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '45.66'}
Train:  58%|█████▊    | 35/60 [26:42<19:20, 46.42s/it]{'loss': '0.03943', 'grad_norm': '0.2415', 'learning_rate': '4.041e-05', 'token_acc': '0.99', 'epoch': '2.946', 'global_step/max_steps': '35/60', 'elapsed_time': '26m 43s', 'remaining_time': '19m 5s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '45.79'}
Train:  67%|██████▋   | 40/60 [30:21<15:21, 46.09s/it]{'loss': '0.01985', 'grad_norm': '0.2619', 'learning_rate': '2.742e-05', 'token_acc': '0.9944', 'epoch': '3.344', 'global_step/max_steps': '40/60', 'elapsed_time': '30m 21s', 'remaining_time': '15m 11s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '45.53'}
Train:  75%|███████▌  | 45/60 [34:08<11:23, 45.57s/it]{'loss': '0.02995', 'grad_norm': '0.2408', 'learning_rate': '1.614e-05', 'token_acc': '0.9925', 'epoch': '3.774', 'global_step/max_steps': '45/60', 'elapsed_time': '34m 8s', 'remaining_time': '11m 23s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '45.52'}
Train:  83%|████████▎ | 50/60 [37:45<07:18, 43.90s/it]{'loss': '0.03346', 'grad_norm': '0.1691', 'learning_rate': '7.4e-06', 'token_acc': '0.9909', 'epoch': '4.172', 'global_step/max_steps': '50/60', 'elapsed_time': '37m 45s', 'remaining_time': '7m 33s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '45.3'}

Val: 100%|██████████| 8/8 [00:15<00:00,  1.91s/it]
{'eval_loss': '0.03461', 'eval_runtime': '18.36', 'eval_samples_per_second': '0.436', 'eval_steps_per_second': '0.436', 'eval_token_acc': '0.99', 'epoch': '4.172', 'global_step/max_steps': '50/60', 'elapsed_time': '38m 4s', 'remaining_time': '7m 37s', 'memory(GiB)': '14.3', 'train_speed(s/it)': '45.67'}


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



