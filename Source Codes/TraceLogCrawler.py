#needed lists to handle the data
traces = list()
compressedTraces = list()

#get tracelog-file
logFile = input("Enter path to TraceLog-File (.txt format): ")
logFile = logFile.replace('"', '')

#create trace log in which the compressed data can be stored
compressedLogFile = logFile.replace('.txt', '_compressed.txt')

#read tracelog and safe it to a list
with open(logFile) as traceLog:
    for trace in traceLog:
        traces.append(trace.strip())

#close the opened file
traceLog.close()

#sort the traces
traces.sort()

#create compressed tracelog
with open(compressedLogFile, 'w') as newTraceLog:
    checkList = list()

    #count occurrence of each trace and save it to a list
    for trace in traces:
        #check if trace was already viewed and counted -> ensures that every trace is only stored once
        if trace not in checkList:
            occurrence = traces.count(trace)
            compressedTraces.append(trace + ',' + str(occurrence))
            #add viewed trace to checkList, to ensure it is not viewed more than once
            checkList.append(trace)

    #write compressed data to file
    for entry in compressedTraces:
        newTraceLog.write(entry + '\n')

#close the opened file
newTraceLog.close()