import json
from pathlib import Path
import pandas as pd
from datetime import datetime

ROOT = Path.cwd()
RAW_API = ROOT / "crawler" / "raw" / "api" / "countries_raw.json"
RAW_WEB = ROOT / "crawler" / "raw" / "web" / "capitals_raw.json"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_api():
    with open(RAW_API, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def normalize_countries(api_data):
    rows = []
    for c in api_data:
        row = {
            "cca3": c.get("cca3"),
            "name_common": c.get("name", {}).get("common"),
            "name_official": c.get("name", {}).get("official"),
            "region": c.get("region"),
            "subregion": c.get("subregion"),
            "capital": ", ".join(c.get("capital") or []),
            "population": c.get("population"),
            "area": c.get("area"),
            "latlng_0": c.get("latlng", [None, None])[0],
            "latlng_1": c.get("latlng", [None, None])[1],
            "timezones": ";".join(c.get("timezones") or []),
            "currencies": ";".join((c.get("currencies") or {}).keys()),
            "languages": ";".join((c.get("languages") or {}).values()) if c.get("languages") else None,
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    return df

def load_web():
    import json
    with open(RAW_WEB, "r", encoding="utf-8") as f:
        rows = json.load(f)
    parsed = []
    for r in rows:
        country = r[0] if len(r) > 0 else None
        capital = r[1] if len(r) > 1 else None
        parsed.append({"country_name": country, "capital_raw": capital, "raw_row": r})
    return pd.DataFrame(parsed)

def join_data(countries_df, web_df):
    merged = countries_df.merge(web_df, left_on="name_common", right_on="country_name", how="left")
    missing = merged[merged["capital_raw"].isna()]
    if not missing.empty:
        alt = countries_df.merge(web_df, left_on="capital", right_on="capital_raw", how="left", suffixes=("","_web"))
        merged["capital_from_web"] = merged["capital_raw"].fillna(alt["capital_raw"])
    return merged

def export_all(df):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    csv_out = OUT_DIR / f"countries_{ts}.csv"
    parquet_out = OUT_DIR / f"countries_{ts}.parquet"
    excel_out = OUT_DIR / f"countries_{ts}.xlsx"

    df.to_csv(csv_out, index=False)
    print(f"Wrote {csv_out}")

    df.to_parquet(parquet_out, index=False)
    print(f"Wrote {parquet_out}")

    with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="countries", index=False)
    print(f"Wrote {excel_out}")

    return csv_out, parquet_out, excel_out

if __name__ == "__main__":
    api_data = load_api()
    countries_df = normalize_countries(api_data)
    web_df = load_web()
    merged = join_data(countries_df, web_df)
    csv_path, parquet_path, excel_path = export_all(merged)
