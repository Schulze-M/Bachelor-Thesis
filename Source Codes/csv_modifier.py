import csv
import pandas as pd
import pm4py
  
file_path = input("Please write path to .csv file: ")
path = input("path ")

# open input CSV file as source
# open output CSV file as result
with open(file_path, "r") as source:
    dialect = csv.Sniffer().sniff(source.readline())
    
    event_log = pd.read_csv(file_path, sep=dialect.delimiter)

    event_log = pm4py.format_dataframe(event_log, case_id='TraceID', activity_key='Activity', timestamp_key='Timestamp')

    #sorts the EventLog
    sortedLog = event_log.sort_values(['TraceID', 'Timestamp'], ascending=True)

    #sortedLog.drop('test')
    
    sortedLog.to_csv(path_or_buf=path + 'out.csv', sep=dialect.delimiter, columns=('TraceID', 'Activity', 'Timestamp'), index=False)
       # for r in sortedLog:
            
            # Use CSV Index to remove a column from CSV
            #r[3] = r['year']
            
            #writer.writerow((r[1], r[2], r[0]))