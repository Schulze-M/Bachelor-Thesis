import csv
import pandas as pd
import pm4py
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer

#gets the path to the .csv file and the wanted threshold for the filter
file_path = input("Please write path to .csv file: ")
file_path = file_path.replace('"', '')

threshold = float(input("Please enter Threshold (0.0 - 1.0): "))

def import_csv(file_path):
    #detect the delimiter of the.csv file
    with open(file_path, "r") as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.readline())
    
    #read .csv file
    event_log = pd.read_csv(file_path, sep=dialect.delimiter)
    
    #define dataframe of the EventLog
    event_log = pm4py.format_dataframe(event_log, case_id='showTraceID', activity_key='showSensorName', timestamp_key='showExecutionTime')

    heuristic_miner(event_log)

def heuristic_miner(log):
    heu_net = heuristics_miner.apply_heu(log, parameters={heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: threshold})
    print(heu_net)
    gviz = hn_visualizer.apply(heu_net)
    hn_visualizer.view(gviz)



#runs the import_csv function with defined path to .csv file
if __name__ == "__main__":
    import_csv(file_path)