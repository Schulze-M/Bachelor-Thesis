import numpy as np
import csv
import pandas as pd
import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization

#gets the path to the .csv file
file_path = input("Please write path to .csv file: ")
file_path = file_path.replace('"', '')

cap = int(input("Determine maximimum of counting quries: "))
threshold = float(input("Please enter Threshold in percent: "))
n = int(input("Determine how often the AboveThreshold-Mechanism should be computed: "))
epsilon1 = float(input("Please enter a epsilon_1 value: "))

def import_csv(file_path):
    #detect the delimiter of the.csv file
    with open(file_path, "r") as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.readline())
    
    #read .csv file
    event_log = pd.read_csv(file_path, sep=dialect.delimiter)
    
    #define dataframe of the EventLog
    event_log = pm4py.format_dataframe(event_log, case_id='showTraceID', activity_key='showSensorName', timestamp_key='showExecutionTime')
    
    #get numer of traces in EventLog
    num_traces = len(event_log.showTraceID.unique())
    print("Number of Traces: {}".format(num_traces))

    #call get_transitions function
    get_transitions(event_log, num_traces)

def get_transitions(log, numT):
    edgesList = []
    checkerList = []

    #get edges tripel with frequency from event log
    edges = dfg_discovery.apply(log, variant=dfg_discovery.Variants.FREQ_TRIPLES)
    
    #create a list with the egde tripels and their frequency
    for k, v in edges.items():
        checkerList.append((k, v))

    #get edge tupels with the corresponding frequencys
    for k, v in edges.items():
        counting = 1
        for key, value in edges.items():
            if (k[0], k[1]) == (key[0], key[1]) and list(edges.keys()).index(k) != list(edges.keys()).index(key):
                if ((k[0], k[1]) in checkerList) == False:
                    counting += 1
                    edgesList.append(((k[0], k[1]), v + value))
                    checkerList.append((k[0], k[1]))
            if (k[1], k[2]) == (key[1], key[2]) and list(edges.keys()).index(k) != list(edges.keys()).index(key):
                if ((k[1], k[2]) in checkerList) == False:
                    counting += 1
                    edgesList.append(((k[1], k[2]), v + value))
                    checkerList.append((k[1], k[2]))
        if counting == 1 and ((k[0], k[1]) in checkerList) == False :
            edgesList.append(((k[0], k[1]), v))
            checkerList.append((k[0], k[1]))
        if counting == 1 and ((k[1], k[2]) in checkerList) == False :
            edgesList.append(((k[1], k[2]), v))
            checkerList.append((k[1], k[2]))
        counting = 1
        
    #create directly follows graph of non filtered data -> for comparison reasons only -> TODO delete
    #normalEventLog(edgesList)

    #call the countingQuries function
    countingQueries(edgesList, numT)

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
    for x in edges:
        #frequencies
        aboveQueries.append(x[1])
        #edges
        aboveQ.append(x[0])

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
        returnedIDX = belowThreshold(belowQuries, aboveQ, threshold, epsilon1, numT)
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
                graphDic[one] = round(np.absolute((dpDic[one])/(dpDic[one]+1)), 4)
            #check if b >^L a exists, when a >^L b exists
            elif one [0] == two[1] and one[1] == two[0]:
                graphDic[one] = round(np.absolute((dpDic[one]-dpDic[two])/(dpDic[one]+dpDic[two]+1)), 4)
                graphDic[two] = round(np.absolute((dpDic[one]-dpDic[two])/(dpDic[one]+dpDic[two]+1)), 4)
            else:
                graphDic[one] = round(np.absolute((dpDic[one])/(dpDic[one]+1)), 4)

    #create directly follows graph
    directlyFollowsGraph(graphDic)
            
def directlyFollowsGraph(dic):
    #get Directly-Follows Graph of filtered Log
    gviz = dfg_visualization.apply(dic, variant=dfg_visualization.Variants.FREQUENCY)
    dfg_visualization.view(gviz)

def dpEventLog(liste, edgesList): 
    allDic = {}
    dpDic = {}

    #create dict from given list
    for x in edgesList:
        allDic.update({x[0]: x[1]})

    #create the dic that fullfuills DP
    for key, val in list(allDic.items()):
        for y in liste:
            try:
                if key == y:
                    dpDic.update({key: val})
            except KeyError:
                pass
            continue

    return(dpDic)

#TODO delete
def normalEventLog(edgesList):
    nDic = {}

    #create dict from given list
    for x in edgesList:
        nDic.update({x[0]: x[1]})

    completeDFG(nDic)

#TODO delete
def completeDFG(dic):
    #get non filtered Directly-Follows Graph for comparison
    gviz = dfg_visualization.apply(dic, variant=dfg_visualization.Variants.FREQUENCY)
    dfg_visualization.view(gviz)

#runs the import_csv function with defined path to .csv file
if __name__ == "__main__":
    import_csv(file_path)