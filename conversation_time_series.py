import json
import os

def get_time_series(MESSAGES_FILE):
    """
    Returns list of timestamps as well as total number of messages.
    """
    with open(MESSAGES_FILE) as f:
        data = json.load(f)

    times = [message['timestamp_ms'] for message in data['messages']]
    return times, len(data['messages'])