import argparse
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

import conversation_sizes_histogram
import largest_chats_all_time
import largest_chats_over_time
import utils

# TODO: eventually: make constants available as command line arguments
MESSAGE_FILE = 'message_{}.json'  # the name of the json file
MIN_MESSAGE_COUNT = 50               # minimum number of messages to do individual analysis

def main():
    args = parse_arguments()
    prepare_output_dirs()

    conversation_sizes_histogram.run(args.folder)
    largest_chats_all_time.run(args.folder)
    largest_chats_over_time.run(args.folder)

    # chats = utils.get_conversations(args.folder)

    # perform various analyses
    # conversation_stats_analyzer(args.folder, chats)
    # time_series_analyzer(args.folder, chats)

    print('Done')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help='root messages directory')
    args = parser.parse_args()

    if not args.folder:
        if os.path.isdir(os.path.join('messages', 'inbox')):
            args.folder = os.path.join('messages', 'inbox')
        else:
            print((
                'Error: must specify path to messages directory or have '
                'the messages/inbox directory in current directory'
            ))
            exit()
    return args


def prepare_output_dirs():
    """Prepares the output directory. If a directory with the same name already
    exists, warns the user before deleting it.
    """
    if os.path.isdir('output'):
        print((
            'Warning: existing output directory detected. Running this '
            'program will delete the existing directory. Continue? [Y/n]:'
        ), end=' ')
        user_input = input()
        if user_input != 'y' and user_input != 'Y' and user_input != '':
            print('Exiting program...')
            exit()
        shutil.rmtree('output')

# TODO: everything below this line must still be refactored

def conversation_stats_analyzer(folder, chats):
    """
    This function produces the following outputs:
    - output/data/individual/{conversation}/conversation_stats.tsv, a file
      containing react and count statistics for a given conversation, performed
      for all conversation found.
    - output/graphs/individual/{conversation}/react_stats.png, a bar graph of
      reacts received for each person in the conversation.
    
    folder: the path to the messages folder
    chats: a list of all conversation names
    """
    for chat in chats:
        try:
            react_map, msg_count_map, char_count_map, msg_count = ind.conversation_stats(os.path.join(folder, chat, utils.MESSAGE_FILE_NAME))
        except:
            continue
        
        if msg_count < MIN_MESSAGE_COUNT:
            continue
        os.makedirs(os.path.join('output', 'data', 'individual', chat))
        os.makedirs(os.path.join('output', 'graphs', 'individual', chat))
        with open(os.path.join('output', 'data', 'individual', chat, 'conversation_stats.tsv'), 'w') as f:
            f.write('\t'.join([
                'person', 'thumbs_up', 'thumbs_down', 'laughing', 'heart_eyes',
                'angry', 'cry', 'wow', 'msg_count', 'char_count',
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
                    person, str(thumbs_up), str(thumbs_down), str(laughing), str(heart_eyes),
                    str(angry), str(cry), str(wow), str(msg_count), str(char_count),
                ]) + '\n')

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


def time_series_analyzer(folder, chats):
    """This function produces the following outputs:
    - output/graphs/individual/{conversation}/message_activity_time_series.png, a
      time series of number of messages sent every (roughly) half-month.
    - output/graphs/individual/{conversation}/total_messages_over_time.png, a
      time series of total messages sent over time.
    
    folder: the path to the messages folder
    chats: a list of all conversation names
    """
    for chat in chats:
        try:
            times = ind.time_series(os.path.join(folder, chat, utils.MESSAGE_FILE_NAME))
            msg_count = len(times)
        except:
            continue
        
        if msg_count < MIN_MESSAGE_COUNT:
            continue
        if not os.path.exists(os.path.join('output', 'graphs', 'individual', chat)):
            os.makedirs(os.path.join('output', 'graphs', 'individual', chat))

        # skip the first few messages in case there are the 'messenger introduction' messages
        # that occur when people initially friend/connect with each other
        if len(times) >= 3:
            times = times[2:]
        first_time = times[0]
        last_time = times[-1]
        num_months = (int) ((last_time - first_time) / 2592000000 + 1)  # number of ms in 30 days
        y, bin_edges = np.histogram(times, bins=num_months * 2)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        timestamps = [datetime.utcfromtimestamp(time / 1000) for time in bin_centers]
        plt.figure(figsize=(14, 6.5))
        plt.plot(timestamps, y)
        plt.title('Messages over Time')
        plt.xlabel('Date')
        plt.ylabel('Messages per Interval (roughly half month)')
        plt.savefig(os.path.join('output', 'graphs', 'individual', chat, 'message_activity_time_series.png'), bbox_inches='tight')
        plt.close()

        accumulated = []
        total = 0
        for bin_count in y:
            total += bin_count
            accumulated.append(total)
        plt.figure(figsize=(14, 6.5))
        plt.plot(timestamps, accumulated)
        plt.title('Total Messages over Time')
        plt.xlabel('Date')
        plt.ylabel('Message Count')
        plt.savefig(os.path.join('output', 'graphs', 'individual', chat, 'total_messages_over_time.png'), bbox_inches='tight')
        plt.close()


def subcategorybar(X, vals, width=0.8):
    """Bar graph with multiple bars per categorical variable.
    From stack overflow.
    https://stackoverflow.com/questions/48157735/plot-multiple-bars-for-categorical-data
    """
    n = len(vals)
    _X = np.arange(len(X))
    for i in range(n):
        plt.bar(_X - width/2.0 + i/float(n)*width, vals[i], width=width/float(n), align='edge')   
    plt.xticks(_X, X)



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

if __name__ == '__main__':
    main()