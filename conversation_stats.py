import json
import os

import matplotlib.pyplot as plt
import numpy as np

from largest_chats import JSON_EXT

import utils

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
                os.path.join(folderDir, chat, utils.JSON_NAME))
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
