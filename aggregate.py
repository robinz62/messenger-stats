import bisect
import json
import os
from datetime import datetime

import individual as ind
import utils

def largest_chats(root_dir):
    """
    Computes and returns a list containing all conversations sorted in
    decreasing order by message count. Also returns the total message
    count across all conversations.
    """
    total_msg_count = 0
    conversations = []
    for chat in utils.get_possible_chats(root_dir):
        try:
            with open(os.path.join(root_dir, chat, utils.MESSAGE_FILE_NAME)) as f:
                data = json.load(f)
            count = len(data['messages'])
            total_msg_count += count
            if 'title' not in data:
                title = 'TITLE MISSING'
            else:
                title = data['title']
            conversations.append({
                'title': title,
                'count': count,
            })
        except IOError:
            # ignore folders not corresponding to a conversation
            pass

    conversations.sort(key=lambda x: x['count'], reverse=True)
    return conversations, total_msg_count


def largest_chats_over_time(root_dir, time_interval=30):
    """
    Returns a dictionary: time interval center -> { chat -> message count }
    """
    times_dict = {}  # chat -> list of timestamps
    time_begin = None
    time_end = None
    for chat in utils.get_possible_chats(root_dir):
        try:
            times_dict[chat] = ind.time_series(os.path.join(root_dir, chat, utils.MESSAGE_FILE_NAME))
            time_begin = times_dict[chat][0] if time_begin == None else min(time_begin, times_dict[chat][0])
            time_end = times_dict[chat][-1] if time_end == None else max(time_end, times_dict[chat][-1])
        except IOError:
            pass
    
    interval_centers = range(time_begin, time_end, time_interval * utils.MICROSECONDS_PER_DAY)
    conversations_over_time = {}
    for key in interval_centers:
        conversations_over_time[key] = {}

    total_title = "__total__"
    for chat in times_dict:
        times = times_dict[chat]
        for x in range(len(interval_centers)):
            lower = interval_centers[x]
            if (x + 1 == len(interval_centers)):
                upper = utils.ENDTIME
            else:
                upper = interval_centers[x + 1]
            ind_l = bisect.bisect_left(times, lower)
            ind_r = bisect.bisect_left(times, upper)
            num_messages = ind_r - ind_l
            if num_messages != 0:
                conversations_over_time[interval_centers[x]][chat] = num_messages

            # update totals count
            if (total_title not in conversations_over_time[interval_centers[x]]):
                conversations_over_time[interval_centers[x]][total_title] = 0
            conversations_over_time[interval_centers[x]][total_title] += num_messages

    return conversations_over_time


        