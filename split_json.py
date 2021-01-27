#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ijson
import simplejson as json

def split_json(json_filename):
    file_count = 0
    with open(json_filename, 'rb') as input_file:
        objects = ijson.items(input_file, 'conversations.item')
        for obj in objects:
            file_count = file_count + 1
            with open('./outfiles/convo{}.json'.format(file_count), 'w') as out_file:
                json.dump(obj, out_file, indent=2)

if __name__ == '__main__':
    split_json("/Users/zackhayden/Downloads/Takeout 2/Hangouts/Hangouts.json")