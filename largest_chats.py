import json
import os

import collections
import datetime
import matplotlib.pyplot as plt

JSON_EXT = '.json'
ENDTIME = datetime.datetime.max.timestamp()*1000

def get_json_files(folder_path):
    files = os.listdir(folder_path)
    json_files = []
    for f in files:
        if(f.endswith(JSON_EXT)):
            json_files.append(f)
    return json_files

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


def writeDatafile(all_conversations, MIN_MESSAGE_COUNT, startDate, endDate, outputDir="./", sortby="messages"):
    with open(os.path.join(outputDir, sortby + '_top_chats.tsv'), 'w') as f:
        f.write("All messaging data with messages over " + str(MIN_MESSAGE_COUNT) +
                " messages.\n")
        f.write("Messages from " + str(startDate) +
                " until " + str(endDate) + "\n")
        f.write("______________________________________________________________\n")
        for c in all_conversations:
            f.write(chatToString(c) + '\n')


def plotMessages(all_conversations, startDate, endDate, sortby="messages", LARGEST_CHATS_TOP_N=10, outputDir="./"):
    print('making top conversation graph')
    print(LARGEST_CHATS_TOP_N)
    x = [c['title'] for c in all_conversations[0:LARGEST_CHATS_TOP_N]]
    y = [c[sortby] for c in all_conversations[0:LARGEST_CHATS_TOP_N]]
    plt.figure(figsize=(14, 6.5))
    plt.bar(x, y)
    plt.title('Top Chats by number of ' + sortby + ' from ' +
              str(startDate) + ' until ' + str(endDate))
    plt.xlabel("Chat name")
    plt.ylabel("Number of " + sortby + " in chat messages")
    
    plt.savefig(os.path.join(outputDir, sortby +
                             '_top_chats.png'), bbox_inches='tight')
    plt.show()
    plt.close()


def plotHistogram(all_conversations, sortby="messages", outputDir="./"):
    plt.figure(figsize=(14, 6.5))
    x = [c[sortby] for c in all_conversations]
    plt.hist(x)
    plt.title('Conversation Size Histogram')
    plt.xlabel('Conversation Size (number of ' + sortby + ')')
    plt.ylabel('Number of Conversations')
    plt.savefig(os.path.join(outputDir, sortby + '_conversation_sizes.png'),
                bbox_inches='tight')
    plt.close()

def get_message_content_size(message, defaultHeaders):
    pass

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
                    #print(message)

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

def sift_timestamps(data, startDate, endDate):
    data_temp = []
    if (startDate is None):
        startTime = -1
    else:
        startTime = startDate.timestamp()*1000
    if (endDate is None):
        endTime = ENDTIME
    else:
        endTime = endDate.timestamp() * 1000
    # filter out messages outside of timestamp
    for message in data['messages']:
        ts = message['timestamp_ms']
        if (ts > startTime and ts < endTime):
            data_temp.append(message)
    return data_temp

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
            chat_path = os.path.join(root_dir, chat)
            json_files = get_json_files(chat_path)
            data = {}
            for json_name in json_files:
                with open(os.path.join(root_dir, chat, json_name)) as f:
                    partial_data = json.load(f)
                    if len(data) == 0:
                        data = partial_data 
                    else:
                        data['messages'].extend(partial_data['messages'])
            
            if (startDate is None and endDate is None):
                pass
            else:
                data['messages'] = sift_timestamps(data, startDate, endDate)

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
            print("File not found:" + chat)
            # ignore folders not corresponding to a conversation
            pass
    return conversations, total_msg_count


def largestChatAnalyzer(folderDir, MIN_MESSAGE_COUNT, startDate=None, endDate=None, sortby="messages", outputDir="./aggregate", topn=10):
       ##########################
    # largest chats analyzer #
    ##########################
    # plots:
    # - largest conversations bar graph
    # - conversation size frequency histogram

    print('finding largest chats')
    all_conversations, total_msg_count = largest_chats(
        folderDir, startDate=startDate, endDate=endDate, minMessages=MIN_MESSAGE_COUNT)

    if (sortby == "both"):
        sortbys = ["characters", "messages"]
        for sortby in sortbys:
            all_conversations.sort(key=lambda x: x[sortby], reverse=True)
            writeDatafile(all_conversations, MIN_MESSAGE_COUNT,
                          startDate, endDate, outputDir=outputDir, sortby=sortby)
            plotMessages(all_conversations, startDate, endDate,
                         sortby=sortby, outputDir=outputDir, LARGEST_CHATS_TOP_N=topn)
            plotHistogram(all_conversations, sortby=sortby,
                          outputDir=outputDir)
    else:
        all_conversations.sort(key=lambda x: x[sortby], reverse=True)
     
        writeDatafile(all_conversations, MIN_MESSAGE_COUNT,
                      startDate, endDate, outputDir=outputDir)
        plotMessages(all_conversations, startDate, endDate,
                     sortby=sortby, outputDir=outputDir, LARGEST_CHATS_TOP_N=topn)
        plotHistogram(all_conversations, sortby=sortby, outputDir=outputDir)
    print('done aggregate')
    return
