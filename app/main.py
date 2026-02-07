from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import time

from app.database import SessionLocal
from app.models import City
from app.schemas import CityCreate, CityResponse
from app.cache import get_from_cache, set_cache
from app.kafka_producer import log_request

app = FastAPI(
    title="City Country Service",
    version="0.1.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/cities", response_model=CityResponse)
def create_or_update_city(
    payload: CityCreate,
    db: Session = Depends(get_db)
):
    city = db.query(City).filter(
        City.city_name == payload.city_name
    ).first()

    if city:
        city.country_code = payload.country_code
    else:
        city = City(
            city_name=payload.city_name,
            country_code=payload.country_code
        )
        db.add(city)

    db.commit()
    db.refresh(city)

    return city


@app.get("/cities/{city_name}")
def get_country_code(
    city_name: str,
    db: Session = Depends(get_db)
):
    start_time = time.time()

    
    cached = get_from_cache(city_name)
    if cached:
        duration = (time.time() - start_time) * 1000
        log_request(duration, cache_hit=True)
        return {
            "city": city_name,
            "country_code": cached,
            "source": "cache"
        }

    
    city = db.query(City).filter(
        City.city_name == city_name
    ).first()

    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    
    set_cache(city_name, city.country_code)

    duration = (time.time() - start_time) * 1000
    log_request(duration, cache_hit=False)

    return {
        "city": city_name,
        "country_code": city.country_code,
        "source": "database"
    }