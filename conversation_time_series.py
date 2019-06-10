import json
import os

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

from largest_chats import JSON_NAME
TIME_INTERVAL = 14  # number of days for time interval analysis
MICROSECONDS_PER_DAY = 86400000


def get_time_series(MESSAGES_FILE):
    """
    Returns list of timestamps as well as total number of messages.
    """
    with open(MESSAGES_FILE) as f:
        data = json.load(f)

    times = [message['timestamp_ms'] for message in data['messages']]
    return times, len(data['messages'])


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
