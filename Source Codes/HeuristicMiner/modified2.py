from queue import Empty
import numpy as np
import csv
import pandas as pd
import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization

#gets the path to the .csv file
file_path = input("Please write path to .csv file: ")

#needed global lists
List = []
liste = []

def import_csv(file_path):
    #detect the delimiter of the.csv file
    with open(file_path, "r") as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.readline())
    
    #read .csv file
    event_log = pd.read_csv(file_path, sep=dialect.delimiter)
    
    #define dataframe of the EventLog
    event_log = pm4py.format_dataframe(event_log, case_id='TraceID', activity_key='Activity', timestamp_key='Timestamp')

    #sorts the EventLog
    sortedLog = event_log.sort_values(['TraceID', 'Timestamp'], ascending=True)
    
    #get numer of traces in EventLog
    num_traces = len(event_log.TraceID.unique())
    print("Number of Traces: {}".format(num_traces))

    def get_transitions(log, numT):
        #get list of sorted activitys from log
        for index, rows in log.iterrows():
            test = [rows.TraceID, rows.Activity]
            List.append(test)
        #print(List)

        #get transitions of the EventLog
        i = 0
        for x in List:
            for y in List:
                try:
                    if (x == List[i] and y == List[i+1]) and (x[0] == y[0]):
                        liste.append((x[0], (x[1], y[1])))
                        i+=1
                    elif (x == List[i] and y == List[i+1]) and x[0] != y[0]:
                        i += 1
                except IndexError:
                    pass
                continue

        #for x in liste:
        #    for y in liste:
        #        if x[0] == y[0] and x[1] == y[1]:
        #            liste.pop(liste.index(y))

        #TODO -> get transitins, variants count only occurencs of differnt traces of activitys 
        #variants_count = case_statistics.get_variant_statistics(sortedLog)
        #variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
        #print(variants_count)

        #gives tupel of transitions with number of uses 
        #dfg = dfg_discovery.apply(log)
        #print(dfg)

        countingQueries(liste, numT)

    def countingQueries(li, numT):
        c = 0
        count = 0
        cQuery = []
        uQuery = []
        db = []
        test = []
        test2 = []

        #count how often an edge from the traces is used
        for i, item in enumerate(li):
            if len(test) != 0:
                for z in test:
                    if z[1] == item[0] and z is not Empty():
                        pass
                    else:
                        count += 1
                        for idx, items in enumerate(li):
                            if item[0] != items[0] and item[1] == items[1]:
                                count += 1
                        test.append((item[1], count))
                        count = 0 
            else:
                count += 1
                for idx, items in enumerate(li):
                    if item[0] != items[0] and item[1] == items[1]:
                        count += 1
                test.append((item[1], count))
                count = 0 

        liCopy = li.copy()

        #for i, item in enumerate(test):
        #    for idx, items in enumerate(test):
        #        if i != idx and item[0] == items[0]:
        #            test[i] = (item[0], item[1]+items[1])
        #            item = (item[0], item[1]+items[1])
        #            test.remove(items)
        #        i = test.index(item)
            


        print(li)
        print(test)

        # #cap the counting queries at 5
        #    if count > 5:
        #        count = 5
        #    cQuery.append(count)
        #    db.append(x[1])

        #execute the above threshold mechanism only for max 20 edges
        #while c < 20 and c < len(cQuery):
        #    if (aboveThreshold(cQuery, db, 7, 0.7, numT, uQuery)) != -1:
        #        liCopy.pop(aboveThreshold(cQuery, db, 7, 0.7, numT, uQuery))
        #    c += 1

        #print(len(liCopy))
        #dpEventLog(sortedLog, liCopy)

    #call get_transitions function
    get_transitions(sortedLog, num_traces)


def aboveThreshold(queries, df, T, epsilon, numTraces, uQueries):
    T_hat = T + np.random.laplace(loc=0, scale = 2/epsilon)

    for idx, q in enumerate(queries):
        nu_i = np.random.laplace(loc=0, scale = 4/epsilon)
        if (((5/0.7) + nu_i) >= T_hat) and ((uQueries[idx]/numTraces) >= 0.7):
            return idx
    return -1 # the index of the last element

def dpEventLog(sortedLog, liste):
    test = []

    #filter out the activitys
    for x in liste:
        test.append(x[1])
    print(test)

    #delete edges that didn't pass the above threshold mechanism
    #for index, row in sortedLog.iterrows():
    #    for indexe, rows in sortedLog.iterrows():
    #        if indexe == index + 1:
    #            for x in test:
    #                try:
    #                    if row.Activity == x[0] and rows.Activity == x[1]:
    #                        sortedLog = sortedLog.drop(sortedLog.index[index])
    #                        sortedLog = sortedLog.drop(sortedLog.index[indexe])
    #                except IndexError:
    #                    pass
    #                continue
    #        else:
    #            break

    dic = dfg_discovery.apply(sortedLog)
    newDict = dic 
    print(dic)

    for key, val in list(dic.items()):
        for y in test:
            try:
                if key == y:
                    del dic[key]
            except KeyError:
                pass
            continue
                
    #TODO -> vielleicht möglich für verbesserung?        
    #newDict = {key:val for key, val in dic.items() if key != y}
    print(dic)
    #dfg_utils.get_activities_from_dfg(dfg)
    directlyFollowsGraph(dic, sortedLog)
            
def directlyFollowsGraph(dic, log):
    #get Directly-Follows Graph of filtered Log
    #dfg = dfg_discovery.apply(log)
    gviz = dfg_visualization.apply(dic, log=log, variant=dfg_visualization.Variants.FREQUENCY)
    dfg_visualization.view(gviz)

#runs the import_csv function with defined path to .csv file
if __name__ == "__main__":
    import_csv(file_path)