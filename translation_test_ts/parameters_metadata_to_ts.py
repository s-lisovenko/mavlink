#! /usr/bin/env python3
""" Convert a parameters.json metadata file to a translation file """

import argparse
import sys
import json
import os
import codecs
from xml.sax.saxutils import escape


parser = argparse.ArgumentParser(description='Convert a parameters.json metadata file to a translation file')
parser.add_argument('json_file', help='JSON input file')
parser.add_argument('file_output', help='.ts output file')

args = parser.parse_args()
json_file = args.json_file
output_file = args.file_output

# load the json file
with open(json_file, 'r') as stream:
    metadata = json.load(stream)

translation = metadata['translation']

def process_items(prefix, translation, json_data, global_translations):
    """ processes an 'items' entry
        :return: list of (context, source string) tuples
    """
    ret = []

    def process_translation(prefix, translation, json_data, global_translations):
        """ processes an entry that potentially contans a 'translate' """
        ret = []
        if 'translate' in translation:
            for translate_name in translation['translate']:
                if translate_name in json_data:
                    ret.append((prefix+'/'+translate_name, json_data[translate_name]))
        if 'translate-global' in translation:
            for translate_name in translation['translate-global']:
                if translate_name in json_data:
                    if translate_name not in global_translations:
                        global_translations[translate_name] = set()
                    # globals will turn into '_globals/$translate_name/$json_data[translate_name]'
                    global_translations[translate_name].add(json_data[translate_name])
        if 'items' in translation:
            ret.extend(process_items(prefix, translation['items'], json_data, global_translations))
        return ret

    for translation_item in translation:
        if translation_item == '*':
            translation_keys = json_data.keys()
        else:
            translation_keys = [translation_item]
        for json_item in translation_keys:
            next_prefix = prefix+'/'+json_item
            next_translation = translation[translation_item]
            if json_item in json_data:
                next_json_data = json_data[json_item]
                if 'list' in next_translation:
                    translation_list = next_translation['list']
                    key = translation_list.get('key', None)
                    all_values = set()
                    for idx, list_entry in enumerate(next_json_data):
                        if key is not None and key in list_entry:
                            value = str(list_entry[key])
                        else:
                            value = str(idx)
                        ret.extend(process_translation(next_prefix+'/'+value, translation_list, list_entry, global_translations))
                        # ensure value is unique
                        assert value not in all_values, "Key {:} is not unique".format(value)
                        all_values.add(value)
                else:
                    ret.extend(process_translation(next_prefix, next_translation, next_json_data, global_translations))
    return ret


tuples = []
global_translations = {}
if 'items' in translation:
    tuples = process_items('', translation['items'], metadata, global_translations)

# write the .ts file
ts_file = codecs.open(output_file, 'w', "utf-8")
ts_file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
ts_file.write("<!DOCTYPE TS>\n")
ts_file.write("<TS version=\"2.1\">\n")
for context, string in tuples:
    ts_file.write("<context>\n")
    ts_file.write("  <name>{:}</name>\n".format(escape(context)))
    ts_file.write("  <message>\n")
    ts_file.write("  <source>{:}</source>\n".format(escape(string)))
    ts_file.write("  </message>\n")
    ts_file.write("</context>\n")

for global_translation in global_translations:
    for string in global_translations[global_translation]:
        ts_file.write("<context>\n")
        ts_file.write("  <name>{:}</name>\n".format('_globals/'+escape(global_translation)+'/'+escape(string)))
        ts_file.write("  <message>\n")
        ts_file.write("  <source>{:}</source>\n".format(escape(string)))
        ts_file.write("  </message>\n")
        ts_file.write("</context>\n")
ts_file.write("</TS>\n")
ts_file.close()

