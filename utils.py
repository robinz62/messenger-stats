from datetime import datetime
import numpy as np
import os
import shutil

import messenger_stats as main

ENDTIME = datetime.max.timestamp() * 1000  # arbitrarily the large time (in ms)
MILLISECONDS_PER_DAY = 86400000


# TODO: expose this filtering capability to user
def get_conversations(root_dir, filters=[]):
    """Returns a list of the available conversations, corresponding to the
    folders' names.

    Args:
        root_dir (str): the path name to the folder containing the conversation
            folders (e.g. messages/inbox).
        filters (list of str, optional): a list of strings that all must be
            substrings of a conversation folder's name.
    
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


def subcategorybar(plt, X, vals, width=0.8):
    """Creates a bar graph with multiple bars per categorical variable.
    Inspired from
    https://stackoverflow.com/questions/48157735/plot-multiple-bars-for-categorical-data

    Args:
        plt (matplotlib.pyplot): a handle to the plotting object.
        X (list of str): the list of categories which contain subcategories.
        vals (list of list of num): the values to plot. The outer list
            corresponds to the subcategory values and the inner list
            corresponds to the value each category takes for the subcategory.
        width (num, optional): used to scale the plot appearance
    """
    n = len(vals)
    _X = np.arange(len(X))
    for i in range(n):
        plt.bar(_X - width/2.0 + i/float(n)*width, vals[i], width=width/float(n), align='edge')   
    plt.xticks(_X, X)


def prepare_output_directory(path):
    """Creates a directory at path, deleting the existing directory at the path
    if it exists.

    Args:
        path (str): the path to the target directory.
    """
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)
