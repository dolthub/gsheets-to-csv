# Gsheets to CSV

This is a GitHub Action plugin that reads good sheets into CSV temporary
files.

In the example below, we first read Google Sheets with
specific ids and tab names
into CSV files, and then count the number of lines in each
file. The inital checkout stage has been necessary during
development to persist temporary files in a common working directory.

The `range` parameter is optional. If `name` is omitted, a sheet's first
tab will be selected for download.

The `GSHEET_CREDENTIALS` parameter is a json file containing credentials
to authorize a Google API service account. The account must have
permissions to access the Google Sheets of interest. This parameter is
currently required.

```yml
name: GSheets Test

on:
  push:
env:
  id: '1ZbkUf1tAzt_Lhh1G8ezDgyU1AdUnm26xzPYLtdtWsI8'
  name: 'temp'
  range: 'A1:I8'

jobs:
  hello_world_job:
    runs-on: ubuntu-latest
    name: A job to say hello
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      - name: Pull GSheet data
        id: 'sheet_to_csv'
        uses: gsheets-to-csv@1
        with:
          creds: ${{ secrets.GSHEET_CREDENTIALS }}
          sheets: |
            [
              { "id": "${{ env.id }}", "range": "${{ env.range }}", "title": "${{ env.name }}" },
              { "id": "${{ env.id }}" }
            ]
      - name: Print CSV
        id: "print_csv"
        run: |
          echo "$FILES" | jq -c '.[]' | while read i; do
              eval file=$i
              echo "$(wc -l $file)"
          done
        env:
          FILES: ${{ steps.sheet_to_csv.outputs.results }}
```

This sample output from the "Print CSV" step is:

```bash
12 Test/tmp0.csv
13500 Test/tmp1.csv
```
