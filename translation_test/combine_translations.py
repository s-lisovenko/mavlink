#! /usr/bin/env python3
""" Combine translations into single json file """

import argparse
import sys
import json
import os

parser = argparse.ArgumentParser(description='Combine translations into single json file')
parser.add_argument('input_dir', help='translation directory')
parser.add_argument('json_file_output', help='JSON output file')

args = parser.parse_args()
input_dir = args.input_dir
output_file = args.json_file_output

output = {}

for subdir, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith('.json'):
            json_file = os.path.join(subdir, file)
            language = os.path.basename(subdir)
            print('Adding '+json_file)

            # load the json file
            with open(json_file, 'r') as stream:
                translation = json.load(stream)
                output[language] = translation

# write output
with open(output_file, 'w') as stream:
    json.dump(output, stream, indent=2)

