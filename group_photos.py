import os
import argparse
from datetime import datetime


def find_photo_date(inbox_path, chat_name, photo_name, print_lines=0):
    chats = os.listdir(inbox_path)
    if (chat_name not in chats):
        raise IOError(chat_name + " not found in " + inbox_path)
    json_file = "message_1.json"
    time_stamp_trigger = 'creation_timestamp'
    file_path = os.path.join(inbox_path, chat_name, json_file)
    with open(file_path, "r") as f:
        for line in f:
            if (photo_name in line):
                print(line)
                break
        time_stamp_line = next(f)
        print(time_stamp_line)
        if (time_stamp_trigger not in time_stamp_line):
            raise AttributeError
        time_stamp = int(time_stamp_line.split(':')[-1])
        print(time_stamp)
        date = datetime.utcfromtimestamp(time_stamp)
        print(date)
        while (print_lines > 0):
            line = next(f)
            if("type" in line):
                print_lines -= 1
            print(line)

    return 'complete'


def process_photo(args):
    photo_name = args.photo_name
    chat_name = args.chat_name
    if ('+' in photo_name and chat_name is None):
        p = photo_name.split('+')
        photo_name = p[0]
        chat_name = p[1]
    date = find_photo_date(args.folder, chat_name, photo_name, args.num_lines)
    print(date)


def move_photos(folder_name, photo_grouping):
    photo_dir_name = "photos"
    for chat in os.listdir(folder_name):
        print('***** ' + chat + '*****')
        chat_path = os.path.join(folder_name, chat)
        chat_dirs = os.listdir(chat_path)
        if (photo_dir_name not in chat_dirs):
            continue
        photo_path = os.path.join(chat_path, photo_dir_name)
        for photo in os.listdir(photo_path):
            new_photo_name = photo.split('.')[0] + '+' + chat + '.jpg'
            group_photo(os.path.join(photo_path, photo),
                        new_photo_name, photo_grouping)
            SystemError()

    print('-------------done-----------------')


def group_photo(photo_path, new_photo_name, photo_grouping):
    print(photo_path)
    new_photo_path = os.path.join(photo_grouping, new_photo_name)
    print(new_photo_path)
    os.rename(photo_path, new_photo_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', required=True)
    parser.add_argument('-d', '--destination')
    parser.add_argument('-p', '--photo_name')
    parser.add_argument('-c', '--chat_name')
    parser.add_argument('-n', '--num_lines', type=int, default=0)
    args = parser.parse_args()
    if (args.photo_name):
        process_photo(args)
    else:
        move_photos(args.folder, args.destination)
