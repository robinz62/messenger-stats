import json
import matplotlib.pyplot as plt
import os

import messenger_stats as main
import utils

def run(messages_folder):
    for conv in utils.get_conversations(messages_folder):
        # Parse data
        person_to_reacts_received = {}  # person -> { react -> count }
        person_to_reacts_given = {}     # person -> { react -> count }
        person_to_message_count = {}
        person_to_char_count = {}
        total_message_count = 0
        message_id = 1
        while True:
            try:
                file_name = main.MESSAGE_FILE.format(message_id)
                with open(os.path.join(messages_folder, conv, file_name)) as f:
                    data = json.load(f)
                participants = [p['name'] for p in data['participants']]
                for person in participants:
                    if person not in person_to_reacts_received:
                        person_to_reacts_received[person] = {}
                        person_to_reacts_given[person] = {}
                        person_to_message_count[person] = 0
                        person_to_char_count[person] = 0
                for msg in data['messages']:
                    sender = msg['sender_name']
                    if sender not in participants:
                        # person has left the conversation
                        continue
                    if 'reactions' in msg:
                        for react in msg['reactions']:
                            emoji = react['reaction']
                            person_to_reacts_received[sender][emoji] = \
                                person_to_reacts_received[sender].get(emoji, 0) + 1
                            if react['actor'] in participants:
                                person_to_reacts_given[react['actor']][emoji] = \
                                    person_to_reacts_given[react['actor']].get(emoji, 0) + 1
                    person_to_message_count[sender] += 1
                    if 'content' in msg:
                        person_to_char_count[sender] += len(msg['content'])
                total_message_count += len(data['messages'])
                message_id += 1
            except FileNotFoundError:
                break

        if total_message_count < main.MIN_MESSAGE_COUNT:
            continue

        utils.prepare_output_directory(os.path.join('output', 'conversation_stats', conv))

        # Additional post-processing: convert unicode emoji into human-readable description
        for person, reacts_received in person_to_reacts_received.items():
            new_dict = {}
            for unicode_emoji in reacts_received:
                react = utils.unicode_to_react(unicode_emoji)
                new_dict[react] = new_dict.get(react, 0) + reacts_received[unicode_emoji]
            reacts_received.clear()
            reacts_received.update(new_dict)
        for person, reacts_given in person_to_reacts_given.items():
            new_dict = {}
            for unicode_emoji in reacts_given:
                react = utils.unicode_to_react(unicode_emoji)
                new_dict[react] = new_dict.get(react, 0) + reacts_given[unicode_emoji]
            reacts_given.clear()
            reacts_given.update(new_dict)

        # Create data files
        with open(os.path.join('output', 'conversation_stats', conv, 'reacts_received.tsv'), 'w') as f:
            f.write('\t'.join([
                'person', 'thumbs_up', 'thumbs_down', 'laughing', 'heart_eyes',
                'angry', 'cry', 'wow', 'message_count', 'char_count',
            ]) + '\n')
            for person, reacts_received in person_to_reacts_received.items():
                f.write('\t'.join([
                    person,
                    str(reacts_received.get('Thumbs Up', 0)),
                    str(reacts_received.get('Thumbs Down', 0)),
                    str(reacts_received.get('Laughing', 0)),
                    str(reacts_received.get('Heart Eyes', 0)),
                    str(reacts_received.get('Angry', 0)),
                    str(reacts_received.get('Cry', 0)),
                    str(reacts_received.get('Wow', 0)),
                    str(person_to_message_count[person]),
                    str(person_to_char_count[person]),
                ]) + '\n')
        with open(os.path.join('output', 'conversation_stats', conv, 'reacts_given.tsv'), 'w') as f:
            f.write('\t'.join([
                'person', 'thumbs_up', 'thumbs_down', 'laughing', 'heart_eyes',
                'angry', 'cry', 'wow', 'message_count', 'char_count',
            ]) + '\n')
            for person, reacts_given in person_to_reacts_given.items():
                f.write('\t'.join([
                    person,
                    str(reacts_given.get('Thumbs Up', 0)),
                    str(reacts_given.get('Thumbs Down', 0)),
                    str(reacts_given.get('Laughing', 0)),
                    str(reacts_given.get('Heart Eyes', 0)),
                    str(reacts_given.get('Angry', 0)),
                    str(reacts_given.get('Cry', 0)),
                    str(reacts_given.get('Wow', 0)),
                    str(person_to_message_count[person]),
                    str(person_to_char_count[person]),
                ]) + '\n')

        # Create plots
        thumbs_up = []
        thumbs_down = []
        laughing = []
        heart_eyes = []
        angry = []
        cry = []
        wow = []
        participants = []
        for person, reacts_received in person_to_reacts_received.items():
            participants.append(person)
            thumbs_up.append(reacts_received.get('Thumbs Up', 0))
            thumbs_down.append(reacts_received.get('Thumbs Down', 0))
            laughing.append(reacts_received.get('Laughing', 0))
            heart_eyes.append(reacts_received.get('Heart Eyes', 0))
            angry.append(reacts_received.get('Angry', 0))
            cry.append(reacts_received.get('Cry', 0))
            wow.append(reacts_received.get('Wow', 0))
        plt.figure(figsize=(14, 6.5))
        plt.title('Reacts Received')
        utils.subcategorybar(plt, participants, [thumbs_up, thumbs_down, laughing, heart_eyes, angry, cry, wow])
        plt.legend(['Thumbs Up', 'Thumbs Down', 'Laughing', 'Heart Eyes', 'Angry', 'Cry', 'Wow'])
        plt.savefig(os.path.join('output', 'conversation_stats', conv, 'reacts_received.png'), bbox_inches='tight')
        plt.close()

        thumbs_up = []
        thumbs_down = []
        laughing = []
        heart_eyes = []
        angry = []
        cry = []
        wow = []
        participants = []
        for person, reacts_given in person_to_reacts_given.items():
            participants.append(person)
            thumbs_up.append(reacts_given.get('Thumbs Up', 0))
            thumbs_down.append(reacts_given.get('Thumbs Down', 0))
            laughing.append(reacts_given.get('Laughing', 0))
            heart_eyes.append(reacts_given.get('Heart Eyes', 0))
            angry.append(reacts_given.get('Angry', 0))
            cry.append(reacts_given.get('Cry', 0))
            wow.append(reacts_given.get('Wow', 0))
        plt.figure(figsize=(14, 6.5))
        plt.title('Reacts Received')
        utils.subcategorybar(plt, participants, [thumbs_up, thumbs_down, laughing, heart_eyes, angry, cry, wow])
        plt.legend(['Thumbs Up', 'Thumbs Down', 'Laughing', 'Heart Eyes', 'Angry', 'Cry', 'Wow'])
        plt.savefig(os.path.join('output', 'conversation_stats', conv, 'reacts_given.png'), bbox_inches='tight')
        plt.close()
