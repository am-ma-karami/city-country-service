import csv
import requests

API_URL = "http://localhost:8000/cities"
DATA_FILE = "data/cities.csv"

def main():
    with open(DATA_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            response = requests.post(
                API_URL,
                json={
                    "city_name": row["city"],
                    "country_code": row["countyCode"]
                }
            )
            response.raise_for_status()

    print("City data loaded successfully")

if __name__ == "__main__":
    main()
