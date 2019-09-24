import json
import os

import utils

"""
This file contains functions that compute statistics with respect to a
particular converstaion.
"""


def conversation_stats(messages_file):
    """
    Returns statistics related to reacts; 3 maps as well as the total message count.
    react_map:      person -> { react -> count }
    msg_count_map:  person -> message count
    char_count_map: person -> character count
    """
    with open(messages_file) as f:
        data = json.load(f)

    participants = data['participants']
    react_map = {}                      # person -> { react -> count }
    msg_count_map = {}                  # person -> message count
    char_count_map = {}                 # person -> character count
    msg_count = len(data['messages'])   # total number of messages

    # initialize maps
    for person in participants:
        react_map[person['name']] = dict()
        msg_count_map[person['name']] = 0
        char_count_map[person['name']] = 0

    for msg in data['messages']:
        sender = msg['sender_name']
        if sender not in react_map:
            # person left group
            continue

        # update reactions, if available
        if 'reactions' in msg:
            for react in msg['reactions']:
                if react['reaction'] not in react_map[sender]:
                    react_map[sender][react['reaction']] = 0
                react_map[sender][react['reaction']] += 1
        
        # update message count
        msg_count_map[sender] += 1

        # update character count if message is text
        if 'content' in msg:
            char_count_map[sender] += len(msg['content'])

    # rename the unicode reacts to understandable names
    for person in react_map:
        react_counts = react_map[person]
        newDict = dict()
        for unicodeKey in react_counts:
            newDict[utils.unicode_to_react(unicodeKey)] = react_counts[unicodeKey]
        react_counts.clear()
        react_counts.update(newDict)

    return react_map, msg_count_map, char_count_map, msg_count


def time_series(message_file):
    """
    Returns a list of all messages' timestamps in ascending order.
    messages_file: the message json file
    """
    with open(message_file) as f:
        data = json.load(f)

    times = [message['timestamp_ms'] for message in data['messages']]
    times.sort()
    return times
