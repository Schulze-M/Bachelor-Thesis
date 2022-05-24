import numpy as np
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization

#gets the path to the .csv file
file_path = input("Please write path to .txt TraceLog-file: ")
file_path = file_path.replace('"', '')

#specify the values
cap = int(input("Determine maximimum of counting quries: "))
threshold = float(input("Please enter Threshold in percent: "))
epsilon1 = float(input("Please enter a epsilon_1 value: "))
n = int(input("How often should the AboveThreshold-Mechanism be calculated: "))

#get the data of the TraceLog
def import_traceLog(file_path):
    #needed lists to handle the data
    traces = list()
    compressedTraces = list()
    checkList = list()

    #open the Trace Log and save the entries
    with open(file_path) as traceLog:
        for trace in traceLog:
            traces.append(trace.strip())

    #close the opened file
    traceLog.close()

    #sort the traces
    traces.sort()

    #count occurrence of each trace and save it to a list
    for trace in traces:
        #check if trace was already viewed and counted -> ensures that every trace is only stored once
        if trace not in checkList:
            occurrence = traces.count(trace)
            compressedTraces.append(trace + ',' + str(occurrence))
            #add viewed trace to checkList, to ensure it is not viewed more than once
            checkList.append(trace)

    #get number of all traces 
    numT = 0
    for i in compressedTraces:
        splitted = i.split(',')
        numT = int(splitted[1]) + numT

    print(numT)

    #terminte if epsilon1 is greater than the number of all traces
    if epsilon1 > numT:
        print("Please enter a valid epsilon value")
        quit()

    #call the get_transitions function
    get_transitions(compressedTraces, numT)

def get_transitions(traceLog, numT):
    #dicts used to handle the data
    traceDict = dict()
    subTraces = dict()

    #create dict -> traces are the keys and the number of occurences of the trace is the value (saved as an int)
    for i in traceLog:
        splitted = i.split(',')
        traceDict.update({splitted[0]: int(splitted[1])})

    #get all subgraphs used from the traces -> store subgraphs as keys and the occurences as values
    for k, v in traceDict.items():
        for i in range(len(k)):
            for j in range(i+1, len(k)+1):
                if len(k[i:j]) == 2 and k[i:j] in subTraces:
                   subTraces.update({k[i:j]: v+subTraces[k[i:j]]})
                elif len(k[i:j]) == 2:
                    subTraces.update({k[i:j]: v})

    #only n edges are viewed
    #while len(subTraces) > 20:
    #    edgesList.pop(edgesList.index(min(edgesList)))
        
    #create directly follows graph of non filtered data -> for comparison reasons only -> TODO delete
    #completeDFG(subTraces)

    #call the countingQuries function
    countingQueries(subTraces, numT)

#counts the occurens of edges in all traces -> every edges is only counted once per trace
def countingQueries(edges, numT):
    aboveQ = []
    belowQ = []
    aboveQueries = []
    belowQuries = []
    capQ = []
    c1 = 0
    b = 0
    
    #get edges and frequencies per edge
    for k, v in edges.items():
        #frequencies
        aboveQueries.append(v)
        #edges
        aboveQ.append(k)

    #copy the lists of quries to use them in the below threshold mechanism
    belowQuries = aboveQueries.copy()
    belowQ = aboveQ.copy()

    #execute the above threshold mechanism only for max 20 edges
    while c1 < n:
        returnedIDX = aboveThreshold1(aboveQueries, aboveQ, threshold, epsilon1, numT)
        if returnedIDX != -1:
            try:
                aboveQ.pop(returnedIDX)
                aboveQueries.pop(returnedIDX)
                c1 += 1
            except IndexError:
                pass
            continue
        c1 += 1

    #execute the below threshold mechanism for max 20 edges
    while b < n:
        returnedIDX = belowThreshold(belowQuries, belowQ, threshold, epsilon1, numT)
        if returnedIDX != -1:
            try:
                belowQ.pop(returnedIDX)
                belowQuries.pop(returnedIDX)
                b += 1
            except IndexError:
                pass
            continue
        b += 1

    #check if queries only passed the above threshold because of the added noise
    for x in aboveQ:
        for y in belowQ:
            if x == y:
                belowQ.remove(y)

    #cap the counting Queries at 5
    for c in belowQuries:
        if c > cap:
            c = cap
            capQ.append(c)
        else:
            capQ.append(c)
    
    #dpEventLog(heuristic(log), belowQ, edges)
    heuristic(dpEventLog(belowQ, edges))

#filter out edges that are below the given percentage
def aboveThreshold1(queries, df, T, epsilon_1, numT):
    T_hat = T + np.random.laplace(loc=0, scale = 2/epsilon_1)
    for idx, q in enumerate(queries):
        nu_i = np.random.laplace(loc=0, scale = 4/epsilon_1)
        if ((queries[idx]/numT)*100 + nu_i) >= T_hat:
            return idx
    return -1 # the index of the last element

#filter out edges that are over the given percentage
def belowThreshold(queries, df, T, epsilon_1, numT):
    T_hat = T + np.random.laplace(loc=0, scale = 2/epsilon_1)
    for idx, q in enumerate(queries):
        nu_i = np.random.laplace(loc=0, scale = 4/epsilon_1)
        if ((queries[idx]/numT)*100 + nu_i) < T_hat:
            return idx
    return -1 # the index of the last element

#calculate the dependency of the edges that are viewed
def heuristic(dpDic):
    List = []
    
    #copy the given dict
    graphDic = dpDic.copy()

    #store keys in list
    for key, val in dpDic.items():
        List.append(key)

    #calculate dependencies of the edges between the nodes, due to the know function of the heuristic miner
    for one in List:
        for two in List:
            #check a >^L a 
            if one[0] == one[1]:
                graphDic[one] = round(np.absolute((dpDic[one])/(dpDic[one]+1)), 6)
            #check if b >^L a exists, when a >^L b exists
            elif one [0] == two[1] and one[1] == two[0]:
                graphDic[one] = round(np.absolute((dpDic[one]-dpDic[two])/(dpDic[one]+dpDic[two]+1)), 6)
                graphDic[two] = round(np.absolute((dpDic[one]-dpDic[two])/(dpDic[one]+dpDic[two]+1)), 6)
            else:
                graphDic[one] = round(np.absolute((dpDic[one])/(dpDic[one]+1)), 6)

    #create directly follows graph
    directlyFollowsGraph(graphDic)
            
def directlyFollowsGraph(dic):
    #get Directly-Follows Graph of filtered Log
    gviz = dfg_visualization.apply(dic, variant=dfg_visualization.Variants.FREQUENCY)
    dfg_visualization.view(gviz)

def dpEventLog(liste, edges):
    dpDic = {}

    #create the dic that fullfuills DP
    for key, val in list(edges.items()):
        for y in liste:
            try:
                if key == y:
                    dpDic.update({key: val})
            except KeyError:
                pass
            continue

    return(dpDic)

#TODO delete
def completeDFG(dic):
    #get non filtered Directly-Follows Graph for comparison
    gviz = dfg_visualization.apply(dic, variant=dfg_visualization.Variants.FREQUENCY)
    dfg_visualization.view(gviz)

#runs the import_csv function with defined path to .txt file
if __name__ == "__main__":
    import_traceLog(file_path)