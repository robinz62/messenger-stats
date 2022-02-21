import json
import os

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
import mplcursors
import bisect
import collections

from largest_chats import get_json_files
from largest_chats import characterCount
from largest_chats import ENDTIME
MICROSECONDS_PER_DAY = 86400000
ENDTIME = datetime.max.timestamp()*1000


def get_time_series(folder_path, sender_name, startDate=None, endDate=None):
    """
    Returns list of timestamps as well as total number of messages and the title of the chat.
    """
    data = {}
    json_files = get_json_files(folder_path)
    for j in json_files:
        
        with open(os.path.join(folder_path, j)) as f:
            data_temp = json.load(f)
        if(len(data) == 0 ):
            data = data_temp 
        else:
            data['messages'].extend(data_temp['messages'])
    
    times = sorted([message['timestamp_ms'] for message in data['messages']])
    send_times = sorted([message['timestamp_ms'] for message in data['messages']
                         if message['sender_name'] == sender_name])
    receive_times = sorted([message['timestamp_ms'] for message in data['messages']
                            if not message['sender_name'] == sender_name])
    
    sender_times = {}
    participants = [x['name'] for x in data['participants']]
    if(sender_name not in participants):
        return 
    for p in participants:
        sender_times[p] = sorted([message['timestamp_ms'] for message in data['messages']
                            if message['sender_name'] == p]) 
    if 'title' not in data:
        title = None
    else:
        title = data['title']
    assert len(times) == len(data['messages'])
    assert len(times) == len(send_times) + len(receive_times)

    if (startDate is None and endDate is None):
        pass
    else:
        if (startDate is None):
            startTime = -1
        else:
            startTime = startDate.timestamp()*1000
        if (endDate is None):
            endTime = ENDTIME
        else:
            endTime = endDate.timestamp() * 1000
        times = [x for x in times if x > startTime and x < endTime]
        send_times = [x for x in send_times if x > startTime and x < endTime]
      
        receive_times = [x for x in receive_times if x >
                         startTime and x < endTime]
        for p in participants:
            sender_times[p] = [x for x in sender_times[p] if x >
                         startTime and x < endTime]
    return times, title, send_times, receive_times, sender_times


def slider_test():

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    x = np.linspace(0, 10, 100)

    ax.set_title("Click on a line to display its label")

    # Plot a series of lines with increasing slopes.
    for i in range(1, 20):
        ax.plot(x, i * x, label="y = " + str(i) + "x")

    # Use a Cursor to interactively display the label for a selected line.
    mplcursors.cursor().connect(
        "add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))
    plt.axis([0, 1, 0, 200])

    axcolor = 'lightgoldenrodyellow'
    axpos = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor=axcolor)

    spos = Slider(axpos, 'Pos', 0.1, 90.0)

    def update(val):
        pos = spos.val
        ax.axis([pos, pos+0.1, 0, 200])
        fig.canvas.draw_idle()

    spos.on_changed(update)

    mplcursors.cursor(hover=True)
    plt.show()


def plotOverlayingTimeSeries(totalTimeDict, outputDir, TIME_INTERVAL, MIN_MESSAGE_COUNT, MIN_MESSAGE_PERIOD, title):
    fig, ax = plt.subplots(figsize=(14, 6.5))
    ax.set_title(title + ' Messages over Time (min_msg_over_time > ' +
                 str(MIN_MESSAGE_COUNT) + ' or min_msg_in_interval > ' +
                 str(MIN_MESSAGE_PERIOD) + ')')
    ax.set_xlabel('Date')
    ax.set_ylabel('Messages per Interval (every ' +
                  str(TIME_INTERVAL) + ' days)')
    sorted_chats = sorted(totalTimeDict, key=lambda chat: len(totalTimeDict[chat]), reverse=True)
    for chat in sorted_chats:
        times = totalTimeDict[chat]
        if (len(times) < 1):
            continue
        first_time = times[0]
        last_time = times[-1]
        num_months = int((last_time - first_time) /
                         (TIME_INTERVAL*MICROSECONDS_PER_DAY)) + 1
        y, timestamps = get_timestamps(times, num_months)
        # only include chats where total message exceeds MIN_MESSAGE_COUNT
        # or there exists a period with msg_count greater than MIN_MESSAGE_COUNT/4
        if (max(y) < MIN_MESSAGE_PERIOD and len(times) < MIN_MESSAGE_COUNT):
            # print('skipped: ' + chat + ' (max freq is ' + str(max(y)) + ')')
            continue
        ax.plot(timestamps, y, label=chat[:20])
    # Use a Cursor to interactively display the label for a selected line.
    mplcursors.cursor().connect(
        "add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))
    mplcursors.cursor(hover=True)
    plt.yscale('linear')
    plt.legend()

    plt.savefig(os.path.join(outputDir, title + '.png'), bbox_inches='tight')
    plt.show()
    print('done showing')
    #plt.close()
    return


def get_timestamps(times, num_months):
    y, bin_edges = np.histogram(times, bins=num_months)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    timestamps = [datetime.utcfromtimestamp(
        time / 1000) for time in bin_centers]
    return y, timestamps


def plotTimeSeries(times, sender_times, chat, outputDir, TIME_INTERVAL, MIN_MESSAGE_COUNT, MIN_MESSAGE_INTERVAL):
    '''
    plots a time series for an individual chat
    assumes times is sorted in ascending order
    '''
    first_time = times[0]
    last_time = times[-1]
    num_months = int((last_time - first_time) /
                     (TIME_INTERVAL*MICROSECONDS_PER_DAY)) + 1
    y, timestamps = get_timestamps(times, num_months)
    # clean up the boundaries

    if (len(y) < 10):

        first_time -= 5 * TIME_INTERVAL * MICROSECONDS_PER_DAY
        last_time += 5*TIME_INTERVAL*MICROSECONDS_PER_DAY
        times.extend([first_time, last_time])
        for p in sender_times:
            sender_times[p].extend([first_time, last_time])
        num_months = int((last_time - first_time) /
                         (TIME_INTERVAL*MICROSECONDS_PER_DAY)) + 1

    else:
        for p in sender_times:
            sender_times[p].extend([first_time, last_time])

    y, timestamps = get_timestamps(times, num_months)
    ys = {}
    timestamp_list = {}
    sorted_senders =sorted(sender_times, key=lambda sender: len(sender_times[sender]), reverse=True)
    for p in sender_times:
        y1, timestamps1 = get_timestamps(sender_times[p], num_months)
        ys[p]=(y1)
        timestamp_list[p]=(timestamps1)
    if not(len(times) > MIN_MESSAGE_COUNT or
            max(y) > MIN_MESSAGE_INTERVAL):
        return

    plt.figure(figsize=(14, 6.5))
    plt.plot(timestamps, y, label='all messages')

    
    for p in sorted_senders:
        plt.plot(timestamp_list[p], ys[p], label=p)

    plt.title('Messages over Time with ' + chat)
    plt.xlabel('Date')
    plt.ylabel('Messages per Interval (every ' +
               str(TIME_INTERVAL) + ' days)')
    plt.legend()
    plt.savefig(os.path.join(outputDir, chat+'.png'), bbox_inches='tight')
    plt.close()
    print('done with ' + chat)


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


def getAllTimeSeriesData(folderDir, chats, sender_name, outputDir="./TimeSeries", TIME_INTERVAL=30,
                         startDate=None, endDate=None):
    '''
    Returns a dictionary that maps a chat to its time series, along with the earliest
    and latest timestamps
    '''
    totalTimeDict = {}
    sendDict = {}
    receiveDict = {}
    senderDict = {}
    earliestTime = ENDTIME
    latestTime = 0
    for chat in chats:
        folder_path = os.path.join(folderDir, chat)
        
        times_tuple = get_time_series(
            folder_path, sender_name, startDate=startDate, endDate=endDate)
        
        if(times_tuple is None):
            continue 
        times, title, send_times, receive_times, sender_times = times_tuple
        if (len(times) < 1):
            continue
        if (title is None or len(title) < 1):
            title = chat
        early = min(times)
        late = max(times)
        earliestTime = min(early, earliestTime)
        latestTime = max(late, latestTime)

        # skip the first few 'messenger introduction' messages
        '''
        if len(times) >= 3:
            times = times[:-2]
        '''

        if (title in totalTimeDict):
            print('duplicate: ' + title + '; using instead: ' + chat)
            title = chat
        assert title not in totalTimeDict
        totalTimeDict[title] = times
        sendDict[title] = send_times
        receiveDict[title] = receive_times
        senderDict[title] = sender_times

    return totalTimeDict, earliestTime, latestTime, sendDict, receiveDict, senderDict


def plotAllTimeSeries(totalTimeDict, senderSeries, outputDir, TIME_INTERVAL, MIN_MESSAGE_COUNT, MIN_MESSAGE_INTERVAL):
    sorted_chats = sorted(totalTimeDict, key=lambda chat: len(totalTimeDict[chat]), reverse=True)
 
    for chat in sorted_chats:

        times = totalTimeDict[chat]
        msg_count = len(times)
        sender_times = senderSeries[chat]

        # get rid of weird backslashes
        if ('/' in chat):
            chat = '_'.join(chat.split('/'))
        plotTimeSeries(times, sender_times, chat, outputDir=outputDir,
                       TIME_INTERVAL=TIME_INTERVAL, MIN_MESSAGE_COUNT=MIN_MESSAGE_COUNT, MIN_MESSAGE_INTERVAL=MIN_MESSAGE_INTERVAL)
    return


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


def timeSeriesAnalyzer(folderDir, MIN_MESSAGE_COUNT, sender_name, startDate=None, endDate=None,
                       outputDir="./timeSeries", TIME_INTERVAL=30, TOP_N_PER_INTERVAL=10, plot=True):
    ###############
    # time series #
    ###############
    chats = get_possible_chats(folderDir)
    print('time series')
    allTimeSeries, earliestTime, latestTime, sendSeries, receiveSeries, senderSeries = getAllTimeSeriesData(
        folderDir, chats, sender_name, startDate=startDate, endDate=endDate)
    plot = True
    plotIndividual = True
    MIN_MESSAGE_PERIOD = MIN_MESSAGE_COUNT/10
    if (plot):
        print('plotting')
        plotOverlayingTimeSeries(allTimeSeries,
                                 outputDir=os.path.join(outputDir, "graphs"),
                                 TIME_INTERVAL=TIME_INTERVAL, MIN_MESSAGE_COUNT=MIN_MESSAGE_COUNT, MIN_MESSAGE_PERIOD=MIN_MESSAGE_PERIOD, title='all')
        plotOverlayingTimeSeries(sendSeries,
                                 outputDir=os.path.join(outputDir, "graphs"),
                                 TIME_INTERVAL=TIME_INTERVAL, MIN_MESSAGE_COUNT=MIN_MESSAGE_COUNT/2, MIN_MESSAGE_PERIOD=MIN_MESSAGE_PERIOD/2,  title='sent')
        plotOverlayingTimeSeries(receiveSeries,
                                 outputDir=os.path.join(outputDir, "graphs"),
                                 TIME_INTERVAL=TIME_INTERVAL, MIN_MESSAGE_COUNT=MIN_MESSAGE_COUNT/2, MIN_MESSAGE_PERIOD=MIN_MESSAGE_PERIOD/2,  title='received')

    if (plotIndividual):
        plotAllTimeSeries(allTimeSeries, senderSeries,
                          outputDir=os.path.join(outputDir, "graphs"),
                          TIME_INTERVAL=TIME_INTERVAL, MIN_MESSAGE_COUNT=MIN_MESSAGE_COUNT, MIN_MESSAGE_INTERVAL=MIN_MESSAGE_PERIOD)

        print('done plotting')
    topNPerInterval(allTimeSeries, earliestTime, latestTime,
                    outputDir, TIME_INTERVAL=TIME_INTERVAL, TOP_N_PER_INTERVAL=TOP_N_PER_INTERVAL)
