import argparse
import os

from reacts_stats import get_possible_chats
from reacts_stats import reactsStats
from largest_chats import largestChats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', help='root messages directory')
    args = parser.parse_args()

    if not args.folder:
        if os.path.isdir('messages'):
            args.folder = 'messages'
        else:
            print((
                'Error: must specify path to messages directory or have '
                'messages directory in current directory'
            ))
            return
        
    while True:
        print('Main Menu')
        print('1. Largest Chats Ranking')
        print('2. Chat React Usage Stats')
        # add others
        print('Q. Quit')
        print()

        choice = input()
        if choice == '1':
            print('Computing...')
            largestChats(args.folder)
        elif choice == '2':
            filters = input('search chats (space-separated keywords e.g. robin) (default empty): ')
            filters = filters.split()
            chats = get_possible_chats(args.folder, filters=filters)
            if not chats:
                print('No results found\n')
                continue
            for i, item in enumerate(chats):
                print(str(i) + ' ' + item)
            choice = input()
            if not choice.isdigit() or int(choice) >= len(chats):
                print('Invalid selection\n')
                continue
            chatSelection = chats[int(choice)]
            reactsStats(os.path.join(args.folder, chatSelection, 'message.json'))
        elif choice == 'Q':
            break
        else:
            print('Not a valid option...')
        print()


if __name__ == '__main__':
    main()