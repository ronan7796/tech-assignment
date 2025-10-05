import requests
import json
from pathlib import Path

OUT = Path("raw/api")
OUT.mkdir(parents=True, exist_ok=True)

FIELDS = [
    "name",
    "cca2",
    "cca3",
    "region",
    "subregion",
    "population",
    "area",
    "capital",
    "flags",
]

def fetch_countries():
    fields_param = ",".join(FIELDS)
    url = f"https://restcountries.com/v3.1/all?fields={fields_param}"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json()

def save_raw(data, filename="countries_raw.json"):
    p = OUT / filename
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {p}")

if __name__ == "__main__":
    try:
        data = fetch_countries()
        save_raw(data)
    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
