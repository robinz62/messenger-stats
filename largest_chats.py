import json
import os

import collections
import datetime
import matplotlib.pyplot as plt

JSON_NAME = 'message_1.json'
ENDTIME = datetime.datetime.max.timestamp()*1000


def chatToString(chat):
    s = chat['title'] + '\n'
    s += 'total messages: ' + str(chat['messages']) + '\n'
    s += 'total characters (content): ' + str(chat['characters']) + '\n'
    for person in chat['indData']:
        s += "----- " + person + ' ----- :\n'
        for stat in chat['indData'][person]:
            s += "'" + str(stat) + "':" + \
                str(chat['indData'][person][stat]) + '\n'
    s += '****************************************************\n'
    return s


def writeDatafile(all_conversations, MIN_MESSAGE_COUNT, startDate, endDate):
    with open(os.path.join('output', 'data', 'aggregate', 'top_chats.tsv'), 'w') as f:
        f.write("All messaging data with messages over " + str(MIN_MESSAGE_COUNT) +
                " messages.\n")
        f.write("Messages from " + str(startDate) +
                " until " + str(endDate) + "\n")
        f.write("______________________________________________________________\n")
        for c in all_conversations:
            f.write(chatToString(c) + '\n')


def plotMessages(all_conversations, startDate, endDate, sortby="messages", LARGEST_CHATS_TOP_N=10):
    print('making top conversation graph')

    x = [c['title'] for c in all_conversations[0:LARGEST_CHATS_TOP_N]]
    y = [c[sortby] for c in all_conversations[0:LARGEST_CHATS_TOP_N]]
    plt.figure(figsize=(14, 6.5))
    plt.bar(x, y)
    plt.title('Top Chats by number of ' + sortby + ' from ' +
              str(startDate) + ' until ' + str(endDate))
    plt.xlabel("Chat name")
    plt.ylabel("Number of " + sortby + " in chat messages")
    plt.savefig(os.path.join('output', 'graphs', 'aggregate',
                             'top_chats.png'), bbox_inches='tight')

    plt.close()


def plotHistogram(all_conversations, sortby="messages"):
    plt.figure(figsize=(14, 6.5))
    x = [c[sortby] for c in all_conversations]
    plt.hist(x)
    plt.title('Conversation Size Histogram')
    plt.xlabel('Conversation Size (number of ' + sortby + ')')
    plt.ylabel('Number of Conversations')
    plt.savefig(os.path.join('output', 'graphs', 'aggregate',
                             'conversation_sizes.png'), bbox_inches='tight')
    plt.close()


def largestChatAnalyzer(folderDir, MIN_MESSAGE_COUNT, startDate=None, endDate=None, sortby="messages"):
       ##########################
    # largest chats analyzer #
    ##########################
    # plots:
    # - largest conversations bar graph
    # - conversation size frequency histogram
    print('finding largest chats')
    all_conversations, total_msg_count = largest_chats(
        folderDir, startDate=startDate, endDate=endDate, minMessages=MIN_MESSAGE_COUNT)

    all_conversations.sort(key=lambda x: x[sortby], reverse=True)
    writeDatafile(all_conversations, MIN_MESSAGE_COUNT, startDate, endDate)
    plotMessages(all_conversations, startDate, endDate, sortby=sortby)
    plotHistogram(all_conversations, sortby=sortby)
    print('done aggregate')
    return


def characterCount(messages):
    indData = {}
    totalChars = 0
    for message in messages:
        sender = message["sender_name"]
        defaultHeaders = {"sender_name", "sender_id_INTERNAL", "timestamp_ms",
                          "type", "missed"}
        messageHeaders = set(list(message.keys()))
        remainingHeaders = messageHeaders.difference(defaultHeaders)
        for h in remainingHeaders:
            if (h == "content"):
                totalChars += len(message[h])
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

            if (not sender in indData):
                indData[sender] = collections.OrderedDict({"messages": 0})
            if (not h in indData[sender]):
                indData[sender][h] = 0
            indData[sender][h] += counter
        indData[sender]["messages"] += 1

    data = indData
    try:
        data_sorted = [{k: v} for k, v in sorted(
            data.items(), key=lambda x: x[1]["messages"], reverse=True)]
    except KeyError:
        data_sorted = data
    sortedDict = collections.OrderedDict()
    for item in data_sorted:
        for key in item:
            sortedDict[key] = item[key]
    return sortedDict, totalChars


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
            charCount, totalChars = characterCount(data['messages'])
            conversations.append({
                'title': title,
                'messages': count,
                'characters': totalChars,
                'indData': charCount
            })
        except IOError:
            print(chat)
            # ignore folders not corresponding to a conversation
            pass
    return conversations, total_msg_count
