import argparse
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import pprint

from conversation_stats import get_possible_chats
from conversation_stats import conversation_stats
from conversation_time_series import get_time_series
from largest_chats import largest_chats

LARGEST_CHATS_TOP_N = 10    # in largest chats, the number of bars to display
MIN_MESSAGE_COUNT = 500      # minimum number of messages to do individual analysis

def main():
    """
    Excuse how ugly this function is. Aside from setup, different analysis is
    separated into different sections. Within each section, data is generated,
    saved, and also plots are saved.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help='root messages directory')
    args = parser.parse_args()

    if not args.folder:
        if os.path.isdir('messages'):
            args.folder = 'messages'
        else:
            print((
                'Error: must specify path to messages directory or have '
                'the messages directory in current directory'
            ))
            return

    # create output dirs, deleting old if exists
    if os.path.isdir('output'):
        shutil.rmtree('output')
    os.makedirs(os.path.join('output', 'data', 'aggregate'))
    os.makedirs(os.path.join('output', 'data', 'individual'))
    os.makedirs(os.path.join('output', 'graphs', 'aggregate'))
    os.makedirs(os.path.join('output', 'graphs', 'individual'))
    
    ##########################
    # largest chats analyzer #
    ##########################
    # plots:
    # - largest conversations bar graph
    # - conversation size frequency histogram
    print('finding largest chats')
    all_conversations, total_msg_count = largest_chats(args.folder)
    print('making graphs')
    with open(os.path.join('output', 'data', 'aggregate', 'top_chats.tsv'), 'w') as f:
        f.write('\t'.join(['title', 'count']) + '\n')
        for c in all_conversations:
            f.write('\t'.join([c['title'], str(c['count'])]) + '\n')
    x = [c['title'] for c in all_conversations[0:LARGEST_CHATS_TOP_N]]
    y = [c['count'] for c in all_conversations[0:LARGEST_CHATS_TOP_N]]
    plt.figure(figsize=(14, 6.5))
    plt.bar(x, y)
    plt.title('Top Chats by Message Count')
    plt.savefig(os.path.join('output', 'graphs', 'aggregate', 'top_chats.png'), bbox_inches='tight')
    plt.close()
    plt.figure(figsize=(14, 6.5))
    x = [c['count'] for c in all_conversations]
    plt.hist(x)
    plt.title('Conversation Size Histogram')
    plt.xlabel('Conversation Size')
    plt.ylabel('Number of Conversations')
    plt.savefig(os.path.join('output', 'graphs', 'aggregate', 'conversation_sizes.png'), bbox_inches='tight')
    plt.close()
    print('done aggregate')
    ######################
    # conversation stats #
    ######################
    
    chats = get_possible_chats(args.folder)
    '''
    for chat in chats:
        try:
            react_map, msg_count_map, char_count_map, msg_count = conversation_stats(os.path.join(args.folder, chat, 'message.json'))
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
        subcategorybar(x, [thumbs_up, thumbs_down, laughing, heart_eyes, angry, cry, wow])
        plt.legend(['Thumbs Up', 'Thumbs Down', 'Laughing', 'Heart Eyes', 'Angry', 'Cry', 'Wow'])
        plt.savefig(os.path.join('output', 'graphs', 'individual', chat, 'react_stats.png'), bbox_inches='tight')
        plt.close()
    '''
    ###############
    # time series #
    ###############
    print('time series')
    for chat in chats:
        try:
            times, msg_count = get_time_series(os.path.join(args.folder, chat, 'message.json'))
        except:
            continue
        
        if msg_count < MIN_MESSAGE_COUNT:
            continue
        if not os.path.exists(os.path.join('output', 'graphs', 'individual', chat)):
            os.makedirs(os.path.join('output', 'graphs', 'individual', chat))
        # TODO: any interesting data to store?

        # skip the first few 'messenger introduction' messages
        if len(times) >= 3:
            times = times[:-2]
        first_time = times[-1]
        last_time = times[0]
        num_months = (int) ((last_time - first_time) / 2592000000 + 1)     # number of ms in 30 days
        y, bin_edges = np.histogram(times, bins=num_months * 2)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        timestamps = [datetime.utcfromtimestamp(time / 1000) for time in bin_centers]
        plt.figure(figsize=(14, 6.5))
        plt.plot(timestamps, y)
        plt.title('Messages over Time')
        plt.xlabel('Date')
        plt.ylabel('Messages per Interval (roughly half month)')
        plt.savefig(os.path.join('output', 'graphs', 'individual', chat, 'conversation_time_series.png'), bbox_inches='tight')
        plt.close()


def subcategorybar(X, vals, width=0.8):
    """
    Bar graph with multiple bars per categorical variable.
    From stack overflow.
    https://stackoverflow.com/questions/48157735/plot-multiple-bars-for-categorical-data
    """
    n = len(vals)
    _X = np.arange(len(X))
    for i in range(n):
        plt.bar(_X - width/2.0 + i/float(n)*width, vals[i], width=width/float(n), align="edge")   
    plt.xticks(_X, X)


if __name__ == '__main__':
    main()