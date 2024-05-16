import os 
import json
import pandas as pd

data_folder = 'label_3h_150524'

data_paths = sorted(os.listdir(data_folder))

# read all files as jsonl

data = []
for i in data_paths:
    with open(os.path.join(data_folder, i), 'r', encoding='utf-8') as f:
        tmp = json.load(f)
        data.append(tmp)

for d in data[:1]:
    text = d['text']
    ents = [(l[0], l[1], l[2]) for l in d['label']]
    
    remove_
    # check if any ent overlap
    for i in range(len(ents)):
        list_overlap = []
        for j in range(i+1, len(ents)):
            if ents[i][1] > ents[j][0] and ents[i][0] < ents[j][1]:
                list_overlap.append(j)
            
        if len(list_overlap) > 0:
            # keep only one ent type ORG left
            if ents[i][2] == 'ORG':
                ents[i] = (ents[i][0], ents[i][1], 'ORG')
                



