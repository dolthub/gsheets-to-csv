import csv
import os

import pytest

from gsheets_to_csv import write_worksheet_to_csv


@pytest.fixture(scope="function")
def tmpfile(tmp_path):
    return os.path.join(tmp_path, "test.csv")


@pytest.fixture(scope="function")
def csv_array():
    return [
        ["name", "score"],
        ["Mary", "4"],
        ["Mark", "2"],
    ]


@pytest.fixture(scope="function")
def csv_dict():
    return [
        dict(name="Mary", score="4"),
        dict(name="Mark", score="2"),
    ]


def test_write_worksheet(csv_array, csv_dict, tmpfile):
    write_worksheet_to_csv(csv_array, tmpfile)

    with open(tmpfile, "r") as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=["name", "score"])
        res = [row for row in reader][1:]

    assert res == csv_dict


def test_load_sheets():
    # mock gspread.service_account_from_dict
    # mock gc.open_by_key
    # mock sheet.worksheet
    # mock worksheet.get
    pass
