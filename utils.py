from datetime import datetime
import os

import messenger_stats as main

ENDTIME = datetime.max.timestamp() * 1000  # arbitrarily the large time (in ms)
MICROSECONDS_PER_DAY = 86400000

# TODO: expose this filtering capability to user
def get_conversations(root_dir, filters=[]):
    """Returns a list of the available conversations, corresponding to the
    folders' names.

    Args:
        root_dir (str): the path name to the folder containing the conversation
            folders (e.g. messages/inbox).
        filters (list of str): a list of strings that all must be substrings
            of a conversation folder's name.
    
    Returns:
        the filtered list of conversation folder names.
    """
    conversations = os.listdir(root_dir)
    filtered = []
    for conv in conversations:
        if not os.path.isfile(os.path.join(root_dir, conv, main.MESSAGE_FILE.format(1))):
            continue
        include = True
        for f in filters:
            if f.lower() not in conv.lower():
                include = False
                break
        if include:
            filtered.append(conv)
    return filtered


# TODO: below has not been altered

def unicode_to_react(c):
    """Returns a string description of select unicode emoji characters.

    Args:
        c (str): the emoji to obtain a name of.
    
    Returns:
        an English description of the emoji character.
    """
    if c == u'\xf0\x9f\x91\x8d':
        return 'Thumbs Up'
    if c == u'\xf0\x9f\x91\x8e':
        return 'Thumbs Down'
    if c == u'\xf0\x9f\x98\x86':
        return 'Laughing'
    if c == u'\xf0\x9f\x98\x8d':
        return 'Heart Eyes'
    if c == u'\xf0\x9f\x98\xa0':
        return 'Angry'
    if c == u'\xf0\x9f\x98\xa2':
        return 'Cry'
    if c == u'\xf0\x9f\x98\xae':
        return 'Wow'
    return 'OTHER'