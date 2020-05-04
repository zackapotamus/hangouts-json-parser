#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import re

NUMBER_REGEX = re.compile(r'[\d\+]')
PLUS_ONE_REGEX = re.compile(r'^\+?1')
global_dict = {}

def normalize_number(number_string):
    return PLUS_ONE_REGEX.sub("", "".join(NUMBER_REGEX.findall(number_string)))

with open('contacts.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        phone = row['Phone 1 - Value'].split(" ::: ")
        phone.extend(row['Phone 2 - Value'].split(' ::: '))
        phone.extend(row['Phone 3 - Value'].split(' ::: '))
        phone.extend(row['Phone 4 - Value'].split(' ::: '))
        output = {s for s in [normalize_number(x) for x in phone] if s}
        for number in output:
            global_dict[number] = row['Name']
print(global_dict)

        # phone1 = "".join(NUMBER_REGEX.findall(row['Phone 1 - Value']))
        # phone2 = "".join(NUMBER_REGEX.findall(row['Phone 2 - Value']))
        # phone3 = "".join(NUMBER_REGEX.findall(row['Phone 3 - Value']))
        # phone4 = "".join(NUMBER_REGEX.findall(row['Phone 4 - Value']))
        # print(phone1, phone2, phone3, phone4)