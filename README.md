# City Country Service

Technical Assessment – Phase 1 / Step 1

---

## Description
A FastAPI-based service for storing city and country code data.
PostgreSQL is used as the primary datastore and runs via Docker.

---

## 🧱 Tech Stack

- Python 3.10+
- FastAPI
- PostgreSQL 15
- SQLAlchemy
- Docker & Docker Compose

---

## 📁 Project Structure

```text
city-country-service/
├── docker-compose.yml
├── .env
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── schemas.py
├── scripts/
│   ├── create_tables.py
│   └── load_cities.py
├── data/
│   └── cities.csv
├── requirements.txt
└── README.md