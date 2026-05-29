# Classify - Finetune

- [Classify](#classify)
- [Fine-tuning Report: Document Information Extraction](#fine-tuning-report-document-information-extraction)
  - [01 - Dataset Preparation](#01---dataset-preparation)
  - [02 - Create Custom Dataset Swift Format](#02---create-custom-dataset-swift-format)
  - [03 - Fine-tune](#03---fine-tune)
  - [04 - Inference](#04---inference)

# Classify

- For the classification step, I do not use standalone base models. Instead, I use a fine-tuned Large Language Model for document classification.
- This LLM processes OCR text and spatial data simultaneously to output accurate labels.

# Fine-Tuning Report: Document Information Extraction

- My notebook for fine-tuning:
  [NotebookColab](https://colab.research.google.com/drive/1a24_laFE-8eGvCojM0z3_UMh_O7SQx8k?authuser=3#scrollTo=tP3LSL97N2wx)
  

*Model*: [Qwen2-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct)

![qwen2-vl](img/qwen2_vl.jpg)


*Framework*: swift


*Platform*: Google Colab

# 01 - Dataset Preparation
- I have used the data at [synthetic-doc-generator-data](https://github.com/NguyenNgocChien-01/synthetic-doc-generator/tree/main/dataset).

- Folder strcuture:

```
data/
├── documents/
|──────aus_passport/
|──────aus_medicare_card/green/, ...
|
└── labels/  (mirrors documents) ...
```

- Now, I have ~20 image + json sample per passport, vic driver license, vic wwc, 3 type medicare card = ~ 100 sample.
-  Schema json each type: [Step 2](ocr-project/OCR-Step2-Design-Schema.MD)
  
# 02 -  Create Custom Dataset Swift Format
<!-- (https://drive.google.com/file/d/1BmtN3q8E-xjYm96ZBzOxnfXOVGZuIh8m/view?usp=drive_link) -->
## Goal: convert raw images and JSON labels into SWIFT training format.
**1. Load data from local:**


**2. Split data:** 

- **If** *n_sample* < 3 ==> no split.
- **Else** ==> Stratified by doc type, 80% train / 10% dev / 10% test, random seed 42. Types with fewer than 3 samples go entirely to train.
  
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
└── passport_00001.png ...

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
  {
    "messages": [
      {
        "role": "system",
        "content": "You are a document processing expert skilled in extracting information from official documents."
      },
      {
        "role": "user",
        "content": "Document: <image>\nExtract the following fields as JSON: document_type, issuing_country, document_number, family_name, given_names, nationality, date_of_birth, sex, date_of_issue, date_of_expiry, place_of_birth, authority, mrz_line1, mrz_line2"
      },
      {
        "role": "assistant",
        "content": "{\"document_type\": \"AUS_PASSPORT\", \"issuing_country\": \"AUS\", \"document_number\": \"HB5437923\", \"family_name\": \"BALDWIN\", \"given_names\": \"KIMBERLY\", \"nationality\": \"KUMARELIAN\", \"date_of_birth\": \"1997-05-07\", \"sex\": \"F\", \"date_of_issue\": \"2012-03-04\", \"date_of_expiry\": \"2029-08-09\", \"place_of_birth\": \"ANELCCHSER\", \"authority\": \"CANEHERA\", \"mrz_line1\": \"P<AUSBALDWIN<<KIMBERLY<<<<<<<<<<<<<<<<<<<<<<\", \"mrz_line2\": \"CJ1423646<AUS970507F290829<<<<<<<<<<<<<<<<01\"}"
      }
    ],
    "images": [
      "/content/drive/MyDrive/INTERN-BIWOCO/sample-for-multi-modal-document-to-json-with-sagemaker-ai/data/swift_dataset/images/aus_passport_00010.png"
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
Train:   0%|          | 0/60 [00:00<?, ?it/s][INFO:swift] use_logits_to_keep: True
Train:   2%|▏         | 1/60 [00:55<54:36, 55.53s/it]{'loss': '0.6647', 'grad_norm': '0.8371', 'learning_rate': '3.333e-05', 'token_acc': '0.8539', 'epoch': '0.08421', 'global_step/max_steps': '1/60', 'elapsed_time': '56s', 'remaining_time': '54m 37s', 'memory(GiB)': '14.34', 'train_speed(s/it)': '55.54'}
Train:   8%|▊         | 5/60 [04:14<46:25, 50.65s/it]{'loss': '0.6151', 'grad_norm': '0.6511', 'learning_rate': '9.97e-05', 'token_acc': '0.8669', 'epoch': '0.4211', 'global_step/max_steps': '5/60', 'elapsed_time': '4m 14s', 'remaining_time': '46m 35s', 'memory(GiB)': '14.34', 'train_speed(s/it)': '50.81'}
Train:  17%|█▋        | 10/60 [08:27<43:03, 51.66s/it]{'loss': '0.446', 'grad_norm': '0.6618', 'learning_rate': '9.632e-05', 'token_acc': '0.8929', 'epoch': '0.8421', 'global_step/max_steps': '10/60', 'elapsed_time': '8m 27s', 'remaining_time': '42m 17s', 'memory(GiB)': '14.34', 'train_speed(s/it)': '50.74'}
Train:  20%|██        | 12/60 [10:03<39:41, 49.61s/it]
Train:  25%|██▌       | 15/60 [12:53<39:29, 52.65s/it]{'loss': '0.2692', 'grad_norm': '0.4791', 'learning_rate': '8.946e-05', 'token_acc': '0.9388', 'epoch': '1.253', 'global_step/max_steps': '15/60', 'elapsed_time': '12m 53s', 'remaining_time': '38m 40s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '51.54'}
Train:  33%|███▎      | 20/60 [17:01<33:38, 50.47s/it]{'loss': '0.1866', 'grad_norm': '0.6824', 'learning_rate': '7.961e-05', 'token_acc': '0.9535', 'epoch': '1.674', 'global_step/max_steps': '20/60', 'elapsed_time': '17m 1s', 'remaining_time': '34m 3s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '51.07'}
Train:  42%|████▏     | 25/60 [21:22<31:20, 53.73s/it]{'loss': '0.1085', 'grad_norm': '0.3586', 'learning_rate': '6.753e-05', 'token_acc': '0.9717', 'epoch': '2.084', 'global_step/max_steps': '25/60', 'elapsed_time': '21m 22s', 'remaining_time': '29m 55s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '51.28'}
Train:  50%|█████     | 30/60 [25:32<25:19, 50.66s/it]{'loss': '0.08856', 'grad_norm': '0.3673', 'learning_rate': '5.413e-05', 'token_acc': '0.9781', 'epoch': '2.505', 'global_step/max_steps': '30/60', 'elapsed_time': '25m 32s', 'remaining_time': '25m 32s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '51.07'}
Train:  58%|█████▊    | 35/60 [29:38<20:32, 49.29s/it]{'loss': '0.08122', 'grad_norm': '0.5321', 'learning_rate': '4.041e-05', 'token_acc': '0.9772', 'epoch': '2.926', 'global_step/max_steps': '35/60', 'elapsed_time': '29m 39s', 'remaining_time': '21m 11s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '50.83'}
Train:  67%|██████▋   | 40/60 [34:01<17:02, 51.12s/it]{'loss': '0.07087', 'grad_norm': '0.2541', 'learning_rate': '2.742e-05', 'token_acc': '0.9814', 'epoch': '3.337', 'global_step/max_steps': '40/60', 'elapsed_time': '34m 2s', 'remaining_time': '17m 1s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '51.05'}
Train:  75%|███████▌  | 45/60 [38:13<12:27, 49.84s/it]{'loss': '0.05639', 'grad_norm': '0.5134', 'learning_rate': '1.614e-05', 'token_acc': '0.983', 'epoch': '3.758', 'global_step/max_steps': '45/60', 'elapsed_time': '38m 14s', 'remaining_time': '12m 45s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '50.98'}
Train:  83%|████████▎ | 50/60 [42:39<08:56, 53.64s/it]{'loss': '0.06318', 'grad_norm': '0.3856', 'learning_rate': '7.4e-06', 'token_acc': '0.9821', 'epoch': '4.168', 'global_step/max_steps': '50/60', 'elapsed_time': '42m 40s', 'remaining_time': '8m 32s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '51.2'}
Train:  92%|█████████▏| 55/60 [46:49<04:14, 50.81s/it]{'loss': '0.04668', 'grad_norm': '0.4049', 'learning_rate': '1.89e-06', 'token_acc': '0.987', 'epoch': '4.589', 'global_step/max_steps': '55/60', 'elapsed_time': '46m 50s', 'remaining_time': '4m 15s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '51.08'}
Train: 100%|██████████| 60/60 [50:53<00:00, 47.92s/it]{'loss': '0.05729', 'grad_norm': '0.5419', 'learning_rate': '0', 'token_acc': '0.9833', 'epoch': '5', 'global_step/max_steps': '60/60', 'elapsed_time': '50m 53s', 'remaining_time': '0s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '50.89'}


Val: 100%|██████████| 8/8 [00:15<00:00,  1.91s/it]
{'eval_loss': '0.03952', 'eval_runtime': '18.44', 'eval_samples_per_second': '0.434', 'eval_steps_per_second': '0.434', 'eval_token_acc': '0.9796', 'epoch': '5', 'global_step/max_steps': '60/60', 'elapsed_time': '51m 32s', 'remaining_time': '0s', 'memory(GiB)': '14.4', 'train_speed(s/it)': '51.53'}


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

```
INPUT:

<<< extract data from <<image>> with format json 
{   "document_type": "",
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

Input an image path or URL <<< /content/drive/MyDrive/INTERN-BIWOCO/sample-for-multi-modal-document-to-json-with-sagemaker-ai/data/swift_dataset/images/aus_passport_00010.png

OUTPUT:

{
    "document_type": "AUS_PASSPORT", 
    "issuing_country": "AUS",
    "document_number": "HB5437923",
    "family_name": "BALDWIN", 
    "given_names": "KIMBERLY", 
    "nationality": "KUMARELIAN",
    "date_of_birth": "1997-05-07", 
    "sex": "F", 
    "date_of_issue": "2012-03-04",
    "date_of_expiry": "2029-09-08",
    "place_of_birth": "CANEHERA",
    "authority": "CANBERRA", 
    "mrz_line1": "P<AUSBALDWIN<<KIMBERLY<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
    "mrz_line2": "CJ1423646<AUS970507F290829<<<<<<<<<<<<<<<<01"
}

--> There are some wrong with mrz.

# 05 - Evalution
![Evalution](img/evalution/evalution-model.png)

# Evaluation Results on Test Data

## Australian Driver License — VIC


Update later...

# ![driver-license](img/evalution/aus_driver_license_vic_00004.png)

# | | Field | Ground Truth | Prediction |
# |:---:|:---|:---|:---|
# | ✓ | address | UNIT 82 | UNIT 82 |
# | ✓ | card number | D3409784 | D3409784 |
# | ✓ | class | CAR | CAR |
# | ✓ | date of birth | 1987-07-07 | 1987-07-07 |
# | ✓ | expiry date | 2029-10-18 | 2029-10-18 |
# | ✓ | first name | DANIEL | DANIEL |
# | ✓ | last name | FOWLER | FOWLER |
# | ✓ | licence number | 822170556 | 822170556 |
# | ✓ | middle name | None | None |
# | ✓ | state | VIC | VIC |
# | ✓ | document type | AUS_DRIVER_LICENSE | AUS_DRIVER_LICENSE |

# **11/11 fields correct** 

---

## Australian Passport

![passport](img/evalution/aus_passport_00018.png)

| | Field | Ground Truth | Prediction |
|:---:|:---|:---|:---|
| ✓ | authority | CANBERRA | CANBERRA |
| ✓ | date of birth | 1982-01-09 | 1982-01-09 |
| ✓ | date of issue | 2012-03-03 | 2012-03-03 |
| ✓ | expiry date | 2022-03-03 | 2022-03-03 |
| ✓ | first name | KEITH | KEITH |
| ✓ | gender | M | M |
| ✓ | last name | GRANT | GRANT |
| ✗ | mrz line 1 | `P<AUSGRANT<<KEITH<<<<<<<<<<<<<<<<<<<<<<<<<<< ` | `P<AUSGRANT<<KEITH<<<<<<<<<<<<<<<<<<<<<<<<<` |
| ✓ | mrz line 2 | `SP2450814<AUS920109M291023<<<<<<<<<<<<<<<<09` | `SP2450814<AUS920109M291023<<<<<<<<<<<<<<<<09` |
| ✓ | nationality | AUSTRALIAN | AUSTRALIAN |
| ✓ | number | SP2450814 | SP2450814 |
| ✓ | place of birth | NE JANDON | NE JANDON |
| ✓ | document type | AUS_PASSPORT | AUS_PASSPORT |

**12/13 fields correct** — MRZ line 1 trailing `<` count mismatch

---

## Medicare Card

### Single member

![green_medicare](img/evalution/aus_medicare_card_green_00016.png)

| Status | Field | Ground Truth | Prediction |
| :---: | :--- | :--- | :--- |
| ✓ | cardholders | `[{pos:1, FERNANDO R MOORE}]` | `[{pos:1, FERNANDO R MOORE}]` |
| ✓ | document type | AUS_MEDICARE_CARD | AUS_MEDICARE_CARD |
| ✓ | expiry date | 2020-07-29 | 2020-07-29 |
| ✓ | card number | 6406 75093 0 | 6406 75093 0 |
| ✓ | card type | regular | regular |

**5/5 fields correct**

### Multiple members

![yellow-medicare](img/evalution/aus_medicare_card_yellow_00023.png)

| Status | Field | Ground Truth | Prediction |
| :---: | :--- | :--- | :--- |
| ✓ | `cardholders` | `[{"position": 1, "first_name": "MARY", "middle_initial": null, "last_name": "WOODS", "full_name": "1 MARY WOODS"}, {"position": 2, "first_name": "TOMMY", "middle_initial": null, "last_name": "DURAN", "full_name": "2 TOMMY DURAN"}, {"position": 3, "first_name": "PAUL", "middle_initial": null, "last_name": "JACKSON", "full_name": "3 PAUL JACKSON"}, {"position": 4, "first_name": "CHRISTINA", "middle_initial": null, "last_name": "CARLSON", "full_name": "4 CHRISTINA CARLSON"}, {"position": 5, "first_name": "JAMES", "middle_initial": "R", "last_name": "LOPEZ", "full_name": "5 JAMES R LOPEZ"}]` | `[{"position": 1, "first_name": "MARY", "middle_initial": null, "last_name": "WOODS", "full_name": "1 MARY WOODS"}, {"position": 2, "first_name": "TOMMY", "middle_initial": null, "last_name": "DURAN", "full_name": "2 TOMMY DURAN"}, {"position": 3, "first_name": "PAUL", "middle_initial": null, "last_name": "JACKSON", "full_name": "3 PAUL JACKSON"}, {"position": 4, "first_name": "CHRISTINA", "middle_initial": null, "last_name": "CARLSON", "full_name": "4 CHRISTINA CARLSON"}, {"position": 5, "first_name": "JAMES", "middle_initial": "R", "last_name": "LOPEZ", "full_name": "5 JAMES R LOPEZ"}]` |
| ✓ | `document_type` | AUS_MEDICARE_CARD | AUS_MEDICARE_CARD |
| ✓ | `medicare_card_expiry_date` | 2030-11-07 | 2030-11-07 |
| ✓ | `medicare_card_number` | 4293 36425 7 | 4293 36425 7 |
| ✓ | `medicare_card_type` | reciprocal health care | reciprocal health care |

**5/5 fields correct**

---

## Working With Children (WWC) Card

![wwc](img/evalution/aus_wwc_card_vic_00007.png)

| Status | Field | Ground Truth | Prediction |
| :---: | :--- | :--- | :--- |
| ✓ | card number | 626067Z-52 | 626067Z-52 |
| ✓ | expiry date | 2027-10-30 | 2027-10-30 |
| ✓ | first name | JASON | JASON |
| ✓ | issuing state | VIC | VIC |
| ✓ | last name | PHILLIPS | PHILLIPS |
| ✓ | type | EMPLOYEE | EMPLOYEE |

**6/6 fields correct**

---