import json
import matplotlib.pyplot as plt
import os

import messenger_stats as main
import utils

N = 10  # the number of top conversations to record

def run(messages_folder):
    utils.prepare_output_directory(os.path.join('output', 'largest_chats_all_time'))

    # Parse data
    conversations = []
    for conv in utils.get_conversations(messages_folder):
        message_id = 1
        conversation = {'title': conv, 'count': 0}
        while True:
            try:
                file_name = main.MESSAGE_FILE.format(message_id)
                with open(os.path.join(messages_folder, conv, file_name)) as f:
                    data = json.load(f)
                conversation['count'] += len(data['messages'])
                if 'title' in data:
                    conversation['title'] = data['title']
                message_id += 1
            except FileNotFoundError:
                break
        conversations.append(conversation)
    conversations.sort(key=lambda x: x['count'], reverse=True)

    # Create data file
    with open(os.path.join('output', 'largest_chats_all_time', 'data.tsv'), 'w') as f:
        f.write('\t'.join(['title', 'count']) + '\n')
        for c in conversations:
            f.write('\t'.join([c['title'], str(c['count'])]) + '\n')
    
    # Create plot
    x = [c['title'] for c in conversations[:N]]
    y = [c['count'] for c in conversations[:N]]
    plt.figure(figsize=(14, 6.5))
    plt.bar(x, y)
    plt.title('Top Conversations by Message Count')
    plt.savefig(os.path.join('output', 'largest_chats_all_time', 'plot.png'), bbox_inches='tight')
    plt.close()
