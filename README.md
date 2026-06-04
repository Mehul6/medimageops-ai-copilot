# MedImageOps AI Copilot

## Overview

MedImageOps AI Copilot is an end-to-end healthcare imaging data platform that combines Data Engineering, Retrieval-Augmented Generation (RAG), SQL Agents, and Local LLMs to enable natural-language analytics over medical imaging metadata.

The system ingests DICOM metadata, stores it in PostgreSQL, generates vector embeddings using SentenceTransformers, performs semantic retrieval with FAISS, and allows users to interact with imaging data through a Streamlit-based AI Copilot.

---

## Problem Statement

Healthcare organizations generate large volumes of imaging studies such as:

* CT Scans
* MRI Scans
* Ultrasounds
* X-Rays

Extracting insights from these datasets typically requires:

* SQL knowledge
* Database expertise
* Manual searching

This project enables users to ask questions in natural language instead of writing SQL queries.

Examples:

```text
Which hospital has the most studies?

How many CT scans exist?

How many chest CT scans are there?

Which manufacturer appears most often?

What body part was scanned?
```

---

## Architecture

```text
AWS S3
    ↓
DICOM Files
    ↓
Metadata Extraction
    ↓
PostgreSQL
    ↓
─────────────────────
       Router
─────────────────────
     ↙         ↘
 SQL Agent     RAG
     ↓          ↓
 PostgreSQL   FAISS
     ↓          ↓
     └────┬─────┘
          ↓
      Llama 3.2
          ↓
      Streamlit
          ↓
      AI Copilot
```

---

## Technology Stack

### Cloud

* AWS S3

### Workflow Orchestration

* Apache Airflow

### Database

* PostgreSQL

### Medical Imaging

* pydicom

### Vector Search

* FAISS

### Embeddings

* SentenceTransformers
* all-MiniLM-L6-v2

### LLM

* Ollama
* Llama 3.2 (3B)

### Frontend

* Streamlit

---

## Key Features

### Data Engineering Pipeline

* DICOM metadata ingestion
* Automated ETL workflow
* PostgreSQL storage
* Data quality validation

### Retrieval-Augmented Generation (RAG)

* Semantic search over imaging metadata
* FAISS vector database
* Local LLM inference

### SQL Agent

Converts natural-language questions into SQL queries.

Example:

```text
Question:
How many CT scans exist?

Generated SQL:
SELECT COUNT(*)
FROM dicom_metadata
WHERE modality='CT';
```

### Question Router

Automatically determines whether a question should be answered using:

* SQL Agent
* RAG Engine

---

## Dataset Statistics

| Metric           | Value   |
| ---------------- | ------- |
| Total Records    | 100,000 |
| Unique Patients  | 43,234+ |
| Hospitals        | 5       |
| Manufacturers    | 5       |
| Vector Documents | 100,010 |

---

## Performance

### PostgreSQL

Aggregate Query Latency:

```text
0.0845 seconds
```

### FAISS

Vector Index:

```text
100,010 embeddings
```

Index Build Time:

```text
3 minutes 38 seconds
```

---

## Example Results

### Hospital With Most Studies

```text
Boston Medical Center
20,164 studies
```

### Total CT Scans

```text
33,283
```

### Chest CT Scans

```text
8,132
```

### Top Manufacturer

```text
SIEMENS
20,131 studies
```

---

## Future Enhancements

* Hybrid Search (BM25 + FAISS)
* Conversational Memory
* Vision-Language Models
* Medical Image Understanding
* Terraform Infrastructure
* Docker Deployment
* CI/CD Pipelines

---

## Author

Mehul Bisht

Boston University

MS Applied Data Analytics
