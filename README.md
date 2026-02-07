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

## 🚀 راه‌اندازی پروژه

### پیش‌نیازها

- Python 3.10 یا بالاتر
- Docker و Docker Compose
- Git

### مرحله 1: کلون کردن پروژه

```bash
git clone <repository-url>
cd city-country-service
```

### مرحله 2: تنظیم فایل .env

فایل `.env` را در ریشه پروژه ایجاد کنید:

```bash
# Database Configuration
POSTGRES_DB=citydb
POSTGRES_USER=cityuser
POSTGRES_PASSWORD=citypass
DATABASE_URL=postgresql://cityuser:citypass@localhost:5432/citydb

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Kafka Configuration
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=city-logs
```

**⚠️ نکته مهم:** اگر Redis local (Homebrew) روی سیستم شما در حال اجرا است، ابتدا آن را متوقف کنید:

```bash
brew services stop redis
```

### مرحله 3: راه‌اندازی سرویس‌های Docker

```bash
docker-compose up -d
```

این دستور سرویس‌های زیر را راه‌اندازی می‌کند:
- PostgreSQL (پورت 5432)
- Redis (پورت 6379)
- Zookeeper (پورت 2181)
- Kafka (پورت 9092)

بررسی وضعیت سرویس‌ها:

```bash
docker ps
```

### مرحله 4: ایجاد Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # در Windows: venv\Scripts\activate
```

### مرحله 5: نصب Dependencies

```bash
pip install -r requirements.txt
```

### مرحله 6: ایجاد جداول دیتابیس

```bash
export DATABASE_URL="postgresql://cityuser:citypass@localhost:5432/citydb"
export REDIS_HOST="localhost"
export KAFKA_BROKER="localhost:9092"
export PYTHONPATH=$(pwd):$PYTHONPATH

python scripts/create_tables.py
```

### مرحله 7: راه‌اندازی سرور FastAPI

```bash
export DATABASE_URL="postgresql://cityuser:citypass@localhost:5432/citydb"
export REDIS_HOST="localhost"
export KAFKA_BROKER="localhost:9092"
export PYTHONPATH=$(pwd):$PYTHONPATH

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

سرور روی `http://localhost:8000` در دسترس خواهد بود.

### مرحله 8: (اختیاری) لود داده‌های اولیه

در یک ترمینال جدید:

```bash
cd city-country-service
source venv/bin/activate
export PYTHONPATH=$(pwd):$PYTHONPATH

python scripts/load_cities.py
```

---

## 📚 API Documentation

پس از راه‌اندازی سرور، مستندات API در آدرس زیر در دسترس است:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints

#### GET `/cities/{city_name}`
دریافت کد کشور یک شهر

**مثال:**
```bash
curl http://localhost:8000/cities/Tehran
```

**پاسخ:**
```json
{
  "city": "Tehran",
  "country_code": "IR",
  "source": "database"
}
```

#### POST `/cities`
ایجاد یا به‌روزرسانی شهر

**مثال:**
```bash
curl -X POST "http://localhost:8000/cities" \
  -H "Content-Type: application/json" \
  -d '{"city_name": "Tehran", "country_code": "IR"}'
```

---

## 🧪 تست Redis

### بررسی اتصال Redis

```bash
docker exec city_redis redis-cli PING
```

باید پاسخ `PONG` را دریافت کنید.

### بررسی کلیدهای Cache

```bash
docker exec city_redis redis-cli KEYS "*"
```

### بررسی یک کلید خاص

```bash
docker exec city_redis redis-cli GET "city:tehran"
```

### بررسی TTL یک کلید

```bash
docker exec city_redis redis-cli TTL "city:tehran"
```

### بررسی LRU List

```bash
docker exec city_redis redis-cli LRANGE "cache:lru" 0 -1
```

### پاک کردن Redis

```bash
docker exec city_redis redis-cli FLUSHALL
```

### تست کامل Cache

```bash
# 1. درخواست اول (از database)
curl http://localhost:8000/cities/Tehran

# 2. بررسی Redis
docker exec city_redis redis-cli GET "city:tehran"

# 3. درخواست دوم (باید از cache باشد)
curl http://localhost:8000/cities/Tehran
```

---

## 🧪 تست Kafka

### بررسی Topic ها

```bash
docker exec kafka_broker kafka-topics --bootstrap-server localhost:9092 --list
```

باید `city-logs` را ببینید.

### خواندن لاگ‌های Kafka

```bash
docker exec kafka_broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic city-logs \
  --from-beginning \
  --max-messages 10 \
  --timeout-ms 5000
```

### بررسی تعداد پیام‌ها

```bash
docker exec kafka_broker kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic city-logs \
  --time -1
```

### بررسی جزئیات Topic

```bash
docker exec kafka_broker kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic city-logs
```

### تست Real-time Logging

```bash
# در یک ترمینال: خواندن لاگ‌ها
docker exec kafka_broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic city-logs \
  --from-beginning

# در ترمینال دیگر: ارسال درخواست
curl http://localhost:8000/cities/TestCity
```

### نمونه لاگ Kafka

هر لاگ شامل فیلدهای زیر است:

```json
{
  "response_time_ms": 15.23,
  "cache_hit": false,
  "cache_hit_ratio": 0.5,
  "timestamp": 1770501304.9008121
}
```

---

## 🛠️ دستورات مفید

### توقف سرویس‌ها

```bash
docker-compose down
```

### توقف و حذف Volume ها

```bash
docker-compose down -v
```

### مشاهده لاگ‌های Docker

```bash
docker-compose logs -f
```

### مشاهده لاگ یک سرویس خاص

```bash
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f kafka
```

### راه‌اندازی مجدد یک سرویس

```bash
docker-compose restart redis
```

---

## 🔧 Troubleshooting

### مشکل: Redis local در حال اجرا است

اگر Redis Homebrew روی سیستم شما در حال اجرا است:

```bash
brew services stop redis
```

### مشکل: پورت 6379 در حال استفاده است

```bash
lsof -i :6379
# سپس PID را kill کنید
kill <PID>
```

### مشکل: اتصال به دیتابیس

بررسی کنید که PostgreSQL در حال اجرا است:

```bash
docker ps | grep postgres
```

### مشکل: اتصال به Kafka

بررسی کنید که Zookeeper و Kafka در حال اجرا هستند:

```bash
docker ps | grep -E "zookeeper|kafka"
```

---

## 📝 Notes

- Cache TTL: 10 دقیقه (600 ثانیه)
- Max Cache Size: 10 آیتم
- تمام درخواست‌ها در Kafka لاگ می‌شوند
- Cache از LRU (Least Recently Used) استفاده می‌کند

---

## 📄 License

This project is part of a technical assessment.
