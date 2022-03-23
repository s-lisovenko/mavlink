#! /usr/bin/env python3
""" Convert a parameters.json metadata file to a key-value json file """

import argparse
import sys
import json
import os


parser = argparse.ArgumentParser(description='Convert a parameters.json metadata file to a key-value json file')
parser.add_argument('json_file', help='JSON input file')
parser.add_argument('json_file_output', help='JSON output file')

args = parser.parse_args()
json_file = args.json_file
output_file = args.json_file_output

# load the json file
with open(json_file, 'r') as stream:
    metadata = json.load(stream)

parameters = metadata['parameters']
key_values = {}
all_categories = set()
all_groups = set()
for parameter in parameters:
    all_categories.add(parameter['category'])
    all_groups.add(parameter['group'])
    param_name = parameter['name']
    for value in parameter.get('values', []):
        key_values['param/'+param_name+'/values/'+str(value['value'])] = value['description']
    for bitmask in parameter.get('bitmask', []):
        key_values['param/'+param_name+'/bitmask/'+str(bitmask['index'])] = bitmask['description']
    key_values['param/'+param_name+'/shortDesc'] = parameter['shortDesc']
    if 'longDesc' in parameter:
        key_values['param/'+param_name+'/longDesc'] = parameter['longDesc']

for group in all_groups:
    key_values['group/'+group] = group
for category in all_categories:
    key_values['category/'+category] = category

# write output
with open(output_file, 'w') as stream:
    json.dump(key_values, stream, indent=2)

