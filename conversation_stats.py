import json
import os

import matplotlib.pyplot as plt
import numpy as np

from largest_chats import JSON_EXT


def unicode_to_react(str):
    """
    Returns a string description of select unicode emoji characters.
    """
    if str == u'\xf0\x9f\x91\x8d':
        return 'Thumbs Up'
    if str == u'\xf0\x9f\x91\x8e':
        return 'Thumbs Down'
    if str == u'\xf0\x9f\x98\x86':
        return 'Laughing'
    if str == u'\xf0\x9f\x98\x8d':
        return 'Heart Eyes'
    if str == u'\xf0\x9f\x98\xa0':
        return 'Angry'
    if str == u'\xf0\x9f\x98\xa2':
        return 'Cry'
    if str == u'\xf0\x9f\x98\xae':
        return 'Wow'
    return 'ERROR'


def subcategorybar(X, vals, width=0.8):
    """
    Bar graph with multiple bars per categorical variable.
    From stack overflow.
    https://stackoverflow.com/questions/48157735/plot-multiple-bars-for-categorical-data
    """
    n = len(vals)
    _X = np.arange(len(X))
    for i in range(n):
        plt.bar(_X - width/2.0 + i/float(n)*width,
                vals[i], width=width/float(n), align="edge")
    plt.xticks(_X, X)


def conversationAnalyzer(chats, folderDir, MIN_MESSAGE_COUNT):
    ######################
    # conversation stats #
    ######################

    print(len(chats))

    for chat in chats:
        try:
            react_map, msg_count_map, char_count_map, msg_count = conversation_stats(
                os.path.join(folderDir, chat, JSON_EXT))
        except:
            continue

        if msg_count < MIN_MESSAGE_COUNT:
            continue
        os.makedirs(os.path.join('output', 'data', 'individual', chat))
        os.makedirs(os.path.join('output', 'graphs', 'individual', chat))
        with open(os.path.join('output', 'data', 'individual', chat, 'conversation_stats.tsv'), 'w') as f:
            f.write('\t'.join([
                'person',
                'thumbs_up',
                'thumbs_down',
                'laughing',
                'heart_eyes',
                'angry',
                'cry',
                'wow',
                'msg_count',
                'char_count',
            ]) + '\n')
            for person in react_map:
                thumbs_up = react_map[person].get('Thumbs Up', 0)
                thumbs_down = react_map[person].get('Thumbs Down', 0)
                laughing = react_map[person].get('Laughing', 0)
                heart_eyes = react_map[person].get('Heart Eyes', 0)
                angry = react_map[person].get('Angry', 0)
                cry = react_map[person].get('Cry', 0)
                wow = react_map[person].get('Wow', 0)
                msg_count = msg_count_map[person]
                char_count = char_count_map[person]
                f.write('\t'.join([
                    person,
                    str(thumbs_up),
                    str(thumbs_down),
                    str(laughing),
                    str(heart_eyes),
                    str(angry),
                    str(cry),
                    str(wow),
                    str(msg_count),
                    str(char_count),
                ]) + '\n')
        # make plot
        x = list(react_map.keys())
        thumbs_up = []
        thumbs_down = []
        laughing = []
        heart_eyes = []
        angry = []
        cry = []
        wow = []
        for _, person in enumerate(x):
            thumbs_up.append(react_map[person].get('Thumbs Up', 0))
            thumbs_down.append(react_map[person].get('Thumbs Down', 0))
            laughing.append(react_map[person].get('Laughing', 0))
            heart_eyes.append(react_map[person].get('Heart Eyes', 0))
            angry.append(react_map[person].get('Angry', 0))
            cry.append(react_map[person].get('Cry', 0))
            wow.append(react_map[person].get('Wow', 0))
        plt.figure(figsize=(14, 6.5))
        plt.title('Reacts Received')
        subcategorybar(x, [thumbs_up, thumbs_down, laughing,
                           heart_eyes, angry, cry, wow])
        plt.legend(['Thumbs Up', 'Thumbs Down', 'Laughing',
                    'Heart Eyes', 'Angry', 'Cry', 'Wow'])
        plt.savefig(os.path.join('output', 'graphs', 'individual',
                                 chat, 'react_stats.png'), bbox_inches='tight')
        plt.close()


def conversation_stats(MESSAGES_FILE):
    """
    Returns statistics related to reacts; 3 maps as well as the message count.
    """
    with open(MESSAGES_FILE) as f:
        data = json.load(f)

    # for each person:
    # absolute react count
    # message count
    # character count

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
            newDict[unicode_to_react(unicodeKey)] = react_counts[unicodeKey]
        react_counts.clear()
        react_counts.update(newDict)

    return react_map, msg_count_map, char_count_map, msg_count
