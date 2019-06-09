import json
import os
import collections
import datetime
JSON_NAME = 'message_1.json'
ENDTIME = datetime.datetime.max.timestamp()*1000


def characterCount(messages):
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
                charCounter[sender] = collections.OrderedDict({"messages": 0})
            if (not h in charCounter[sender]):
                charCounter[sender][h] = 0
            charCounter[sender][h] += counter
        charCounter[sender]["messages"] += 1

    data = charCounter
    try:
        data_sorted = [{k: v} for k, v in sorted(
            data.items(), key=lambda x: x[1]["messages"], reverse=True)]
    except KeyError:
        data_sorted = data
    sortedDict = collections.OrderedDict()
    for item in data_sorted:
        for key in item:
            sortedDict[key] = item[key]
    return sortedDict


def largest_chats(root_dir, startDate=None, endDate=None, minMessages=0):
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
            data_temp = []
            if (startDate is None and endDate is None):
                pass
            else:
                if (startDate is None):
                    startTime = -1
                else:
                    startTime = startDate.timestamp()*1000
                if (endDate is None):
                    endTime = ENDTIME
                else:
                    endTime = endDate.timestamp()*1000
                for message in data['messages']:
                    ts = message['timestamp_ms']
                    if (ts > startTime and ts < endTime):
                        data_temp.append(message)
                data['messages'] = data_temp

            count = len(data['messages'])
            if (count < minMessages):
                continue
            total_msg_count += count
            if 'title' not in data:
                title = 'TITLE MISSING'
            else:
                title = data['title']
            charCount = characterCount(data['messages'])
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
