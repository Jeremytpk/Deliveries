import re
import csv
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

CSV_PATH = "dsp_directory.csv"
XLSX_PATH = "usa_international_dsp_directory.xlsx"

HEADERS = [
    "DSP Name",
    "Street Address",
    "City",
    "State/Province",
    "Zip/Postal Code",
    "Country",
    "Region",
    "Owner",
    "LinkedIn",
    "Email",
]

def infer_region(country: str) -> str:
    c = (country or "").strip().lower()
    if c in {"usa","united states","u.s.a.","us"}:
        return "USA"
    if c == "canada":
        return "Canada"
    if c in {"united kingdom","uk"}:
        return "UK"
    eu_countries = {
        "germany","france","spain","italy","netherlands","belgium","poland",
        "sweden","denmark","ireland","austria","czechia","czech republic",
        "portugal","finland","greece","hungary","romania","slovakia","slovenia",
        "bulgaria","croatia","estonia","latvia","lithuania","luxembourg","malta",
    }
    if c in eu_countries:
        return "EU"
    return "Other"

def clean(text: str) -> str:
    return re.sub(r"\s+"," ", text).strip() if text else ""

def fetch_rows():
    data = []
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        header_map = {h.lower(): i for i, h in enumerate(header)}

        def idx(names):
            for n in names:
                if n.lower() in header_map:
                    return header_map[n.lower()]
            return None

        idx_dsp = idx(["DSP Name","DSP","Company"])
        idx_street = idx(["Street Address","Address"])
        idx_city = idx(["City"])
        idx_state = idx(["State","State/Province","Province","Region"])
        idx_zip = idx(["Zip","Zip Code","Postal Code","Zip/Postal Code"])
        idx_country = idx(["Country"])
        idx_owner = idx(["Owner","Owner Name"])

        for row in reader:
            dsp = clean(row[idx_dsp]) if idx_dsp is not None else ""
            street = clean(row[idx_street]) if idx_street is not None else ""
            city = clean(row[idx_city]) if idx_city is not None else ""
            state = clean(row[idx_state]) if idx_state is not None else ""
            zipc = clean(row[idx_zip]) if idx_zip is not None else ""
            country = clean(row[idx_country]) if idx_country is not None else ""
            owner = clean(row[idx_owner]) if idx_owner is not None else ""
            region = infer_region(country)
            data.append([dsp, street, city, state, zipc, country, region, owner, "", ""])
    return data

## Removed CSV saving as per user request

def save_xlsx(rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "DSP Directory"
    ws.append(HEADERS)
    for row in rows:
        ws.append(row)
    wb.save(XLSX_PATH)

def main():
    rows = fetch_rows()
    print(f"Fetched {len(rows)} DSP entries.")
    save_xlsx(rows)
    print("File saved:", XLSX_PATH)

if __name__ == "__main__":
    main()