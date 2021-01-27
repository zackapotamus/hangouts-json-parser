#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ijson
from termcolor import colored
from datetime import datetime
import os
import sys
import csv
import re
import pycurl
from urllib.parse import urlparse
import magic

NUMBER_REGEX = re.compile(r"[\d\+]")
PLUS_ONE_REGEX = re.compile(r"^\+?1")
FILENAME_REGEX = re.compile(r'[\+\*\?%/\\]')


def normalize_number(number_string):
    return PLUS_ONE_REGEX.sub("", "".join(NUMBER_REGEX.findall(number_string)))


participant_dict = {}

with open("contacts.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        phone = row["Phone 1 - Value"].split(" ::: ")
        phone.extend(row["Phone 2 - Value"].split(" ::: "))
        phone.extend(row["Phone 3 - Value"].split(" ::: "))
        phone.extend(row["Phone 4 - Value"].split(" ::: "))
        output = {s for s in [normalize_number(x) for x in phone] if s}
        for number in output:
            participant_dict[number] = row["Name"]


global_name_id_dict = {}
global_chat_name_dict = {}

def extension_from_mime(mime_type):
    if mime_type == "image/png":
        return ".png"
    elif mime_type == "image/jpeg":
        return ".jpg"
    elif mime_type == "image/gif":
        return ".gif"
    elif mime_type == "video/quicktime":
        return ".mov"
    elif mime_type == "video/3gpp":
        return ".3gp"
    elif "/" in mime_type:
        return '.{}'.format(mime_type[mime_type.find('/')+1:])
    return ""

def parse_json(json_filename):
    with open(json_filename, "rb") as input_file:
        # load json iteratively
        parser = ijson.parse(input_file)
        for prefix, event, value in parser:
            # print('prefix={}, event={}, value={}'.format(colored(prefix, 'red'), colored(event, 'yellow'), colored(value, 'green')))
            print("prefix={}, event={}, value={}".format(prefix, event, value))


def write_to_file(timestamp_dt, sender_id, conversation_id, message_type, message):
    conversation_name = global_chat_name_dict[conversation_id]
    sender_name = participant_dict.get(
        normalize_number(global_name_id_dict[sender_id]), global_name_id_dict[sender_id]
    )
    if message_type == "text":
        out_file = "{}.txt".format(conversation_id)
        timestamp_display = timestamp_dt.strftime("%a %b %d, %Y %I:%M:%S %p")
        # build path
        path_part = os.path.join("./output", conversation_name)
        file_path = os.path.join(path_part, out_file)
        if not os.path.exists(path_part):
            os.makedirs(path_part)
        with open(file_path, "a") as file:
            file.write("[{}] {}: {}\n".format(timestamp_display, sender_name, message))
    elif message_type == "attachment":
        timestamp_display = timestamp_dt.strftime("%Y-%m-%d-%H-%M-%S.%f")
        new_file_name = ''
        o = urlparse(message)
        original_file_name = os.path.basename(o.path)
        if '.' not in original_file_name:
            if '%' in original_file_name:
                new_file_name = original_file_name[0:original_file_name.find('%')]
            else:
                new_file_name = original_file_name
        else:
            new_file_name = original_file_name[0:original_file_name.find('.')]
        new_file_name = FILENAME_REGEX.sub('', '{}__{}_{}'.format(sender_name.replace(" ", "_"), timestamp_display, new_file_name))
        # build path
        path_part = os.path.join("./output", conversation_name, "images")
        file_path = os.path.join(path_part, new_file_name)
        # print('{}  {}'.format(file_path, message))
        if not os.path.exists(path_part):
            os.makedirs(path_part)
        with open(file_path, 'wb') as out_file:
            c = pycurl.Curl()
            c.setopt(c.URL, message)
            c.setopt(c.WRITEDATA, out_file)
            c.perform()
            c.close()
        mime_type = magic.from_file(file_path, mime=True)
        extension = extension_from_mime(mime_type)
        os.rename(file_path, '{}{}'.format(file_path, extension))
        



def zack_function(json_filename):
    with open(json_filename, "rb") as input_file:
        parser = ijson.parse(input_file)
        conversation_id = ""
        name_id_dict = {}
        gaia_id = ""
        fallback_name = ""
        sender_id = ""
        timestamp_display = ""
        timestamp = None
        for prefix, event, value in parser:
            if (prefix, event) == ("conversations.item.conversation", "start_map"):
                # print("Start of Conversation")
                name_id_dict = {}
                conversation_id = ""
                sender_id = ""
            elif (prefix, event) == (
                "conversations.item.conversation.conversation_id.id",
                "string",
            ):
                # print("conversation_id", value)
                conversation_id = value
                print(global_chat_name_dict[conversation_id])
            elif (prefix, event) == (
                "conversations.item.conversation.conversation.participant_data.item.id.gaia_id",
                "string",
            ):
                # print("gaia_id", value)
                gaia_id = value
                name_id_dict[gaia_id] = gaia_id
            elif (prefix, event) == (
                "conversations.item.conversation.conversation.participant_data.item.fallback_name",
                "string",
            ):
                fallback_name = value
                name_id_dict[gaia_id] = fallback_name
            elif (prefix, event) == (
                "conversations.item.events.item.sender_id.gaia_id",
                "string",
            ):
                sender_id = value
            elif (prefix, event) == (
                "conversations.item.events.item.timestamp",
                "string",
            ):
                timestamp = datetime.fromtimestamp(int(value) / 1000000)
                timestamp_display = timestamp.strftime("%Y-%m-%d %-I:%M:%S %p")
            elif (prefix, event) == (
                "conversations.item.events.item.chat_message.message_content.segment.item.text",
                "string",
            ):
                the_sender = participant_dict.get(
                    normalize_number(global_name_id_dict[sender_id]),
                    global_name_id_dict[sender_id],
                )
                # print("{}@{}>{}: {}".format(global_chat_name_dict[conversation_id], timestamp_display, the_sender, value))
                write_to_file(
                    timestamp, sender_id, conversation_id, "text", value
                )
            elif (prefix, event) == (
                "conversations.item.events.item.chat_message.message_content.attachment.item.embed_item.plus_photo.url",
                "string",
            ):
                the_sender = participant_dict.get(
                    normalize_number(global_name_id_dict[sender_id]),
                    global_name_id_dict[sender_id],
                )
                # print("{}@{}>{}: {}".format(global_chat_name_dict[conversation_id], timestamp_display, the_sender, value))
                write_to_file(
                    timestamp, sender_id, conversation_id, "attachment", value
                )
            elif (prefix, event) == ("conversations.item.events", "end_array"):
                print("--------------------------------")


def get_participants(json_filename):
    with open(json_filename, "rb") as input_file:
        parser = ijson.parse(input_file)
        conversation_id = ""
        name_id_dict = {}
        gaia_id = ""
        fallback_name = ""  # this might blow up
        for prefix, event, value in parser:
            if (prefix, event) == ("conversations.item.conversation", "start_map"):
                # print("Start of Conversation******************************************************")
                name_id_dict = {}
                conversation_id = ""
            elif (prefix, event) == (
                "conversations.item.conversation.conversation_id.id",
                "string",
            ):
                # print("conversation_id", value)
                conversation_id = value
            elif (prefix, event) == (
                "conversations.item.conversation.conversation.participant_data.item.id.gaia_id",
                "string",
            ):
                # print("gaia_id", value)
                gaia_id = value
                name_id_dict[gaia_id] = gaia_id
                global_name_id_dict[gaia_id] = gaia_id
            elif (prefix, event) == (
                "conversations.item.conversation.conversation.participant_data.item.fallback_name",
                "string",
            ):
                fallback_name = value
                name_id_dict[gaia_id] = fallback_name
                global_name_id_dict[gaia_id] = fallback_name
            # elif (prefix, event) == ('conversations.item.events.item.chat_message.message_content.segment.item.text', 'string'):
            #     print('{}: {}'.format(global_name_id_dict[sender_id], value))
            elif (prefix, event) == ("conversations.item.events", "end_array"):
                participant_list = [
                    participant_dict.get(normalize_number(x), x)
                    for x in name_id_dict.values()
                ]
                if "Zack Hayden" in participant_list:
                    participant_list.remove("Zack Hayden")
                # participant_list.remove("Zack Hayden")
                global_chat_name_dict[conversation_id] = "__".join(
                    participant_list
                ).replace(" ", "-")
                # print(global_chat_name_dict[c onversation_id])
                # print(conversation_id)
                print(".", end="", flush=True)
    # print(global_name_id_dict.values())
    zack_function(json_filename)


if __name__ == "__main__":
    # parse_json('./hangouts_json_test.json')
    # zack_function('./hangouts_json_test.json')
    # get_participants('./hangouts_json_test.json')
    # get_participants("/Users/zackhayden/Downloads/Takeout 2/Hangouts/Hangouts.json")
    parse_json("/Users/zackhayden/Downloads/Takeout/Hangouts/Hangouts.json")
    # zack_function('/Users/zackhayden/Downloads/Takeout/Hangouts/Hangouts.json')

# I guess we'll loop twice -_-

# new conversation
## prefix=conversations.item.conversation, event=start_map, value=None

# participant data
## prefix=conversations.item.conversation.conversation.participant_data, event=start_array, value=None

# gaia_id
## prefix=conversations.item.conversation.conversation.participant_data.item.id.gaia_id, event=string, value=101951511583911246459

# name for gaia_id
## prefix=conversations.item.conversation.conversation.participant_data.item.fallback_name, event=string, value=Chris Riley

# start of events
## prefix=conversations.item.events, event=start_array, value=None

# timestamp
## prefix=conversations.item.events.item.timestamp, event=string, value=1371575798553784

# start of messages
## prefix=conversations.item.events, event=start_array, value=None

# sender id
## prefix=conversations.item.events.item.sender_id.gaia_id, event=string, value=117550337082912090040

# message text
## prefix=conversations.item.events.item.chat_message.message_content.segment.item.text, event=string, value=blah
