
from flask import Flask, jsonify
from flask_cors import CORS
from fetch import clean, infer_region, HEADERS, fetch_rows, FEDEX_URL
import csv

app = Flask(__name__)
CORS(app)

# Endpoint to merge DSPs and FedEx ISPs into one table
@app.route('/api/all-companies')
def all_companies():
    dsp_rows = fetch_rows("dsp_directory.csv", name_label="DSP")
    fedex_rows = fetch_rows("fedex_directory.csv", name_label="ISP")
    data = []
    for row in dsp_rows:
        data.append({
            "Name": row[0],
            "Type": "DSP",
            "Street Address": row[1],
            "City": row[2],
            "State/Province": row[3],
            "Zip/Postal Code": row[4],
            "Country": row[5],
            "Region": row[6],
            "Owner": row[7],
            "LinkedIn": row[8],
            "Email": row[9]
        })
    for row in fedex_rows:
        data.append({
            "Name": row[0],
            "Type": "FedEx",
            "Street Address": row[1],
            "City": row[2],
            "State/Province": row[3],
            "Zip/Postal Code": row[4],
            "Country": row[5],
            "Region": row[6],
            "Owner": row[7],
            "LinkedIn": row[8],
            "Email": row[9]
        })
    headers = ["Name", "Type"] + HEADERS[1:]
    return jsonify({"headers": headers, "rows": data})

# Endpoint to merge DSPs and FedEx ISPs into one table
@app.route('/api/fedex-data')
def fedex_data():
    rows = fetch_rows("fedex_directory.csv", name_label="ISP")
    data = []
    for row in rows:
        # row: [name, street, city, state, zipc, country, region, owner, linkedin, email]
        data.append({
            "Name": row[0],
            "Type": "FedEx",
            "Street Address": row[1],
            "City": row[2],
    # Endpoint to merge DSPs and FedEx ISPs into one table
            "State/Province": row[3],
            "Zip/Postal Code": row[4],
            "Country": row[5],
            "Region": row[6],
            "Owner": row[7],
            "LinkedIn": row[8],
            "Email": row[9]
        })
    headers = ["Name", "Type"] + HEADERS[1:]
    return jsonify({"headers": headers, "rows": data})

@app.route('/api/dsp-data')
def dsp_data():
    data = []
    with open('dsp_directory.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        header_map = {h.lower(): i for i, h in enumerate(header)}

        def idx(names):
            for n in names:
                if n.lower() in header_map:
                    return header_map[n.lower()]
            return None

        idx_name = idx(["Name","DSP Name","DSP","Company"])
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
            # Determine type
            company_type = "FedEx" if "fedex" in name.lower() or "isp" in name.lower() else "DSP"
            data.append({
                "Name": name,
                "Type": company_type,
                "Street Address": street,
                "City": city,
                "State/Province": state,
                "Zip/Postal Code": zipc,
                "Country": country,
                "Region": region,
                "Owner": owner,
                "LinkedIn": "",
                "Email": ""
            })
    headers = ["Name", "Type"] + HEADERS[1:]
    return jsonify({"headers": headers, "rows": data})

if __name__ == "__main__":
    app.run(debug=True, port=5001)