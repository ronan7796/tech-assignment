import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

OUT = Path("raw/web")
OUT.mkdir(parents=True, exist_ok=True)

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_national_capitals"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    )
}

def fetch_wikipedia_table():
    resp = requests.get(WIKI_URL, timeout=20, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", {"class": "wikitable"})
    rows = []
    if not table:
        return rows
    for tr in table.find_all("tr")[1:]:
        cols = [td.get_text(strip=True) for td in tr.find_all(["td","th"])]
        if cols:
            rows.append(cols)
    return rows

def save_raw(rows, filename="capitals_raw.json"):
    p = OUT / filename
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {p}")

if __name__ == "__main__":
    rows = fetch_wikipedia_table()
    save_raw(rows)
