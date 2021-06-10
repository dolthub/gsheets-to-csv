# Gsheets to CSV

This is a GitHub Action plugin that reads Google sheets into CSV
files.

## Example Usage

### Bash Array Result

```yml
name: GSheets Test

on:
  push:
env:
  id: '1ZbkUf1tAzt_Lhh1G8ezDgyU1AdUnm26xzPYLtdtWsI8'
  name: 'temp'
  range: 'A1:I8'

jobs:
  test_job:
    runs-on: ubuntu-latest
    name: A job to say hello
    steps:
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
        env:
          FILES: ${{ steps.sheet_to_csv.outputs.results }}
        run: |
          file_list=($FILES)
          for file in "${file_list[@]}"; do
              echo "$(wc -l $file)"
          done
```

This sample output from the "Print CSV" step is:

```bash
12 Test/tmp0.csv
13500 Test/tmp1.csv
```

### JSON Result

```yml
name: GSheets Test

on:
  push:
env:
  id: '1ZbkUf1tAzt_Lhh1G8ezDgyU1AdUnm26xzPYLtdtWsI8'
  name: 'temp'
  range: 'A1:I8'

jobs:
  test_job:
    runs-on: ubuntu-latest
    name: A job to say hello
    steps:
      - name: Pull GSheet data
        id: 'sheet_to_csv'
        uses: gsheets-to-csv@1
        with:
          creds: ${{ secrets.GSHEET_CREDENTIALS }}
          json_output: true
          sheets: |
            [
              { "id": "${{ env.id }}", "range": "${{ env.range }}", "title": "${{ env.name }}" },
              { "id": "${{ env.id }}" }
            ]
      - name: Print CSV
        id: "print_csv"
        env:
          FILES: ${{ steps.sheet_to_csv.outputs.results }}
        run: |
          echo "$FILES" | jq -c '.[]' | while read i; do
              eval file=$i
              echo "$(wc -l $file)"
          done
```

This sample output from the "Print CSV" step is:

```bash
12 Test/tmp0.csv
13500 Test/tmp1.csv
```

## Parameters

`sheets` is a valid JSON array with `id`, `title`, and `range`
parameters in each row. The `range` parameter is optional. If
`name` is omitted, a sheet's first tab will be downloaded.

The `creds` parameter is a json blob containing credentials
to authorize a Google API service account. The account must have
permissions to access the Google Sheets of interest. This parameter is
currently required.

By default, the results output will be a space-separated list of strings
that can be loaded into a list as follows:

```bash
file_list=(${{ steps.print_csv.outputs.result }})
for file in "${file_list[@]}"; do
    echo $file
done
```

Alternatively, `output_json=True` will output a JSON string encoding an
array of file names.

`tempfile` allows for overriding the target directory. If not using the
default, a subpath of `/github/workspace` is recommended to make sure
files persist between steps.

## File Persistence

How files are persisted between GitHub Action steps depends on whether
you indicate a `run` or `uses` step, and whether you checkout a GitHub directory
or not.

1. By default, your working directory is `/github/workspace`. This is
   true if you are using the default Docker container, or if you run a
   plugin/action with a `uses` block.

2. After you run `uses: actions/checkout@v2`, your working directory is
   now moved to the location of the GitHub repo, but nested action
   calls still mount that directory to `/github/workspace`.

To give a concrete example, the sheets plugin will default write files
to `/github/workspace`:

```bash
$ ls /github/workspace
tmp0.csv
tmp1.csv
```

If you have not checked out a GitHub directory, a generice `run` step
will still find files in `/github/workspace`.

If you have checked out a GitHub directory, `{{ github.workspace }}`
and our files will now reside in `/home/runner/work/gsheets-to-csv/gsheets-to-csv` during a
generic `run` step. Relative paths can be used to bridge this
discrepency. Containerized tasks will mount files back to
`/github/workspace` even after a GitHub checkout.
