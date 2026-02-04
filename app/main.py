from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import City
from app.schemas import CityCreate, CityResponse

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

