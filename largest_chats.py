import json
import os

def largest_chats(root_dir):
    """
    Computes and returns a list containing all conversations sorted in
    decreasing order by message count. Also returns the total message
    count across all conversations.
    """
    total_msg_count = 0

    folders = os.listdir(root_dir)
    conversations = []
    for chat in folders:
        try:
            with open(os.path.join(root_dir, chat, 'message.json')) as f:
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