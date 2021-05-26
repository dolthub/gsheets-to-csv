#!/bin/sh

set -eox pipefail

if [ "$( "$INPUT_SHEETS" | jq 'if type=="array" then "true" else "false" end')" = "false" ]; then
    echo "Inputs: sheets must be a valid json array"
    exit 1
fi

row_cnt=0
outputs=()

for row in $(echo "${INPUT_SHEETS}" | jq -r '.[] | @base64'); do
    _jq() {
      echo ${row} | base64 --decode | jq -r ${1}
    }

    id=$(_jq '.id')
    range=$(_jq '.range')
    name=$(_jq '.name')

    if [ -n "${id}" ] || [ -n "${range}" ] || [ -n "${name}" ]; then
        row_cnt=$((row_cnt+1))
        continue
    fi

    tempfile="${INPUT_TEMPDIR}/${row_cnt}.csv"

    curl \
        --data-urlencode "range=${name}!${range}" \
        --header "Accept: application/json" \
        'https://sheets.googleapis.com/v4/spreadsheets/1aaEoK1InHzEYjw6RNpuPvMoR-OKxYKXOjfhb1eE5Y_Y/values:get' \
        --compressed \
    | jq -r '.values | .[0], .[1:][] | @csv' \
    > "${tempfile}"
        #--data-urlencode "key=${INPUT_API_KEY}" \
        #--header "Authorization: Bearer ${INPUT_ACCESS_TOKEN}]" \

    row_cnt=$((row_cnt+1))
    outputs+=(tempfile)
done

echo "::set-output name=results::${outputs}"
