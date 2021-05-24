from argparse import ArgumentParser
from csv import DictWriter, excel
from fnmatch import fnmatch
from logging import basicConfig, INFO, error, debug
from os import path, listdir
from docx import Document
from pyparsing import (Or, Word, alphas, OneOrMore,
                       Suppress, alphas8bit, nums, ParseException, restOfLine)


def main():
    basicConfig(format='%(asctime)s - %(levelname)s:%(message)s', level=INFO)

    parser = ArgumentParser(description='Transform unstructured data in docx '
                            'to formatted csv files.')
    parser.add_argument('-i', metavar='input folder', type=str, default='.',
                        help="Folder path with docx files")
    parser.add_argument('-o', metavar='output file', type=str,
                        default='output.csv',
                        help='CSV output path. Existing file will '
                        'be rewritten.')
    args = parser.parse_args()

    if not path.isdir(args.i):
        raise Exception('input path is not a folder')

    formatted_data = []
    for file in [x for x in listdir(args.i) if fnmatch(x, '*.docx')]:
        raw_data = read_docx(path.join(args.i, file))
        structured_data = parse_unstructured_data(raw_data)
        formatted_data.append(format_data(structured_data))
        break

    write_excel(formatted_data, args.o)


def read_docx(docx_path):
    return '\n'.join([x.text for x in Document(docx_path).paragraphs
                      if len(x.text.strip()) > 0])


def parse_unstructured_data(data):
    parser = Or([OneOrMore(Word(alphas + nums + alphas8bit + ' ')
                           .setResultsName('key')) +
                 Suppress(':') +
                 Or([Word(nums + '/').setResultsName('date'),
                     Word(alphas + nums + '.@-').setResultsName('email'),
                     Word(alphas + nums + ' :/.-').setResultsName('generic')]),
                 Word('CODE').setResultsName('ignored') + restOfLine,
                 Word(nums + ' ').setResultsName('2fa')])

    structured_data = {}
    structured_data['2fa'] = []

    for raw_row in [x for x in data.split('\n') if len(x.strip()) > 0]:
        debug(f'raw row:{raw_row}')

        try:
            parsed_row = parser.parseString(raw_row, True)
        except ParseException as ex:
            error(f'Não foi possível traduzir o valor "{raw_row}" '
                  f'pelo seguinte motivo: {ex}')
            continue

        debug(f'parsed_row:{parsed_row}')

        if 'ignored' in parsed_row:
            continue

        key = parsed_row['key'].lower().strip() \
            if 'key' in parsed_row else 'context'

        if 'date' in parsed_row:
            structured_data[key] = parsed_row['date']
        elif 'email' in parsed_row:
            structured_data[key] = parsed_row['email']
        elif 'generic' in parsed_row:
            structured_data[key] = parsed_row['generic'].strip()
        elif '2fa' in parsed_row:
            structured_data['2fa'].append(parsed_row['2fa'])

    debug(f'structured_data:{structured_data}')
    return structured_data


def format_data(data):
    formatted_data = {}

    formatted_data['login'] = data.get(
        next(iter([x for x in data.keys()
                   if 'email' in x]), None), None)
    formatted_data['senha fb'] = data.get(
        next(iter([x for x in data.keys()
                   if 'face' in x]), None), None)
    formatted_data['url'] = data.get(
        next(iter([x for x in data.keys()
                   if 'usuario' in x]), None), None)
    formatted_data['data de nascimento'] = data.get(
        next(iter([x for x in data.keys()
                   if 'data' in x]), None), None)
    formatted_data['link com códigos para recuperação'] = data.get(
        next(iter([x for x in data.keys()
                   if 'fator' in x]), None), None)
    formatted_data['senha email'] = data.get(
        next(iter([x for x in data.keys()
                   if 'senha' in x and 'email' in x]), None), None)

    debug(f'formatted_data:{formatted_data}')
    return formatted_data


def write_excel(data, output_path):
    if not data:
        return

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        output_writer = DictWriter(csvfile, data[0].keys(),
                                   delimiter=excel.delimiter,
                                   quotechar=excel.quotechar,
                                   quoting=excel.quoting)
        output_writer.writeheader()
        for row in data:
            output_writer.writerow(row)


if __name__ == '__main__':
    main()
