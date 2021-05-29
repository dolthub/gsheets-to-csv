#!/bin/bash

set -eo pipefail

if [ -z "$1" ]; then
    echo "must supply sheets argument ./print-csv.sh '[{'id':'','start':'','end':'','name':''}]'"
    exit 1
fi

if [ -z "$TOKEN" ] || [ -z "$API_KEY" ] || [ -z "$CSV_DIR" ]; then
    echo "must supply TOKEN, API_KEY, and CSV_DIR"
    exit 1
fi

sheets="$1"

if [ "$( echo "$sheets" | jq 'if type=="array" then "true" else "false" end')" = "false" ]; then
    echo "Inputs: sheets must be a valid json array"
    exit 1
fi

_jq() {
  local row="$1"
  local field="$2"
  echo "$row" | base64 -d | jq -r "$field"
}

fromResponseCSV() {
  local res="$1"
  local rows=$(echo "$res" | jq -r '.values | .[0], .[1:][] | @csv')
  echo "$rows"
}

googleSheetToCSV() {
  local id="$1"
  local start="$2"
  local end="$3"

  local res=""
  res=$(
     curl -L \
    "https://sheets.googleapis.com/v4/spreadsheets/$id/values/$start%3A$end?key=$API_KEY" \
    --header "Authorization: Bearer $TOKEN" \
    --header "Accept: application/json" \
    --compressed)

  fromResponseCSV "$res"
}

row_cnt=0

for row in $(echo "${sheets}" | jq -r '.[] | @base64'); do
    id=$(_jq "$row" '.id')
    start=$(_jq "$row" '.start')
    end=$(_jq "$row" '.end')
    name=$(_jq "$row" '.name')

    if [ -z "${id}" ] || [ -z "${start}" ] || [ -z "${end}" ] || [ -z "${name}" ]; then
        row_cnt=$((row_cnt+1))
        continue
    fi
    if [ "$id" == "null" ] || [ "$start" == "null" ] || [ "$end" == "null" ] || [ "$name" == "null" ]; then
        row_cnt=$((row_cnt+1))
        continue
    fi

    tempfile="$CSV_DIR/$row_cnt.csv"

    googleSheetToCSV "$id" "$start" "$end" > "$tempfile"

    row_cnt=$((row_cnt+1))
done
