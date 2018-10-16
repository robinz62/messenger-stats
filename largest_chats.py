import json
import os
import pprint

ROOTDIR = './messages'  # path to 'message' folder

### NO NEED TO MODIFY BELOW THIS LINE ###

folders = os.listdir(ROOTDIR)
conversations = []
for chat in folders:
    try:
        with open(ROOTDIR + '/' + chat + '/message.json') as f:
            data = json.load(f)
        count = len(data['messages'])
        conversations.append({
            'title': data['title'],
            'count': count
        })
    except:
        pass

conversations.sort(key=lambda x: x['count'], reverse=False)
pprint.pprint(conversations)