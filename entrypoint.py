import csv
import json
import logging
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger("gsheets-to-csv")
logger.setLevel(logging.INFO)

def write_worksheet_to_csv(data, file):
    with open(file, "w", newline="") as csvfile:
        #writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerows(data)

def load_sheets_into_csv(sheets, output_dir, creds):
    scope = ['https://spreadsheets.google.com/feeds']
    #creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    #creds = ServiceAccountCredentials.from_dict(creds, scope)
    gc = gspread.service_account_from_dict(creds, scope)
    #gc = gspread.authorize(creds)

    os.makedirs(output_dir, exist_ok=True)
    outputs = []

    for i, sh in enumerate(sheets):
        if "id" not in sh:
            logger.warning("Id required to lookup sheet")
            continue
        sheet = gc.open_by_key(key=sh["id"])

        if "title" in sh:
            ws = sheet.worksheet(title=sh["title"])
        else:
            logger.info("Sheet title not specified; selecting first")
            ws = sheet.worksheets()[0]

        if "range" in sh:
            data = ws.get(sh["range"])
        else:
            data = ws.get()

        filename = os.path.join(output_dir, f"tmp{i}.csv")
        write_worksheet_to_csv(data, filename)
        outputs.append(filename)
    return outputs

if __name__=="__main__":
    creds = json.loads(os.environ.get("INPUT_CREDS", {}))
    sheets = json.loads(os.environ.get("INPUT_SHEETS", []))
    output_dir = os.environ.get("INPUT_TEMPDIR") or os.environ.get("RUNNER_TEMP")
    print(sheets)
    print(output_dir)
    print(creds)
    #creds_path = "/Users/max-hoffman/Downloads/dolt-action-test-a2c10c0bd7fd.json"
    #output_dir = "/Users/max-hoffman/Documents/dolt/actify/gsheets-to-csv/tmp"
    #sheets = [
        #dict(
            #id="1aaEoK1InHzEYjw6RNpuPvMoR-OKxYKXOjfhb1eE5Y_Y",
            #title="Sheet2",
            #range="A1:Z30",
        #),
        #dict(
            #id="1aaEoK1InHzEYjw6RNpuPvMoR-OKxYKXOjfhb1eE5Y_Y",
            #title="temp",
            ##range="A1:Z30",
        #),
    #]

    outputs = load_sheets_into_csv(
        sheets=sheets,
        output_dir=output_dir,
        creds=creds,
    )
    print(outputs)
    print(f"::set-output name=results::{json.dumps(outputs)}")

