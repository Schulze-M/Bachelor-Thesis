from turtle import color
import matplotlib.pyplot as plt

#needed list and dicts to handle the data
traces = list()
traceDict = dict()
subTraces = dict()
subgraphsDict = dict()

#get tracelog-file
logFile = input("Enter path to TraceLog-File (.txt format): ")
logFile = logFile.replace('"', '')

def getSubgraps(logFile):
#open the compressed tracelog.file and store the data in a list 
    with open(logFile) as traceLog:
        for trace in traceLog:
            traces.append(trace.strip())

    #create dict -> traces are the keys and the number of occurences of the trace is the value (saved as an int)
    for i in traces:
        splitted = i.split(',')
        traceDict.update({splitted[0]: int(splitted[1])})

    #get all subgraphs used from the traces -> store subgraphs as keys and the occurences as values
    for k, v in traceDict.items():
        n = 2
        while n < len(k):
            for i in range(len(k)):
                for j in range(i+1, len(k)+1):
                    if len(k[i:j]) == n and k[i:j] in subTraces:
                       subTraces.update({k[i:j]: v+subTraces[k[i:j]]})
                    elif len(k[i:j]) == n:
                        subTraces.update({k[i:j]: v})
            n += 1

    #sort the dict from longest subgraph to shortest
    for k in sorted(subTraces, key=len, reverse=True):
        subgraphsDict[k] = subTraces[k]

    plotGraph(subgraphsDict)
    graphSortedValues(subgraphsDict)

def plotGraph(graphDict):
    traceNames = list()
    numTraces = list()
        
    for k, v in graphDict.items():
        traceNames.append(k)
        numTraces.append(int(v))
    
    plt.bar(traceNames, numTraces, color = ['green'])
    
    plt.xlabel('traces')
    plt.xticks(rotation=90)
    plt.ylabel('numberTraces')
    plt.title('test')
    
    plt.show()

def graphSortedValues(subgraphsDict):
    sortedByValue = dict(sorted(subgraphsDict.items(), key=lambda item: item[1], reverse=True))

    traceNames = list()
    numTraces = list()

    for k, v in sortedByValue.items():
        traceNames.append(k)
        numTraces.append(int(v))

    plt.bar(traceNames, numTraces, color = ['green'])
    
    plt.xlabel('traces')
    plt.xticks(rotation=90)
    plt.ylabel('numberTraces')
    plt.title('test')
    
    plt.show()    

#runs the import_csv function with defined path to .csv file
if __name__ == "__main__":
    getSubgraps(logFile)