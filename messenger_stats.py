
import argparse
import os
import shutil

from datetime import datetime

from conversation_stats import conversationAnalyzer
from conversation_time_series import timeSeriesAnalyzer
from largest_chats import largestChatAnalyzer


def setupDirTree(folderDir, outputDir="./"):
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
    if os.path.isdir(outputDir):
        shutil.rmtree(outputDir)

    aggreOutDir = os.path.join(outputDir, 'aggregate')
    timeOutDir = os.path.join(outputDir, 'timeSeries')
    timeGraphOutDir = os.path.join(outputDir, 'timeSeries', 'graphs')
    os.makedirs(aggreOutDir)
    os.makedirs(timeOutDir)
    os.makedirs(timeGraphOutDir)
    return folderDir, aggreOutDir, timeOutDir


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
    parser.add_argument(
        '-o', '--output', help="where to save the output data", default="./output")
    parser.add_argument(
        '-n', '--topN', help="top N chats displayed per time interval", default=10, type=int)
    parser.add_argument('-t', '--timeInterval',
                        help="number of days for each time interval", default=30, type=int)
    parser.add_argument('-p', '--plotTimeInterval',
                        help="whether to plot individual plots for time series analysis", action='store_true')
    args = parser.parse_args()

    ###############################################################################################

    MIN_MESSAGE_COUNT = args.minSize
    startDate = None
    if (args.startDate):
        startDate = datetime.strptime(args.startDate, "%Y-%m-%d")
    endDate = None
    if (args.endDate):
        endDate = datetime.strptime(args.endDate, "%Y-%m-%d")

    folderDir, aggreOutDir, timeOutDir = setupDirTree(
        args.folder, outputDir=args.output)

    basicAnalysis = False
    if(basicAnalysis):
        largestChatAnalyzer(folderDir, MIN_MESSAGE_COUNT,
                            startDate=startDate, endDate=endDate, sortby=args.sortby, outputDir=aggreOutDir)

    karmaAnalysis = False
    if(karmaAnalysis):
        # conversationAnalyzer(folderDir, MIN_MESSAGE_COUNT,folderDir)
        pass

    timeAnalysis = True
    if(timeAnalysis):
        timeSeriesAnalyzer(folderDir, MIN_MESSAGE_COUNT,
                           startDate=startDate, endDate=endDate, outputDir=timeOutDir,
                           TOP_N_PER_INTERVAL=args.topN, TIME_INTERVAL=args.timeInterval, plot=args.plotTimeInterval)


if __name__ == '__main__':
    main()
