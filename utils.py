from datetime import datetime
import json
import os
import utils

ENDTIME = datetime.max.timestamp() * 1000  # from tom; not sure what this is
MESSAGE_FILE_NAME = 'message_1.json'        # the name of the messages json file
MICROSECONDS_PER_DAY = 86400000

# TODO: normalize filter case
# TODO: expose this filtering capability to user
def get_possible_chats(root_dir, filters=[]):
    """
    Returns a list of the available chat groups.
    filter is a list of strings that must be substrings of a chat folder's name
    """
    chats = os.listdir(root_dir)
    filtered = []
    for chat in chats:
        if not os.path.isfile(os.path.join(root_dir, chat, utils.MESSAGE_FILE_NAME)):
            continue
        include = True
        for f in filters:
            if f not in chat:
                include = False
                break
        if include:
            filtered.append(chat)

    return filtered


def get_titles_dict(root_dir, filters=[]):
    """
    Returns a dictionary from conversation directory name to the chat's title.
    """
    titles_dict = {}
    for chat in get_possible_chats(root_dir, filters):
        with open(os.path.join(root_dir, chat, MESSAGE_FILE_NAME)) as f:
            data = json.load(f)
            titles_dict[chat] = data['title'] if data['title'] else chat
    return titles_dict


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
    return 'OTHER'