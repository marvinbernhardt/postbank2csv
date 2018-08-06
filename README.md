# postbank2csv
Convert Postbank account statements to a csv file
Inspired by https://github.com/FlatheadV8/Postbank_PDF2CSV>

## Dependencies
python >= 3.6
pdftotext from poppler

## Input
Postbank account statement pdf files from July 2017 or later. Before the format was different.

## Output
On stdout, all statements, as they appeared in the pdf file(s).
The columns are:
date, type, amount, purpose

## Usage
postbank2csv.py [-h] pdf_file [pdf_file ...]
