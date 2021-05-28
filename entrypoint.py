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
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerows(data)

def load_sheets_into_csv(sheets, output_dir, creds):
    scope = ['https://spreadsheets.google.com/feeds']
    gc = gspread.service_account_from_dict(creds, scope)

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
    output_dir = os.environ.get("INPUT_TEMPDIR") or os.environ.get("GITHUB_WORKSPACE")

    outputs = load_sheets_into_csv(
        sheets=sheets,
        output_dir=output_dir,
        creds=creds,
    )

    print(f"::set-output name=results::{json.dumps(outputs)}")
