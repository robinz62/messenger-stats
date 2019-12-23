from datetime import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import os

import messenger_stats as main
import utils

def run(messages_folder):
    for conv in utils.get_conversations(messages_folder):
        message_id = 1
        timestamps = []
        while True:
            try:
                file_name = main.MESSAGE_FILE.format(message_id)
                with open(os.path.join(messages_folder, conv, file_name)) as f:
                    data = json.load(f)
                timestamps.extend([message['timestamp_ms'] for message in data['messages']])
                message_id += 1
            except FileNotFoundError:
                break
        timestamps.sort()

        # skip the first few messages in case there are the 'messenger introduction' messages
        # that occur when people initially friend/connect with each other
        if len(timestamps) >= 3:
            timestamps = timestamps[2:]

        if len(timestamps) < main.MIN_MESSAGE_COUNT:
            continue

        utils.prepare_output_directory(os.path.join('output', 'time_series', conv))

        # Create data files
        with open(os.path.join('output', 'time_series', conv, 'data.tsv'), 'w') as f:
            for time in timestamps:
                f.write(str(time) + '\n')

        # Create plots
        first_time = timestamps[0]
        last_time = timestamps[-1]
        num_months = (int) ((last_time - first_time) / (30 * utils.MILLISECONDS_PER_DAY) + 1)
        y, bin_edges = np.histogram(timestamps, bins=num_months * 2)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        timestamps = [datetime.utcfromtimestamp(time / 1000) for time in bin_centers]
        plt.figure(figsize=(14, 6.5))
        plt.plot(timestamps, y)
        plt.title('Messages Rate Over Time')
        plt.xlabel('Date')
        plt.ylabel('Messages per Interval (roughly half month)')
        plt.savefig(os.path.join('output', 'time_series', conv, 'messages_rate_over_time.png'), bbox_inches='tight')
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
        plt.savefig(os.path.join('output', 'time_series', conv, 'total_messages_over_time.png'), bbox_inches='tight')
        plt.close()
