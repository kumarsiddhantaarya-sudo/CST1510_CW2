"""
fetch_data.py - Week 8: get data from an API and save it as DATA/raw.csv.

Run it:  python fetch_data.py
"""

from pathlib import Path

import pandas as pd
import requests

# ---- Settings: the only part you change for your own data ----------------

URL = "https://api.github.com/orgs/python/repos"
PARAMS = {"per_page": 100}
RECORDS_KEY = None            # the key that holds the list of records (None if the reply is already a list)

RENAME = {"stargazers_count": "stars"}     # ugly column name -> short column name
KEEP = ["name", "language", "description", "stars", "forks",
        "open_issues", "size", "created_at", "updated_at"]   # the columns you want
MUST_HAVE = ["name", "stars"]               # drop any row that is empty in these columns

RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"


def get_data(url, params):
    """Ask the API. Return the JSON, or None if it failed."""
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("Could not get data:", error)
        return None


def make_table(data, records_key):
    """Turn the list of records into a flat table."""
    records = data[records_key] if records_key else data
    return pd.json_normalize(records, sep="_")


def tidy_data(df):
    """Rename, keep only the columns we need, drop rows with gaps."""
    df = df.rename(columns=RENAME)
    df = df[KEEP]
    df = df.dropna(subset=MUST_HAVE)
    return df


def save_data(df, path):
    """Write the table to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    data = get_data(URL, PARAMS)
    if data is not None:
        table = make_table(data, RECORDS_KEY)
        tidy = tidy_data(table)
        save_data(tidy, RAW_FILE)