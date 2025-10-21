# 🧠 Wikiquote NLP Capstone — Local Development Guide

## 📋 Project Overview

This repository contains the **Wikiquote NLP Capstone**, a multimodal system that:

* Builds a **graph database** from Wikiquote (quotes ↔ authors ↔ pages),
* Provides **autocomplete and search** on quotes,
* Supports **voice commands (ASR)** and **speaker recognition (TitaNet)**,
* Responds via a **chatbot** integrated with **personalized TTS**,
* Will later be deployed to the **cloud (Azure AKS)**.

---

## 🧩 Project Structure

```
wikiquote-capstone/
│
├── services/
│   ├── etl/          # Parse Wikiquote dump → graph DB + index
│   ├── autocomplete/ # Full-text search API (Elasticsearch)
│   ├── asr/          # Speech-to-text (Whisper / NeMo)
│   ├── speaker/      # Speaker recognition (TitaNet)
│   ├── chatbot/      # Dialogue manager
│   └── tts/          # Text-to-Speech generation (NeMo TTS)
│
├── webapp/           # (Optional) Frontend UI (React or Django)
├── data/             # Raw and processed data
├── tests/            # Unit and integration tests
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🧰 Requirements

| Tool           | Version | Purpose                     |
| :------------- | :------ | :-------------------------- |
| Python         | ≥ 3.10  | Backend & scripts           |
| Docker         | ≥ 24.x  | Containerization            |
| Docker Compose | ≥ 2.x   | Multi-service orchestration |
| Git            | any     | Version control             |

---

## ⚙️ Environment Setup

1. **Clone repository**

   ```bash
   git clone https://github.com/<your-username>/wikiquote-capstone.git
   cd wikiquote-capstone
   ```

2. **Create `.env` file**

   ```bash
   cp .env.example .env
   ```

   **`.env.example`:**

   ```bash
   # Global
   PROJECT_NAME=wikiquote-capstone
   ENV=local

   # Ports
   AUTOCOMPLETE_PORT=8000
   ASR_PORT=8001
   SPEAKER_PORT=8002
   CHATBOT_PORT=8003
   TTS_PORT=8004
   ETL_PORT=8005

   # Neo4j
   NEO4J_URI=bolt://neo4j:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=neo4jpassword

   # Elasticsearch
   ES_HOST=http://elasticsearch:9200
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Pre-pull images**

   ```bash
   docker pull neo4j:5.22
   docker pull elasticsearch:8.14.0
   ```

---

## 🐳 Run All Services Locally

Start everything (APIs + DBs) with:

```bash
docker-compose up --build
```

Then open these URLs:

| Service          | Port | URL                                            |
| :--------------- | :--: | :--------------------------------------------- |
| Autocomplete API | 8000 | [http://localhost:8000](http://localhost:8000) |
| ASR API          | 8001 | [http://localhost:8001](http://localhost:8001) |
| Speaker API      | 8002 | [http://localhost:8002](http://localhost:8002) |
| Chatbot API      | 8003 | [http://localhost:8003](http://localhost:8003) |
| TTS API          | 8004 | [http://localhost:8004](http://localhost:8004) |
| ETL API          | 8005 | [http://localhost:8005](http://localhost:8005) |
| Neo4j Browser    | 7474 | [http://localhost:7474](http://localhost:7474) |
| Elasticsearch    | 9200 | [http://localhost:9200](http://localhost:9200) |

---

## 🧪 Testing

Run tests with:

```bash
pytest -v
```

You can add service-specific tests in `tests/` (e.g., `test_autocomplete.py`).

---

## 🧱 Common Development Commands

| Task                   | Command                          |
| :--------------------- | :------------------------------- |
| Rebuild containers     | `docker-compose build`           |
| Start containers       | `docker-compose up -d`           |
| Stop all services      | `docker-compose down`            |
| View logs              | `docker-compose logs -f`         |
| Run individual service | `docker-compose up autocomplete` |
| Clean all images       | `docker system prune -a`         |

---

## 🧾 Notes for Developers

* Keep each service **self-contained** (its own `Dockerfile`, `app.py`, and logic).
* Common utilities (e.g., logging, config) can go in `services/common/`.
* Start implementing services in order:

  1. ETL → 2. Autocomplete → 3. ASR → 4. Speaker → 5. Chatbot → 6. TTS.
* Use `pytest` + GitHub Actions CI to validate builds automatically.

---

## 🌍 Next Stage (Cloud Deployment)

When all local services work:

* Push Docker images to your container registry (Azure ACR or GHCR).
* Deploy to Azure AKS using the same `docker-compose.yml` as reference for Kubernetes manifests.
* Add CI/CD deployment steps in `.github/workflows/ci.yml`.

---

## 📜 License & Credits

This project is for the **NLP Capstone Course**, integrating speech, language, and graph-based retrieval technologies using **FastAPI**, **Neo4j**, **Elasticsearch**, and **NVIDIA NeMo**.

