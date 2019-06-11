import json
import os

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import bisect
import collections

from largest_chats import JSON_NAME
from largest_chats import ENDTIME
MICROSECONDS_PER_DAY = 86400000


def get_time_series(MESSAGES_FILE):
    """
    Returns list of timestamps as well as total number of messages and the title of the chat.
    """
    with open(MESSAGES_FILE) as f:
        data = json.load(f)

    times = sorted([message['timestamp_ms'] for message in data['messages']])
    if 'title' not in data:
        title = None
    else:
        title = data['title']
    return times, len(data['messages']), title


def plotTimeSeries(times, chat, outputDir, TIME_INTERVAL):
    '''
    plots a time series for an individual chat
    assumes times is sorted in ascending order
    '''
    first_time = times[0]
    last_time = times[-1]
    num_months = int((last_time - first_time) /
                     (TIME_INTERVAL*MICROSECONDS_PER_DAY)) + 1
    y, bin_edges = np.histogram(times, bins=num_months)
    bin_centers = (bin_edges[:-1] + bin_edges[1:])/2.0
    timestamps = [datetime.utcfromtimestamp(
        time / 1000) for time in bin_centers]
    plt.figure(figsize=(14, 6.5))
    plt.plot(timestamps, y)
    plt.title('Messages over Time')
    plt.xlabel('Date')
    plt.ylabel('Messages per Interval (every ' +
               str(TIME_INTERVAL) + ' days)')
    plt.savefig(os.path.join(outputDir, chat+'.png'), bbox_inches='tight')
    plt.close()


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


def getAllTimeSeriesData(folderDir, chats, MIN_MESSAGE_COUNT, plot=True, outputDir="./TimeSeries", TIME_INTERVAL=30):
    '''
    Returns a dictionary that maps a chat to its time series, along with the earliest
    and latest timestamps
    '''
    totalTimeDict = {}
    earliestTime = ENDTIME
    latestTime = 0
    for chat in chats:

        try:

            times, msg_count, title = get_time_series(
                os.path.join(folderDir, chat, JSON_NAME))
            if (title is None):
                title = chat
            early = min(times)
            late = max(times)
            earliestTime = min(early, earliestTime)
            latestTime = max(late, latestTime)

        except:
            print("************************Error************************")
            continue
        # skip the first few 'messenger introduction' messages
        if len(times) >= 3:
            times = times[:-2]

        totalTimeDict[title] = times

        if (msg_count > MIN_MESSAGE_COUNT and plot):
            plotTimeSeries(times, chat, outputDir=outputDir,
                           TIME_INTERVAL=TIME_INTERVAL)
    return totalTimeDict, earliestTime, latestTime


def saveTopN(mostFrequentChats, TOP_N_PER_INTERVAL, TIME_INTERVAL, outputDir):
    keys = mostFrequentChats.keys()
    timeBins = []
    totalMessages = []
    with open(os.path.join(outputDir, "topNtimeSeries.tsv"), "w+") as f:
        f.write("Printing the top " + str(TOP_N_PER_INTERVAL) +
                " chats by number of messages for intervals of every " + str(TIME_INTERVAL) + " days")
        keys = sorted(keys)
        for x in range(len(keys)):
            f.write('\n**********************************\n')
            f.write("timeStamp: " + str(keys[x]) + "\n")
            lower = datetime.utcfromtimestamp(keys[x] / 1000)
            lowerS = str(lower)
            try:
                upper = str(datetime.utcfromtimestamp(keys[x+1]/1000))
            except IndexError:
                upper = "End"
            f.write("between " + lowerS + " and " + upper + '\n')
            mostFrequentChats[keys[x]] = sorted(
                mostFrequentChats[keys[x]].items(), key=lambda z: z[1], reverse=True)

            frequented = mostFrequentChats[keys[x]][:TOP_N_PER_INTERVAL + 1]
            for freq in frequented:
                f.write(str(freq) + '\n')

            timeBins.append(lower)
            totalMessages.append(frequented[0][1])

    plt.figure(figsize=(14, 6.5))
    plt.plot(timeBins, totalMessages)
    plt.title('Total messages over Time')
    plt.xlabel('Date')
    plt.ylabel('Messages per Interval (every ' +
               str(TIME_INTERVAL) + ' days)')
    plt.savefig(os.path.join(outputDir, 'allMessages.png'),
                bbox_inches='tight')
    plt.close()


def topNPerInterval(allTimeSeries, earliestTime, latestTime, outputDir, TIME_INTERVAL, TOP_N_PER_INTERVAL):
    keys = range(earliestTime, latestTime,
                 TIME_INTERVAL * MICROSECONDS_PER_DAY)
    mostFrequentChats = {}
    for key in keys:
        # print(datetime.utcfromtimestamp(key/1000))
        mostFrequentChats[key] = {}

    totalTitle = "........TOTAL......."
    for title in allTimeSeries:
        # print("iterating through: " + title)
        timeSeries = allTimeSeries[title]
        for x in range(len(keys)):
            # ASSUMES timeSeries IS SORTED
            # NUMBER OF ENTRIES IN timeSeries BETWEEN THE TWO TIMESTAMPS ARE ADDED TO THE BIN
            lower = keys[x]
            if (x + 1 == len(keys)):
                upper = ENDTIME
            else:
                upper = keys[x + 1]
            indL = bisect.bisect_left(timeSeries, lower)
            indR = bisect.bisect_left(timeSeries, upper)
            numMessages = indR - indL
            if(numMessages != 0):
                mostFrequentChats[keys[x]][title] = numMessages

            # Include total count oo
            if (totalTitle in mostFrequentChats[keys[x]]):
                mostFrequentChats[keys[x]][totalTitle] += numMessages
            else:
                mostFrequentChats[keys[x]][totalTitle] = numMessages

        '''
        # DEPRECATED BECAUSE LESS EFFICIENT
        for stamp in timeSeries:
            print(stamp)
            print(keys)
            keyIndex = bisect.bisect_left(stamp, keys)
            stamp = keys[keyIndex]
            if(title in mostFrequentChats[stamp]):
                mostFrequentChats[stamp][title] += 1
            else:
                mostFrequentChats[stamp][title] = 1
        '''
    saveTopN(mostFrequentChats=mostFrequentChats, TOP_N_PER_INTERVAL=TOP_N_PER_INTERVAL,
             TIME_INTERVAL=TIME_INTERVAL, outputDir=outputDir)


def timeSeriesAnalyzer(folderDir, MIN_MESSAGE_COUNT, startDate=None, endDate=None,
                       outputDir="./timeSeries", TIME_INTERVAL=30, TOP_N_PER_INTERVAL=10, plot=True):
    ###############
    # time series #
    ###############
    chats = get_possible_chats(folderDir)
    print('time series')
    allTimeSeries, earliestTime, latestTime = getAllTimeSeriesData(
        folderDir, chats, MIN_MESSAGE_COUNT, plot=plot, outputDir=os.path.join(outputDir, "graphs"), TIME_INTERVAL=TIME_INTERVAL)
    topNPerInterval(allTimeSeries, earliestTime, latestTime,
                    outputDir, TIME_INTERVAL=TIME_INTERVAL, TOP_N_PER_INTERVAL=TOP_N_PER_INTERVAL)
