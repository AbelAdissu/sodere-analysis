import json 
import csv
import random 
import pandas as pd
import prompts 


def load_parquet_to_json_list(parquet_file_path):
    data = pd.read_parquet(parquet_file_path, engine='pyarrow')

    json_list = []

    for index, row in data.iterrows():
        jso = json.loads(row.to_json())
        jso['index'] = index
        json_list.append(jso)
    
    return json_list

'''
The function load_parquet_to_json_list is designed to load data from a Parquet file and 
convert it into a list of JSON objects. 

'''

def load_jsonl_to_json_list(jsonl_file_path):
    json_list = []

    with open(jsonl_file_path) as f:
        for line in f:
            json_list.append(json.loads(line))
    
    return json_list

'''
The function load_jsonl_to_json_list is designed to read data from a JSON Lines (JSONL) file and 
convert each line into a JSON object, which it collects into a list. 

'''