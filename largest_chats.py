import json
import os
import collections
JSON_NAME = 'message_1.json'


def characterCount(data):
    messages = data["messages"]
    participants = data["participants"]
    charCounter = {}
    for message in messages:
        sender = message["sender_name"]
        defaultHeaders = {"sender_name", "timestamp_ms",
                          "type", "missed"}
        messageHeaders = set(list(message.keys()))
        remainingHeaders = messageHeaders.difference(defaultHeaders)
        for h in remainingHeaders:
            if (h == "call_duration"):
                counter = message[h]
            elif (h == "sticker"):
                counter = 1
            else:
                try:
                    counter = len(message[h])
                except TypeError:
                    counter = 1
                    print(message)

            if (not sender in charCounter):
                charCounter[sender] = collections.OrderedDict({"content": 0})
            if (not h in charCounter[sender]):
                charCounter[sender][h] = 0
            charCounter[sender][h] += counter

    data = charCounter
    try:
        data_sorted = [{k: v} for k, v in sorted(
            data.items(), key=lambda x: x[1]["content"], reverse=True)]
    except KeyError:
        data_sorted = data
    sortedDict = collections.OrderedDict()
    for item in data_sorted:
        for key in item:
            sortedDict[key] = item[key]
    return sortedDict


def largest_chats(root_dir):
    """
    Computes and returns a list containing all conversations sorted in
    decreasing order by message count. Also returns the total message
    count across all conversations.
    """
    total_msg_count = 0

    folders = os.listdir(root_dir)
    conversations = []
    for chat in folders:
        try:
            with open(os.path.join(root_dir, chat, JSON_NAME)) as f:
                data = json.load(f)
            count = len(data['messages'])
            total_msg_count += count
            if 'title' not in data:
                title = 'TITLE MISSING'
            else:
                title = data['title']
            charCount = characterCount(data)
            conversations.append({
                'title': title,
                'count': count,
                'chars': charCount
            })
        except IOError:
            print(chat)
            # ignore folders not corresponding to a conversation
            pass

    conversations.sort(key=lambda x: x['count'], reverse=True)
    return conversations, total_msg_count
