
# 🧑‍💻 Customer Onboarding Microservice (FastAPI)

A robust **FastAPI** microservice for fintech customer onboarding with multi-tier risk assessment and advanced business validation.

---

## 🧐 Use Case: Customer Onboarding with Risk Assessment

This service powers customer onboarding for a fintech application. The onboarding process features:

- **Full customer data capture:** name, email, phone, address, date of birth, national ID
- **Multi-step validation:** ensures correct formats, rejects customers under 18, enforces unique email and national ID
- **Risk assessment pipeline:**
  - Tier 1: Blacklist check (local or DB)
  - Tier 2: Async call to (mocked) external fraud API with retry/exponential backoff
  - Tier 3: Dynamic risk scoring (address, age, phone rules)
- **Error handling:** Failed assessments return error details; only safe messages exposed to clients
- **Observability:** Logs onboarding attempts with correlation ID; masks sensitive data in logs
- **Bonus**: Query onboarding status / risk score for a given customer

This solution demonstrates advanced Python and FastAPI practices, error management, and secure/loggable API design.

---

## ⚡ Features
- FastAPI-based RESTful endpoints
- Async external API integration, retries
- Pydantic-based validation (incl. regex, age, uniqueness)
- Clean, modular code (service, CRUD, API, models)
- Dockerized deployment
- Unit tests for business logic and API

---

## 📦 Requirements
- Python 3.14
- [uv](https://github.com/astral-sh/uv) (Recommended for fast installs)
- Docker (optional)

---

## 🛠️ Installation (with uv)

```bash
uv pip install -r requirements.txt
```

---

## ▶️ Running the Service

### Start locally with Uvicorn:
```bash
uvicorn app.main:app --reload
```

App docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Run with Docker:
```bash
docker-compose up --build
```

App docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 Folder Structure

```
app/
├── api/v1/           # API routes
├── core/             # DB connection
├── crud/             # DB logic
├── services/         # Business logic
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
└── main.py           # Entry point
tests/                # Unit + API tests
Dockerfile
docker-compose.yml
requirements.txt
README.md
```

---

## 🧑‍💻 Author

Rahul

---

## Boilerplate credit
[Structured Fastapi Application Boilerplate](https://github.com/maazbin/medium-blog-code/tree/main/Structured%20Fastapi%20Application%20Boilerplate)