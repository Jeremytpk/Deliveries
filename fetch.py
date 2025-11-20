import re
import csv
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

# URLs
AMAZON_CSV = "dsp_directory.csv"
FEDEX_URL = "fedex_directory.csv"

# Output paths
AMAZON_CSV = "amazon_dsp_directory.csv"
AMAZON_XLSX = "amazon_dsp_directory.xlsx"
FEDEX_CSV = "fedex_isp_directory.csv"
FEDEX_XLSX = "fedex_isp_directory.xlsx"

HEADERS = [
    "Name",
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

def fetch_rows(url, name_label="DSP"):
    # Read from local CSV for Amazon DSPs or FedEx ISPs
    csv_path = url if url.endswith('.csv') else AMAZON_CSV
    data = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        header_map = {h.lower(): i for i, h in enumerate(header)}

        def idx(names):
            for n in names:
                if n.lower() in header_map:
                    return header_map[n.lower()]
            return None

        idx_name = idx(["Name","DSP Name","Company","DSP"])
        idx_street = idx(["Street Address","Address"])
        idx_city = idx(["City"])
        idx_state = idx(["State","State/Province","Province","Region"])
        idx_zip = idx(["Zip","Zip Code","Postal Code","Zip/Postal Code"])
        idx_country = idx(["Country"])
        idx_owner = idx(["Owner","Owner Name"])

        for row in reader:
            name = clean(row[idx_name]) if idx_name is not None else ""
            street = clean(row[idx_street]) if idx_street is not None else ""
            city = clean(row[idx_city]) if idx_city is not None else ""
            state = clean(row[idx_state]) if idx_state is not None else ""
            zipc = clean(row[idx_zip]) if idx_zip is not None else ""
            country = clean(row[idx_country]) if idx_country is not None else ""
            owner = clean(row[idx_owner]) if idx_owner is not None else ""
            region = infer_region(country)
            data.append([name, street, city, state, zipc, country, region, owner, "", ""])
    return data

def save_csv(rows, path):
    with open(path,"w",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(rows)

def save_xlsx(rows, path, sheet_name):
    from openpyxl.worksheet.table import Table, TableStyleInfo
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(HEADERS)
    for row in rows:
        ws.append(row)
    # Define table range
    end_col = chr(ord('A') + len(HEADERS) - 1)
    end_row = len(rows) + 1
    tab = Table(displayName="DSPTable", ref=f"A1:{end_col}{end_row}")
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    tab.tableStyleInfo = style
    ws.add_table(tab)
    wb.save(path)

def main():
    print("Loading DSPs from dsp_directory.csv...")
    dsp_rows = fetch_rows("dsp_directory.csv")
    print(f"Loaded {len(dsp_rows)} DSP entries.")

    save_csv(dsp_rows, "dsp_directory.csv")
    save_xlsx(dsp_rows, "dsp_directory.xlsx", "DSPs")

    print("DSP files: dsp_directory.csv, dsp_directory.xlsx")

    print("Loading FedEx ISPs from fedex_directory.csv...")
    fedex_rows = fetch_rows("fedex_directory.csv")
    print(f"Loaded {len(fedex_rows)} FedEx ISP entries.")

    save_csv(fedex_rows, "fedex_directory.csv")
    save_xlsx(fedex_rows, "fedex_directory.xlsx", "FedEx ISPs")

    print("FedEx ISP files: fedex_directory.csv, fedex_directory.xlsx")

if __name__ == "__main__":
    main()

