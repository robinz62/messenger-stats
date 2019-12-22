import bisect
import json
import matplotlib.pyplot as plt
import os
from datetime import datetime

import messenger_stats as main
import utils

N = 5  # the number of top conversations to record per time interval
TIME_INTERVAL = 30  # the number of days per time interval to analyze

def run(messages_folder, time_interval=TIME_INTERVAL):
    os.makedirs(os.path.join('output', 'largest_chats_over_time'))

    # Parse data
    conversation_to_timestamps = {}
    conversation_to_title = {}
    time_begin = None  # the globally smallest timestamp
    time_end = None  # the globally largest timestamp
    for conv in utils.get_conversations(messages_folder):
        message_count = 1
        timestamps = []
        while True:
            try:
                file_name = main.MESSAGE_FILE.format(message_count)
                with open(os.path.join(messages_folder, conv, file_name)) as f:
                    data = json.load(f)
                timestamps.extend([message['timestamp_ms'] for message in data['messages']])
                conversation_to_title[conv] = data['title'] if 'title' in data else conv
                message_count += 1
            except FileNotFoundError:
                break
        timestamps.sort()
        time_begin = timestamps[0] if time_begin == None else min(time_begin, timestamps[0])
        time_end = timestamps[-1] if time_end == None else max(time_end, timestamps[-1])
        conversation_to_timestamps[conv] = timestamps
    
    conversations_over_time = {}  # interval start -> { conversation -> message count }
    interval_starts = range(time_begin, time_end, time_interval * utils.MICROSECONDS_PER_DAY)
    for center in interval_starts:
        conversations_over_time[center] = {}

    total_title = '__total__'
    for conv, times in conversation_to_timestamps.items():
        for i in range(len(interval_starts)):
            lower = interval_starts[i]
            upper = utils.ENDTIME if i + 1 == len(interval_starts) else interval_starts[i + 1]
            ind_l = bisect.bisect_left(times, lower)
            ind_r = bisect.bisect_left(times, upper)
            num_messages = ind_r - ind_l
            if num_messages != 0:
                conversations_over_time[interval_starts[i]][conv] = num_messages

            if (total_title not in conversations_over_time[interval_starts[i]]):
                conversations_over_time[interval_starts[i]][total_title] = 0
            conversations_over_time[interval_starts[i]][total_title] += num_messages
    
    # Create data file
    conversation_to_title['__total__'] = 'Total'
    interval_starts_str = []
    total_messages = []
    with open(os.path.join('output', 'largest_chats_over_time', 'data.tsv'), 'w') as f:
        for i in range(len(interval_starts)):
            lower_str = str(datetime.utcfromtimestamp(interval_starts[i] / 1000))
            upper_str = str(datetime.utcfromtimestamp(interval_starts[i + 1] / 1000)) if i + 1 < len(interval_starts) else 'End'
            f.write('\t'.join(['timestamp', str(interval_starts[i])]) + '\n')
            f.write('\t'.join(['lower', lower_str]) + '\n')
            f.write('\t'.join(['upper', upper_str]) + '\n')
            conversations_over_time[interval_starts[i]] = sorted(
                conversations_over_time[interval_starts[i]].items(), key=lambda x: x[1], reverse=True)

            frequented = conversations_over_time[interval_starts[i]][:N + 1]  # +1 is for total
            for conv, count in frequented:
                f.write('\t'.join([conversation_to_title[conv], str(count)]) + '\n')
            f.write('\n')

            interval_starts_str.append(lower_str)
            total_messages.append(frequented[0][1])

    # Create plot
    # TODO: make this more interesting: plot more than just total somehow?
    # TODO: don't plot all the dates lol
    plt.figure(figsize=(14, 6.5))
    plt.plot(interval_starts_str, total_messages)
    plt.title('Total Messages over Time')
    plt.xlabel('Date')
    plt.ylabel('Messages per Interval')
    plt.savefig(os.path.join('output', 'largest_chats_over_time', 'total_message_time_series.png'),
                bbox_inches='tight')
    plt.close()
