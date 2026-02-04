from pydantic import BaseModel, Field

class CityCreate(BaseModel):
    city_name: str = Field(..., example="Tehran")
    country_code: str = Field(..., example="IR")

class CityResponse(BaseModel):
    city_name: str
    country_code: str

    class Config:
        orm_mode = True