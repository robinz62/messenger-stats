import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import bisect

import utils

#######################
# Top-Level Functions #
#######################

# TODO: start_date, end_date currently unused
# TODO: re-add plotting flag
def analyze_time_series(root_dir, min_msg_count, start_date, end_date,
                       output_dir, time_interval, n):
    chats = utils.get_possible_chats(root_dir)
    times_dict, titles_dict, earliest_time, latest_time = get_all_time_series(root_dir, chats, min_msg_count)
    plot_all_time_series(times_dict, titles_dict, output_dir, time_interval)
    most_frequent_chats = get_message_count_per_interval(times_dict, earliest_time, latest_time, time_interval)
    write_top_n_per_interval(most_frequent_chats, titles_dict, n, time_interval, output_dir)


###############################
# Functions for writing files #
# e.g. plots/other output     #
###############################

def write_top_n_per_interval(most_frequent_chats, titles_dict, n, time_interval, output_dir):
    """
    parameters:
        most_frequent_chats: interval center -> { chat -> messange count }
        n:                   this function saves the top N chats by message count for each interval
        time_interval:       the number of days in an interval
        output_dir:          the output directory
    """
    keys = most_frequent_chats.keys()
    time_bins = []
    total_messages = []
    with open(os.path.join(output_dir, "top_n_time_series.txt"), "w") as f:
        f.write("Printing the top " + str(n) +
                " chats by number of messages for intervals of every " + str(time_interval) + " days")
        keys = sorted(keys)
        for x in range(len(keys)):
            f.write('\n**********************************\n')
            f.write("timeStamp: " + str(keys[x]) + "\n")
            lower = datetime.utcfromtimestamp(keys[x] / 1000)
            lowerS = str(lower)
            try:
                upper = str(datetime.utcfromtimestamp(keys[x+1]/1000))
            except IndexError:
                upper = "End"
            f.write("between " + lowerS + " and " + upper + '\n')
            most_frequent_chats[keys[x]] = sorted(
                most_frequent_chats[keys[x]].items(), key=lambda z: z[1], reverse=True)

            frequented = most_frequent_chats[keys[x]][:n + 1]
            for chat, count in frequented:
                if chat not in titles_dict:
                    title = chat
                else:
                    title = titles_dict[chat] 
                f.write(title + ', ' + str(count) + '\n')

            time_bins.append(lower)
            total_messages.append(frequented[0][1])

    plt.figure(figsize=(14, 6.5))
    plt.plot(time_bins, total_messages)
    plt.title('Total messages over Time')
    plt.xlabel('Date')
    plt.ylabel('Messages per Interval (every ' +
               str(time_interval) + ' days)')
    plt.savefig(os.path.join(output_dir, 'allMessages.png'),
                bbox_inches='tight')
    plt.close()


def plot_all_time_series(times_dict, titles_dict, output_dir, time_interval):
    for chat in times_dict:
        plot_time_series(times_dict[chat], titles_dict[chat], output_dir, time_interval)


def plot_time_series(times, chat, output_dir, time_interval):
    """
    Plots a time series for an individual chat and saves it as a png image.

    parameters
        times:         a list of unix timestamps, in increasing order
        chat:          the name of the chat
        output_dir:    the output directory
        time_interval: the number of days per bin
    returns
        None
    """
    first_time = times[0]
    last_time = times[-1]
    num_bins = int((last_time - first_time) / (time_interval * utils.MICROSECONDS_PER_DAY)) + 1
    y, bin_edges = np.histogram(times, bins=num_bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    timestamps = [datetime.utcfromtimestamp(time / 1000) for time in bin_centers]
    plt.figure(figsize=(14, 6.5))
    plt.plot(timestamps, y)
    plt.title('Messages over Time')
    plt.xlabel('Date')
    plt.ylabel('Messages per Interval (every ' + str(time_interval) + ' days)')
    plt.savefig(os.path.join(output_dir, chat + '.png'), bbox_inches='tight')
    plt.close()


#################################
# Functions for retrieving data #
#################################

def get_conversation_stats(messages_file):
    """
    Returns statistics related to reacts; 3 maps as well as the message count.
    
    parameters
        messages_file: the path to the messages json file to analyze
    returns
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


def get_time_series(messages_file):
    """
    Returns list of sorted timestamps, the total number of messages, and the title of the chat.
    
    parameters:
        messages_file: the path to the messages json file to analyze.
    returns:
        times:  the sorted list of timestamps
        length: the total number of messages
        title:  the title of the chat
    """
    with open(messages_file) as f:
        data = json.load(f)

    times = sorted([message['timestamp_ms'] for message in data['messages']])
    if 'title' not in data:
        title = None
    else:
        title = data['title']
    return times, len(data['messages']), title


def get_all_time_series(root_dir, chats, min_msg_count=0):
    """
    Returns a map from chat to times, a map from chat to title, and the first and last timestamps.
    
    parameters:
        root_dir:      the path to the directory containing the chat folders
        chats:         a list of chat (folder) names
        min_msg_count: if a chat has less than this many messages, it is ignored
    returns:
        times_dict:    chat -> timestamp list
        titles_dict:   chat -> title
        earliest_time: the first occurring timestamp
        latest_time:   the last occurring timestamp
    """
    times_dict = {}
    titles_dict = {}
    earliest_time = utils.ENDTIME
    latest_time = 0
    for chat in chats:
        try:
            times, msg_count, title = get_time_series(os.path.join(root_dir, chat, 'message.json'))
            if msg_count < min_msg_count:
                continue
            if title is None:
                title = chat
            early = min(times)
            late = max(times)
            earliest_time = min(early, earliest_time)
            latest_time = max(late, latest_time)
        except:
            print("Error in get_all_time_series on chat", chat)
            continue

        # skip the first few 'messenger introduction' messages
        if len(times) >= 3:
            times = times[:-2]
        times_dict[chat] = times
        titles_dict[chat] = title

    return times_dict, titles_dict, earliest_time, latest_time


def get_message_count_per_interval(times_dict, earliest_time, latest_time, time_interval):
    """
    parameters:
        times_dict:    chat -> timestamp list
        earliest_time: the earliest timestamp
        latest_time:   the latest timestamp
        time_interval: the number of days per interval
    returns:
        most_frequent_chats: interval center -> { chat -> message count }
    """
    keys = range(earliest_time, latest_time, time_interval * utils.MICROSECONDS_PER_DAY)
    most_frequent_chats = {}
    for key in keys:
        most_frequent_chats[key] = {}

    # TODO: what is this? special title to tally total
    total_title = "........TOTAL......."
    for chat in times_dict:
        times = times_dict[chat]
        for x in range(len(keys)):
            lower = keys[x]
            if (x + 1 == len(keys)):
                upper = utils.ENDTIME
            else:
                upper = keys[x + 1]
            ind_l = bisect.bisect_left(times, lower)
            ind_r = bisect.bisect_left(times, upper)
            num_messages = ind_r - ind_l
            if num_messages != 0:
                most_frequent_chats[keys[x]][chat] = num_messages

            # Include total count
            if (total_title in most_frequent_chats[keys[x]]):
                most_frequent_chats[keys[x]][total_title] += num_messages
            else:
                most_frequent_chats[keys[x]][total_title] = num_messages

    return most_frequent_chats
