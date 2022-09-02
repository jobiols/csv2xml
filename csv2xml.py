"""Convert an OpenERP CSV data file to XML."""

import argparse
import lxml.etree as ET

#from unicode_csv import UnicodeReader

#from util import indent, sanitize_id

def sanitize_id(data):
    return data


parser = argparse.ArgumentParser(
    description=u"Convert an OpenERP CSV data file to XML"
)
parser.add_argument(
    u"-i",
    u"--input",
    required=True,
    help=u"CSV Input file",
)
parser.add_argument(
    u"-o",
    u"--output",
    required=True,
    help=u"XML Output file",
)
parser.add_argument(
    u"-m",
    u"--model",
    required=True,
    help=u"OSV Model",
)
parser.add_argument(
    u"--no-update",
    action='store_false',
    help=u"Add no_update attribute to the data node",
)
parser.add_argument(
    u"-s",
    u"--sanitize",
    action='store_false',
    help=u"Sanitize IDs",
)
parser.add_argument(
    u"-t",
    u"--trim",
    action='store_false',
    help=u"Trim data",
)
args = parser.parse_args()

template = ET.ElementTree(file='digital_signup/data/template.xml')
root_e = template.getroot()
data_e = root_e.find(u"data")

if not args.no_update:
    data_e.attrib[u"no_update"] = "1"

with open(args.input, 'r') as f:

    fields = []

    for line in f.readlines():

        # Assume the first line contains field names.
        line = line.strip().split(',')
        if not fields:
            if line[0] != u"id":
                raise Exception(
                    u"The first column of the CSV file must be the id."
                )
            fields = line
            continue

        record_id = line[0].encode('ascii', 'replace')
        if args.sanitize:
            record_id = sanitize_id(record_id)

        record_e = ET.SubElement(data_e, u"record", attrib={
            u"id": record_id,
            u"model": args.model
        })

        col_count = -1
        for col in line:
            col_count += 1
            if col_count == 0:
                continue  # Ignore the ID column.

            if args.trim:
                col = col.strip()

            field = fields[col_count]

            rel_field = field[-3:] == '/id'
            if rel_field:
                if not col:
                    continue
                field = field[:-3]

            field_e = ET.SubElement(record_e, 'field', attrib={
                'name': field
            })
            if rel_field:
                field_e.attrib['ref'] = col
            else:
                field_e.text = col
ET.indent(template)
template.write(args.output, encoding='utf-8', xml_declaration=True, pretty_print=True)
