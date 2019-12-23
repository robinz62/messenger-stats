import json
import matplotlib.pyplot as plt
import os

import messenger_stats as main
import utils

def run(messages_folder):
    utils.prepare_output_directory(os.path.join('output', 'conversation_sizes_histogram'))

    # Parse data
    counts = []
    for conv in utils.get_conversations(messages_folder):
        message_id = 1
        count = 0
        while True:
            try:
                file_name = main.MESSAGE_FILE.format(message_id)
                with open(os.path.join(messages_folder, conv, file_name)) as f:
                    data = json.load(f)
                count += len(data['messages'])
                message_id += 1
            except FileNotFoundError:
                break
        counts.append(count)

    # Create data file
    with open(os.path.join('output', 'conversation_sizes_histogram', 'data.tsv'), 'w') as f:
        f.write('count\n')
        for count in counts:
            f.write(str(count) + '\n')
    
    # Create plot
    plt.figure(figsize=(14, 6.5))
    x = counts
    plt.hist(x)
    plt.title('Conversation Sizes Histogram')
    plt.xlabel('Conversation Sizes')
    plt.ylabel('Number of Conversations')
    plt.savefig(os.path.join('output', 'conversation_sizes_histogram', 'conversation_sizes.png'), bbox_inches='tight')
    plt.close()
