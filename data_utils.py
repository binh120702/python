import os 
import json
from tqdm import tqdm

def dupl(e1, e2):
    return e1[0]==e2[0] and e1[1]==e2[1]

def cross(e1, e2):
    return (e1[0]<=e2[0] and e1[1]>e2[0]) or (e1[0]<e2[1] and e1[1]>=e2[1])

def inside(e1, e2):
    return e1[0]>=e2[0] and e1[1]<=e2[1]

def contains(e1, e2):
    return e1[0]<=e2[0] and e1[1]>=e2[1]

def overlap(e1, e2):
    return dupl(e1, e2) or cross(e1, e2) or inside(e1, e2) or contains(e1, e2)

def count_ent(data):
    ent_count = {}
    for i in data:
        for e in i['label']:
            if e[2] not in ent_count:
                ent_count[e[2]] = 1
            else:
                ent_count[e[2]] += 1
    return ent_count

def count_overlap(data):
    overlap_count={}
    for doc in tqdm(data):
        d = doc['label']
        l = len(d)
        for i in range(l):
            for j in range(i+1, l):
                if overlap(d[i], d[j]): 
                    if d[i][2] < d[j][2]:
                        temp = d[i][2] + '-' + d[j][2] 
                    else:
                        temp = d[j][2] + '-' + d[i][2]
                    if temp in overlap_count:
                        overlap_count[temp] += 1
                    else:
                        overlap_count[temp] = 1
    return overlap_count

def main():
    data_folder = 'data_phase_1/label_3h_150524_revise_final'

    data_paths = sorted(os.listdir(data_folder))
    data = []
    for i in data_paths:
        with open(os.path.join(data_folder, i), 'r', encoding='utf-8') as f:
            tmp = json.load(f)
            data.append(tmp)
    ent_count = count_overlap(data)
    for i in ent_count:
        print(i, '\t\t', ent_count[i])

if __name__ == '__main__':
    main()
    print('Done')