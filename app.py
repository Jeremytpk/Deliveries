from flask import Flask, jsonify
from flask_cors import CORS
from fetch import clean, infer_region, HEADERS
import csv

app = Flask(__name__)
CORS(app)

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
            data.append({
                "DSP Name": dsp,
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
    return jsonify({"headers": HEADERS, "rows": data})

if __name__ == "__main__":
    app.run(debug=True)