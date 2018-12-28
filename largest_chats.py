import json
import os
import pprint

def largestChats(root_dir):
    """
    Reports the number of messages in each conversation in sorted order as well
    as a count of the total number of messages.
    """
    total_msg_count = 0

    folders = os.listdir(root_dir)
    conversations = []
    for chat in folders:
        try:
            with open(root_dir + '/' + chat + '/message.json') as f:
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

    conversations.sort(key=lambda x: x['count'], reverse=False)
    pprint.pprint(conversations)

    print(total_msg_count)