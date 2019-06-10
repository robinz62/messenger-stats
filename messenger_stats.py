
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
from largest_chats import JSON_NAME
TIME_INTERVAL = 14          # number of days for time interval analysis
MICROSECONDS_PER_DAY = 86400000


def chatToString(chat):
    s = chat['title'] + '\n'
    s += 'total messages: ' + str(chat['count']) + '\n'
    s += 'total characters: ' + str(chat['chars']) + '\n'
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
        f.write("NOTE: 'content' refers to number of characters\n")
        f.write("______________________________________________________________\n")
        for c in all_conversations:
            f.write(chatToString(c) + '\n')


def plotMessages(all_conversations, startDate, endDate, sortby="count", LARGEST_CHATS_TOP_N=10):
    print('making top conversation graph')

    x = [c['title'] for c in all_conversations[0:LARGEST_CHATS_TOP_N]]
    y = [c[sortby] for c in all_conversations[0:LARGEST_CHATS_TOP_N]]
    plt.figure(figsize=(14, 6.5))
    plt.bar(x, y)
    plt.title('Top Chats by Message ' + sortby + ' from ' +
              str(startDate) + ' until ' + str(endDate))
    plt.xlabel("Chat name")
    plt.ylabel("Number of " + sortby + " of messages")
    plt.savefig(os.path.join('output', 'graphs', 'aggregate',
                             'top_chats.png'), bbox_inches='tight')

    plt.close()


def plotHistogram(all_conversations, sortby="count"):
    plt.figure(figsize=(14, 6.5))
    x = [c[sortby] for c in all_conversations]
    plt.hist(x)
    plt.title('Conversation Size Histogram')
    plt.xlabel('Conversation Size (number of ' + sortby + ')')
    plt.ylabel('Number of Conversations')
    plt.savefig(os.path.join('output', 'graphs', 'aggregate',
                             'conversation_sizes.png'), bbox_inches='tight')
    plt.close()


def largestChatAnalyzer(folderDir, MIN_MESSAGE_COUNT, startDate=None, endDate=None, sortby="count"):
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


def conversationAnalyzer(chats, folderDir, MIN_MESSAGE_COUNT):
    ######################
    # conversation stats #
    ######################

    print(len(chats))

    for chat in chats:
        try:
            react_map, msg_count_map, char_count_map, msg_count = conversation_stats(
                os.path.join(folderDir, chat, 'message.json'))
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
                freeusfromthisworld2
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


def timeSeriesAnalyzer(chats, folderDir, MIN_MESSAGE_COUNT, startDate=None, endDate=None):
    ###############
    # time series #
    ###############

    print('time series')
    for chat in chats:
        try:
            times, msg_count = get_time_series(
                os.path.join(folderDir, chat, JSON_NAME))
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
        num_months = int((last_time - first_time) /
                         (TIME_INTERVAL*MICROSECONDS_PER_DAY)) + 1
        y, bin_edges = np.histogram(times, bins=num_months)
        bin_centers = (bin_edges[:-1] + bin_edges[1:])/2.0
        timestamps = [datetime.utcfromtimestamp(
            time / 1000) for time in bin_centers]
        plt.figure(figsize=(14, 6.5))
        plt.plot(timestamps, y)
        plt.title('Messages over Time')
        plt.xlabel('Date')
        plt.ylabel('Messages per Interval (every ' +
                   str(TIME_INTERVAL) + ' days)')
        plt.savefig(os.path.join('output', 'graphs', 'individual',
                                 chat, 'conversation_time_series.png'), bbox_inches='tight')
        plt.close()


def setupDirTree(folderDir):
    if not folderDir:
        if os.path.isdir('messages/inbox'):
            folderDir = 'messages/inbox'
        else:
            print((
                'Error: must specify path to messages directory or have '
                'the messages/inbox directory in current directory'
            ))
            return

    # create output dirs, deleting old if exists
    if os.path.isdir('output'):
        shutil.rmtree('output')
    os.makedirs(os.path.join('output', 'data', 'aggregate'))
    os.makedirs(os.path.join('output', 'data', 'individual'))
    os.makedirs(os.path.join('output', 'graphs', 'aggregate'))
    os.makedirs(os.path.join('output', 'graphs', 'individual'))
    return folderDir


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


def main():
    """
    Excuse how ugly this function is. Aside from setup, different analysis is
    separated into different sections. Within each section, data is generated,
    saved, and also plots are saved.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help='root messages directory')
    parser.add_argument('-d', '--startDate',
                        help='earliest message from this date (YYYY-MM-DD)')
    parser.add_argument('-e', '--endDate',
                        help='last message up to this date (YYYY-MM-DD)')
    parser.add_argument(
        '-m', '--minSize', help="size of smallest chat you wish to include", type=int, default=500)
    parser.add_argument(
        '-s', '--sortby', help="by what to sort the largest chats (count, chars)", default="count")
    args = parser.parse_args()
    MIN_MESSAGE_COUNT = args.minSize
    startDate = None
    if (args.startDate):
        startDate = datetime.strptime(args.startDate, "%Y-%m-%d")
    endDate = None
    if (args.endDate):
        endDate = datetime.strptime(args.endDate, "%Y-%m-%d")
    folderDir = setupDirTree(args.folder)
    chats = get_possible_chats(folderDir)
    largestChatAnalyzer(folderDir, MIN_MESSAGE_COUNT,
                        startDate=startDate, endDate=endDate, sortby=args.sortby)
    # conversationAnalyzer(folderDir, MIN_MESSAGE_COUNT,folderDir)
    timeSeriesAnalyzer(chats, folderDir, MIN_MESSAGE_COUNT,
                       startDate=startDate, endDate=endDate)


if __name__ == '__main__':
    main()
