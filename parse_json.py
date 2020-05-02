#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ijson
from termcolor import colored
from datetime import datetime

global_name_id_dict = {}
global_chat_name_dict = {}

def parse_json(json_filename):
    with open(json_filename, 'rb') as input_file:
        # load json iteratively
        parser = ijson.parse(input_file)
        for prefix, event, value in parser:
            # print('prefix={}, event={}, value={}'.format(colored(prefix, 'red'), colored(event, 'yellow'), colored(value, 'green')))
            print('prefix={}, event={}, value={}'.format(prefix, event, value))

def zack_function(json_filename):
    with open(json_filename, 'rb') as input_file:
        parser = ijson.parse(input_file)
        conversation_id = ''
        name_id_dict = {}
        chat_id = ''
        fallback_name = ''
        sender_id = ''
        for prefix, event, value in parser:
            if (prefix, event) == ('conversations.item.conversation,', 'start_map'):
                # print("Start of Conversation")
                name_id_dict = {}
                conversation_id = ''
                sender_id = ''
            elif (prefix, event) == ('onversations.item.conversation.conversation_id.id', 'string'):
                # print("conversation_id", value)
                conversation_id = value
            elif (prefix, event) == ('conversations.item.conversation.conversation.participant_data.item.id.chat_id', 'string'):
                # print("chat_id", value)
                chat_id = value
                name_id_dict[chat_id] = chat_id
            elif (prefix, event) == ('conversations.item.conversation.conversation.participant_data.item.fallback_name', 'string'):
                fallback_name = value
                name_id_dict[chat_id] = fallback_name
            if (prefix, event) == ('conversations.item.events.item.sender_id.chat_id', 'string'):
                sender_id = value
            elif (prefix, event) == ('conversations.item.events.item.chat_message.message_content.segment.item.text', 'string'):
                print('{}: {}'.format(global_name_id_dict[sender_id], value))
            elif (prefix, event) == ('conversations.item.events', 'end_array'):
                print('--------------------------------')

# def get_participants(json_filename):
#     with open(json_filename, 'rb') as input_file:
#         parser = ijson.parse(input_file)
#         if (prefix, event) == ('conversations.item.conversation,', 'start_map'):
#             # print("Start of Conversation")
#             name_id_dict = {}
#             chat_name_dict = {}
#             conversation_id = ''
#             sender_id = ''
#         elif (prefix, event) == ('onversations.item.conversation.conversation_id.id', 'string'):
#             # print("conversation_id", value)
#             conversation_id = value

#         for prefix, event, value in parser:
#             if (prefix, event) == ('conversations.item.conversation.conversation.participant_data.item.id.chat_id', 'string'):
#                 # print("chat_id", value)
#                 chat_id = value
#                 name_id_dict[chat_id] = chat_id
#                 chat_name_dict[chat_id] = name_id_dict
#                 global_name_id_dict[chat_id] = chat_id
#             elif (prefix, event) == ('conversations.item.conversation.conversation.participant_data.item.fallback_name', 'string'):
#                 # fallback_name = value
#                 name_id_dict[chat_id] = value
#                 global_name_id_dict[chat_id] = value
#             elif (prefix, event) == ('conversations.item.events', 'end_array'):
#                 global_chat_name_dict[chat_id] = "".join(name_id_dict.values())

#     print(global_name_id_dict)
#     zack_function(json_filename)

def get_participants(json_filename):
    with open(json_filename, 'rb') as input_file:
        parser = ijson.parse(input_file)
        conversation_id = ''
        name_id_dict = {}
        chat_id = ''
        fallback_name = ''
        sender_id = ''
        for prefix, event, value in parser:
            if (prefix, event) == ('conversations.item.conversation,', 'start_map'):
                # print("Start of Conversation")
                name_id_dict = {}
                conversation_id = ''
                sender_id = ''
            elif (prefix, event) == ('onversations.item.conversation.conversation_id.id', 'string'):
                # print("conversation_id", value)
                conversation_id = value
            elif (prefix, event) == ('conversations.item.conversation.conversation.participant_data.item.id.chat_id', 'string'):
                # print("chat_id", value)
                chat_id = value
                name_id_dict[chat_id] = chat_id
            elif (prefix, event) == ('conversations.item.conversation.conversation.participant_data.item.fallback_name', 'string'):
                fallback_name = value
                name_id_dict[chat_id] = fallback_name
            if (prefix, event) == ('conversations.item.events.item.sender_id.chat_id', 'string'):
                sender_id = value
            elif (prefix, event) == ('conversations.item.events.item.chat_message.message_content.segment.item.text', 'string'):
                print('{}: {}'.format(global_name_id_dict[sender_id], value))
            elif (prefix, event) == ('conversations.item.events', 'end_array'):
                print('--------------------------------')


if __name__ == '__main__':
    parse_json('./hangouts_json_test.json')
    # zack_function('./hangouts_json_test.json')
    # get_participants('./hangouts_json_test.json')
    # get_participants('/Users/zackhayden/Downloads/Takeout/Hangouts/Hangouts.json')
    # parse_json('/Users/zackhayden/Downloads/Takeout/Hangouts/Hangouts.json')
    # zack_function('/Users/zackhayden/Downloads/Takeout/Hangouts/Hangouts.json')

# I guess we'll loop twice -_-

# new conversation
## prefix=conversations.item.conversation, event=start_map, value=None

# participant data
## prefix=conversations.item.conversation.conversation.participant_data, event=start_array, value=None

# chat_id
## prefix=conversations.item.conversation.conversation.participant_data.item.id.chat_id, event=string, value=101951511583911246459

# name for chat_id
## prefix=conversations.item.conversation.conversation.participant_data.item.fallback_name, event=string, value=Chris Riley

# start of events
## prefix=conversations.item.events, event=start_array, value=None

# start of messages
## prefix=conversations.item.events, event=start_array, value=None

# sender id
## prefix=conversations.item.events.item.sender_id.chat_id, event=string, value=117550337082912090040

# message text
## prefix=conversations.item.events.item.chat_message.message_content.segment.item.text, event=string, value=blah