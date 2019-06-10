
import argparse
import os
import shutil

from datetime import datetime

from conversation_stats import conversationAnalyzer
from conversation_time_series import timeSeriesAnalyzer
from largest_chats import largestChatAnalyzer


def setupDirTree(folderDir):
    if not folderDir:
        if os.path.isdir('messages/inbox'):
            folderDir = 'messages/inbox'
        else:
            print((
                'Error: must specify path to messages directory or have '
                'the messages/inbox directory in current directory'
            ))
            return

    # create output dirs, deleting old if exists
    if os.path.isdir('output'):
        shutil.rmtree('output')
    os.makedirs(os.path.join('output', 'data', 'aggregate'))
    os.makedirs(os.path.join('output', 'data', 'individual'))
    os.makedirs(os.path.join('output', 'graphs', 'aggregate'))
    os.makedirs(os.path.join('output', 'graphs', 'individual'))
    return folderDir


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


def main():
    """
    Excuse how ugly this function is. Aside from setup, different analysis is
    separated into different sections. Within each section, data is generated,
    saved, and also plots are saved.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help='root messages directory')
    parser.add_argument('-d', '--startDate',
                        help='earliest message from this date (YYYY-MM-DD)')
    parser.add_argument('-e', '--endDate',
                        help='last message up to this date (YYYY-MM-DD)')
    parser.add_argument(
        '-m', '--minSize', help="size of smallest chat you wish to include", type=int, default=500)
    parser.add_argument(
        '-s', '--sortby', help="by what to sort the largest chats (messages, characters)", default="messages")
    args = parser.parse_args()

    ###############################################################################################

    MIN_MESSAGE_COUNT = args.minSize
    startDate = None
    if (args.startDate):
        startDate = datetime.strptime(args.startDate, "%Y-%m-%d")
    endDate = None
    if (args.endDate):
        endDate = datetime.strptime(args.endDate, "%Y-%m-%d")

    folderDir = setupDirTree(args.folder)
    chats = get_possible_chats(folderDir)
    largestChatAnalyzer(folderDir, MIN_MESSAGE_COUNT,
                        startDate=startDate, endDate=endDate, sortby=args.sortby)
    # conversationAnalyzer(folderDir, MIN_MESSAGE_COUNT,folderDir)
    timeSeriesAnalyzer(chats, folderDir, MIN_MESSAGE_COUNT,
                       startDate=startDate, endDate=endDate)


if __name__ == '__main__':
    main()
