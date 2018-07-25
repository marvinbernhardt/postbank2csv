#!/usr/bin/env python3

import argparse
import csv
import subprocess
import tempfile

parser = argparse.ArgumentParser(description='Convert Postbank account statement pdf files to a single csv file.')
parser.add_argument('pdf_files', metavar='pdf_file', type=argparse.FileType('r'), nargs='+', help='pdf files to convert')
args = parser.parse_args()

def main():
    statements = []

    for file in args.pdf_files:
        print(file.name)
        statements += parse_statements_from_file(str(file.name))

    save_statements_as_csv(statements, "statements.csv")

def parse_statements_from_file(pdf_filename):
    txt_filename = next(tempfile._get_candidate_names()) + ".txt"

    bashCommand = f"pdftotext -layout -x 70 -y 100 -W 500 -H 700 {pdf_filename} {txt_filename}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    with open(txt_filename, 'r') as f:
        filecontent = f.read()

    in_statement_area = False
    in_statement = False
    last_line_token = []
    statements = []
    statement = {}

    for line in filecontent.splitlines():
        line_token = [token.strip() for token in line.split()]

        if line_token == ['Buchung/Wert', 'Vorgang/Buchungsinformation', 'Soll', 'Haben']:
            in_statement_area = True
            last_line_token = line_token
            continue

        if line_token == ['Auszug', 'Jahr', 'Seite', 'von', 'IBAN', 'Übertrag']:
            in_statement_area = False

        if line_token == ['Kontonummer', 'BLZ', 'Summe', 'Zahlungseingänge']:
            in_statement_area = False

        if in_statement_area:
            #print(line_token)
            if line_token and not last_line_token: # if non empty and last one was empty
                in_statement = True
                statement = {}
                statement_first_line = True

            if not line_token:
                in_statement = False
                if statement: # if dict not empty
                    statements.append(statement)
                    #print("new statement written", statement)
                    statement = {}

            if in_statement:
                if statement_first_line:
                    try:
                        statement['value'] = float(''.join(line_token[-2:]).replace('.', '').replace(',', '.'))
                    except ValueError:
                        in_statement = False
                        continue
                    statement['date1'] = line_token[0].split('/')[0][:-1]
                    statement['date2'] = line_token[0].split('/')[1][:-1]
                    print(statement['date1'], statement['date2'])
                    statement['type'] = ' '.join(line_token[1:-2])
                    statement['other'] = ""
                    statement_first_line = False
                else:
                    statement['other'] += ' '.join(line_token)
                    statement['other'] += ' '

        last_line_token = line_token

    bashCommand = f"rm {txt_filename}"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    return statements


def save_statements_as_csv(statements, csv_filename):

    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['date1', 'date2', 'type', 'value', 'other']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for statement in statements:
            writer.writerow(statement)


if __name__ == "__main__":
    main()
