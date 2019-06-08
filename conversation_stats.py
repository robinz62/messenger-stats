import json
import os

def unicode_to_react(str):
    """
    Returns a string description of select unicode emoji characters.
    """
    if str == u'\xf0\x9f\x91\x8d':
        return 'Thumbs Up'
    if str == u'\xf0\x9f\x91\x8e':
        return 'Thumbs Down'
    if str == u'\xf0\x9f\x98\x86':
        return 'Laughing'
    if str == u'\xf0\x9f\x98\x8d':
        return 'Heart Eyes'
    if str == u'\xf0\x9f\x98\xa0':
        return 'Angry'
    if str == u'\xf0\x9f\x98\xa2':
        return 'Cry'
    if str == u'\xf0\x9f\x98\xae':
        return 'Wow'
    return 'ERROR'


def get_possible_chats(root_dir, filters=[]):
    """
    Returns a list of the available chat groups. Manually ignores hidden files.
    filter is a list of strings that must be substrings of a chat folder's name
    """
    chats = os.listdir(root_dir)
    filtered = []
    for chat in chats:
        if chat.startswith('.') or chat == 'stickers_used':
            continue
        include = True
        for f in filters:
            if f not in chat:
                include = False
                break
        if include:
            filtered.append(chat)
    
    return filtered


def conversation_stats(MESSAGES_FILE):
    """
    Returns statistics related to reacts; 3 maps as well as the message count.
    """
    with open(MESSAGES_FILE) as f:
        data = json.load(f)

    # for each person:
    # absolute react count
    # message count
    # character count

    participants = data['participants']
    react_map = {}                      # person -> { react -> count }
    msg_count_map = {}                  # person -> message count
    char_count_map = {}                 # person -> character count
    msg_count = len(data['messages'])   # total number of messages

    # initialize maps
    for person in participants:
        react_map[person['name']] = dict()
        msg_count_map[person['name']] = 0
        char_count_map[person['name']] = 0

    for msg in data['messages']:
        sender = msg['sender_name']
        if sender not in react_map:
            # person left group
            continue

        # update reactions, if available
        if 'reactions' in msg:
            for react in msg['reactions']:
                if react['reaction'] not in react_map[sender]:
                    react_map[sender][react['reaction']] = 0
                react_map[sender][react['reaction']] += 1
        
        # update message count
        msg_count_map[sender] += 1

        # update character count if message is text
        if 'content' in msg:
            char_count_map[sender] += len(msg['content'])

    # rename the unicode reacts to understandable names
    for person in react_map:
        react_counts = react_map[person]
        newDict = dict()
        for unicodeKey in react_counts:
            newDict[unicode_to_react(unicodeKey)] = react_counts[unicodeKey]
        react_counts.clear()
        react_counts.update(newDict)

    return react_map, msg_count_map, char_count_map, msg_count