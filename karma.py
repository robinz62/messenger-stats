import json

MESSAGES_FILE = 'message.json'  # path to 'message.json' file

### NO NEED TO MODIFY BELOW THIS LINE ###

def unicode_to_react(str):
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

with open(MESSAGES_FILE) as f:
    data = json.load(f)

# for each person:
# absolute react count
# message count
# word count
# words per message

participants = data['participants']
reactMap = {}       # person -> { react -> count }
msgCountMap = {}    # person -> message count
charCountMap = {}   # person -> character count

# initialize maps
for person in participants:
    reactMap[person['name']] = dict()
    msgCountMap[person['name']] = 0
    charCountMap[person['name']] = 0

for msg in data['messages']:
    sender = msg['sender_name']

    # update reactions, if available
    if 'reactions' in msg:
        for react in msg['reactions']:
            if react['reaction'] not in reactMap[sender]:
                reactMap[sender][react['reaction']] = 0
            reactMap[sender][react['reaction']] += 1
    
    # update message count
    msgCountMap[sender] += 1

    # update character count if message is text
    if 'content' in msg:
        charCountMap[sender] += len(msg['content'])

# rename the unicode reacts to understandable names
for person in reactMap:
    reactCounts = reactMap[person]
    newDict = dict()
    for unicodeKey in reactCounts:
        newDict[unicode_to_react(unicodeKey)] = reactCounts[unicodeKey]
    reactCounts.clear()
    reactCounts.update(newDict)

# print results

print('REACT STATS')
print('')
for person in reactMap:
    print(person)
    print('-' * len(person))
    for react in reactMap[person]:
        print(react + ': ' + str(reactMap[person][react]))
    print('')

print('MESSAGE COUNT')
print('-------------')
for person in msgCountMap:
    print(person + ': ' + str(msgCountMap[person]))

print('')
print('CHARACTER COUNT')
print('---------------')
for person in charCountMap:
    print(person + ': ' + str(charCountMap[person]))