import argparse
import matplotlib.pyplot as plt
import os

import conversation_sizes_histogram
import conversation_stats
import largest_chats_all_time
import largest_chats_over_time
import time_series
import utils

# TODO: eventually: make constants available as command line arguments
MESSAGE_FILE = 'message_{}.json'  # the name of the json file
MIN_MESSAGE_COUNT = 50  # minimum number of messages required to produce analysis

def main():
    args = parse_arguments()
    print_warning_message()

    # Analyses to perform: comment individual lines to skip that analysis.

    # Aggregate analyses
    conversation_sizes_histogram.run(args.folder)
    largest_chats_all_time.run(args.folder)
    largest_chats_over_time.run(args.folder)

    # Individual analyses: note these tend to take much longer if the number of
    # conversations to analyze is not restricted.
    conversation_stats.run(args.folder)
    time_series.run(args.folder)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help='root messages directory')
    args = parser.parse_args()

    if not args.folder:
        if os.path.isdir(os.path.join('messages', 'inbox')):
            args.folder = os.path.join('messages', 'inbox')
        else:
            print((
                'Error: must specify path to messages directory or have '
                'the messages/inbox directory in current directory'
            ))
            exit()
    return args


def print_warning_message():
    """Prepares the output directory. If a directory with the same name already
    exists, warns the user before deleting it.
    """
    if os.path.isdir('output'):
        print((
            'Warning: existing output directory detected.\n'
            'Running this program will delete any existing, conflicting '
            'directories. Continue? [Y/n]:'
        ), end=' ')
        user_input = input()
        if user_input != 'y' and user_input != 'Y' and user_input != '':
            print('Exiting program...')
            exit()


if __name__ == '__main__':
    main()
