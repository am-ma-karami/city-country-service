# City Country Service

Technical Assessment – Phase 1 / Step 1

---

## Description
A FastAPI-based service for storing city and country code data.
PostgreSQL is used as the primary datastore, Redis for caching, and Kafka for logging.

---

## 🧱 Tech Stack

- Python 3.10+
- FastAPI
- PostgreSQL 15
- Redis 7
- Kafka 7.5.0
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
│   ├── schemas.py
│   ├── cache.py
│   └── kafka_producer.py
├── scripts/
│   ├── create_tables.py
│   └── load_cities.py
├── data/
│   └── cities.csv
├── requirements.txt
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Git

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd city-country-service
```

### Step 2: Configure .env File

Create a `.env` file in the project root:

```bash
POSTGRES_DB=citydb
POSTGRES_USER=cityuser
POSTGRES_PASSWORD=citypass

DATABASE_URL=postgresql://cityuser:citypass@postgres:5432/citydb

REDIS_HOST=redis
REDIS_PORT=6379

KAFKA_SERVER=kafka:9092
KAFKA_TOPIC=city-logs
```

**⚠️ Important:** If you have a local Redis (Homebrew) running, stop it first:

```bash
brew services stop redis
```

### Step 3: Start Docker Services

```bash
docker-compose up -d
```

This will start the following services:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Zookeeper (port 2181)
- Kafka (port 9092)

Check service status:

```bash
docker ps
```

### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Create Database Tables

```bash
export DATABASE_URL="postgresql://cityuser:citypass@localhost:5432/citydb"
export REDIS_HOST="localhost"
export KAFKA_BROKER="localhost:9092"
export PYTHONPATH=$(pwd):$PYTHONPATH

python scripts/create_tables.py
```

### Step 7: Start FastAPI Server

```bash
export DATABASE_URL="postgresql://cityuser:citypass@localhost:5432/citydb"
export REDIS_HOST="localhost"
export KAFKA_BROKER="localhost:9092"
export PYTHONPATH=$(pwd):$PYTHONPATH

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`.

### Step 8: (Optional) Load Initial Data

In a new terminal:

```bash
cd city-country-service
source venv/bin/activate
export PYTHONPATH=$(pwd):$PYTHONPATH

python scripts/load_cities.py
```

---

## 📚 API Documentation

After starting the server, API documentation is available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints

#### GET `/cities/{city_name}`
Get country code for a city

**Example:**
```bash
curl http://localhost:8000/cities/Tehran
```

**Response:**
```json
{
  "city": "Tehran",
  "country_code": "IR",
  "source": "database"
}
```

#### POST `/cities`
Create or update a city

**Example:**
```bash
curl -X POST "http://localhost:8000/cities" \
  -H "Content-Type: application/json" \
  -d '{"city_name": "Tehran", "country_code": "IR"}'
```

---

## 🧪 Testing

### Test Redis Cache

View all cache keys:

```bash
docker exec city_redis redis-cli KEYS "*"
```

View a specific key:

```bash
docker exec city_redis redis-cli GET "city:tehran"
```

### Test Kafka Logs

View Kafka logs:

```bash
docker exec kafka_broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic city-logs \
  --from-beginning \
  --max-messages 10 \
  --timeout-ms 5000
```

### Test API with Cache

```bash
# First request (from database)
curl http://localhost:8000/cities/Tehran

# Check Redis cache
docker exec city_redis redis-cli GET "city:tehran"

# Second request (should be from cache)
curl http://localhost:8000/cities/Tehran
```

---

## 🛠️ Useful Commands

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes

```bash
docker-compose down -v
```

### View Docker Logs

```bash
docker-compose logs -f
```

### Restart a Service

```bash
docker-compose restart redis
```

---

## 📝 Notes

- Cache TTL: 10 minutes (600 seconds)
- Max Cache Size: 10 items
- All requests are logged to Kafka
- Cache uses LRU (Least Recently Used) eviction policy

---

## 📄 License

This project is part of a technical assessment.
