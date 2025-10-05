import pandas as pd
from pathlib import Path

OUT_SQL = Path("sql")
OUT_SQL.mkdir(exist_ok=True)

def df_to_upsert_sql(df: pd.DataFrame, table_name="countries", conflict_cols=None):
    if conflict_cols is None:
        conflict_cols = ["cca3"]

    cols = list(df.columns)

    col_list = ", ".join(f'"{c}"' for c in cols)

    values_sql = []
    for _, row in df.iterrows():
        vals = []
        for c in cols:
            v = row[c]
            if pd.isna(v):
                vals.append("NULL")
            else:
                s = str(v).replace("'", "''")
                vals.append(f"'{s}'")
        values_sql.append(f"({', '.join(vals)})")

    all_values = ",\n  ".join(values_sql)

    conflict_cols_list = ", ".join(f'"{c}"' for c in conflict_cols)
    set_list = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in cols if c not in conflict_cols)

    sql = (
        f'INSERT INTO "{table_name}" ({col_list})\n'
        f'VALUES\n  {all_values}\n'
        f'ON CONFLICT ({conflict_cols_list}) DO UPDATE\n'
        f'SET {set_list};'
    )

    return sql


if __name__ == "__main__":
    import glob
    files = glob.glob("outputs/countries_*.csv")
    if not files:
        print("No CSV output found. Run etl_pipeline first")
    else:
        files = sorted(files)
        df = pd.read_csv(files[-1], dtype=str)
        sql_text = df_to_upsert_sql(df, table_name="countries", conflict_cols=["cca3"])
        out = OUT_SQL / "countries_upsert.sql"
        out.write_text(sql_text, encoding="utf-8")
        print(f"Wrote {out}")
