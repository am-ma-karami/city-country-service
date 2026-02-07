import redis
from dotenv import load_dotenv
import os
import logging

load_dotenv()

CACHE_TTL_SECONDS = 600      # 10 minutes
MAX_CACHE_SIZE = 10
CACHE_KEY_PREFIX = "city:"
CACHE_ORDER_KEY = "cache:lru"

logger = logging.getLogger(__name__)

# ایجاد redis client به صورت global
redis_client = None


def _get_redis_connection():
    """دریافت اتصال Redis با تنظیمات صحیح"""
    # برای اجرای محلی باید localhost باشد، نه redis (نام Docker service)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    # اگر REDIS_HOST=redis است (از .env)، برای اجرای محلی باید localhost باشد
    if REDIS_HOST == "redis":
        REDIS_HOST = "localhost"
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    return REDIS_HOST, REDIS_PORT


def _init_redis_client():
    """ایجاد redis client با تنظیمات صحیح"""
    REDIS_HOST, REDIS_PORT = _get_redis_connection()
    
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        # تست اتصال
        client.ping()
        logger.info(f"اتصال به Redis در {REDIS_HOST}:{REDIS_PORT} برقرار شد")
        return client
    except Exception as e:
        logger.error(f"خطا در اتصال به Redis: {e}")
        return None


def _ensure_redis_client():
    """اطمینان از وجود redis client"""
    global redis_client
    if redis_client is None:
        redis_client = _init_redis_client()
    # اگر client وجود دارد اما connection مشکل دارد، reconnect کن
    if redis_client:
        try:
            redis_client.ping()
        except:
            redis_client = _init_redis_client()
    return redis_client


# Initialize on import - اما بعداً در هر فراخوانی بررسی می‌کنیم
redis_client = None


def get_from_cache(city: str):
    """دریافت مقدار از cache"""
    client = _ensure_redis_client()
    if not client:
        logger.warning("Redis client در دسترس نیست در get_from_cache")
        return None
    
    try:
        key = f"{CACHE_KEY_PREFIX}{city.lower()}"
        value = client.get(key)
        logger.info(f"get_from_cache: city={city}, key={key}, value={value}")
        
        if value:
            # به‌روزرسانی LRU list
            city_lower = city.lower()
            try:
                # اگر list است، از lrem استفاده کن
                client.lrem(CACHE_ORDER_KEY, 0, city_lower)
                client.lpush(CACHE_ORDER_KEY, city_lower)
            except redis.ResponseError:
                # اگر کلید string است یا وجود ندارد، حذف و دوباره ایجاد کن
                client.delete(CACHE_ORDER_KEY)
                client.lpush(CACHE_ORDER_KEY, city_lower)
        
        return value
    except redis.RedisError as e:
        logger.warning(f"خطا در خواندن از Redis: {e}")
        return None
    except Exception as e:
        logger.error(f"خطای غیرمنتظره در get_from_cache: {e}")
        return None


def set_cache(city: str, country_code: str):
    """ذخیره مقدار در cache"""
    client = _ensure_redis_client()
    if not client:
        logger.warning("Redis client در دسترس نیست در set_cache")
        return
    
    try:
        key = f"{CACHE_KEY_PREFIX}{city.lower()}"
        city_lower = city.lower()

        # ذخیره مقدار با TTL
        result = client.setex(key, CACHE_TTL_SECONDS, country_code)
        logger.info(f"set_cache: city={city}, key={key}, country_code={country_code}, result={result}")
        if not result:
            logger.warning(f"خطا در ذخیره کلید {key}")
            return
        
        # به‌روزرسانی LRU list
        try:
            # اگر list است، از lrem استفاده کن
            client.lrem(CACHE_ORDER_KEY, 0, city_lower)
            client.lpush(CACHE_ORDER_KEY, city_lower)
        except redis.ResponseError:
            # اگر کلید string است یا وجود ندارد، حذف و دوباره ایجاد کن
            client.delete(CACHE_ORDER_KEY)
            client.lpush(CACHE_ORDER_KEY, city_lower)

        # حذف قدیمی‌ترین آیتم اگر بیش از حد مجاز باشد
        try:
            if client.llen(CACHE_ORDER_KEY) > MAX_CACHE_SIZE:
                oldest_city = client.rpop(CACHE_ORDER_KEY)
                if oldest_city:
                    client.delete(f"{CACHE_KEY_PREFIX}{oldest_city}")
        except redis.ResponseError:
            # اگر list نیست، نادیده بگیر
            pass
                
    except redis.ConnectionError as e:
        logger.error(f"خطای اتصال به Redis: {e}")
        # تلاش برای reconnect
        global redis_client
        redis_client = None
    except redis.RedisError as e:
        logger.error(f"خطا در نوشتن به Redis: {e}")
    except Exception as e:
        logger.error(f"خطای غیرمنتظره در set_cache: {e}")
