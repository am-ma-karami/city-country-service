from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String(100), unique=True, nullable=False, index=True)
    country_code = Column(String(10), nullable=False)

    def __repr__(self) -> str:
        return f"<City(city_name='{self.city_name}', country_code='{self.country_code}')>"
