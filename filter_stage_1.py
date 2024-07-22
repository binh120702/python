import os 
import json
import pandas as pd
import re
from tqdm import tqdm
import copy

def dupl(e1, e2):
    return e1[0]==e2[0] and e1[1]==e2[1]

def cross(e1, e2):
    return (e1[0]<=e2[0] and e1[1]>e2[0]) or (e1[0]<e2[1] and e1[1]>=e2[1])

def inside(e1, e2):
    return e1[0]>=e2[0] and e1[1]<=e2[1]

def contains(e1, e2):
    return e1[0]<=e2[0] and e1[1]>=e2[1]

def very_close(e1, e2):
    return e2[0] - e1[1] < 3 

################################################################################################
def rule_1(e1, e2):
    if contains(e1, e2) and e1[2]=='COURT' and e2[2]!='LOC':
        return (1, 0)
    return (1, 1)

def rule_2(e1, e2):
    if dupl(e1, e2) and e1[2]=='LOC' and e2[2]!='COURT':
        return (1, 0)
    return (1, 1)

def rule_3(e1, e2):
    if dupl(e1, e2) and e1[2]=='PETITIONER' and e2[2]=='VICTIM':
        return (1, 0)
    if dupl(e1, e2) and e1[2]=='RESPONDENT' and e2[2]=='VICTIM':
        return (1, 0)
    if dupl(e1, e2) and e1[2]=='PETITIONER' and e2[2]=='CRIMINAL':
        return (1, 0)
    if dupl(e1, e2) and e1[2]=='RESPONDENT' and e2[2]=='CRIMINAL':
        return (1, 0)
    return (1, 1)

def rule_4(e1, e2):
    if contains(e1, e2) and e1[2]==e2[2]:
        return (1, 0)
    return (1, 1)

def rule_5(e1, e2):
    if dupl(e1, e2) and e1[2]=='ORG' and e2[2]!='COURT':
        return (1, 0)
    return (1, 1)

def rule_6(e1, e2):
    if contains(e1, e2) and e1[2]=='AMT':
        return (0, 1)
    return (1, 1)

################################################################################################
def app_rule(rule, e):
    keep_list = [1]*len(e['label'])
    if len(keep_list) > 2000:
        return
    for i in range(len(e['label'])):
        for j in range(len(e['label'])):
            if i==j or keep_list[i]==0 or keep_list[j]==0:
                continue
            res = rule(e['label'][i], e['label'][j])
            keep_list[i] = res[0]
            keep_list[j] = res[1]
    e['label'] = [e['label'][i] for i in range(len(e['label'])) if keep_list[i]==1]

def special_location_guess(e):
    # find all substring = loc_guess
    loc_guess = 'địa chỉ:'
    loc_guess_lower = loc_guess.lower()
    all_match = [m.start() for m in re.finditer(loc_guess_lower, e['text'].lower())]
    for i in all_match:
        st = i + len(loc_guess)
        ed = st
        while ed < len(e['text']) and e['text'][ed] != '.' and e['text'][ed] != '\n':
            ed += 1
        e['label'].append((st, ed, 'LOC'))

def special_location_correct(e):
    # find all loc or crimeloc that adjacent to each other and combine them
    list_loc = []
    for i in e['label']:
        if i[2] == 'LOC' or i[2] == 'CRIME_LOCATION':
            list_loc.append(i)
    if len(list_loc) < 2:
        return
    list_loc = sorted(list_loc, key=lambda x : x[0])
    i = 0
    while i < len(list_loc)-1:
        j = i
        while (j < len(list_loc)-1) and (list_loc[j+1][0] - list_loc[j][1] <= 5):
            j += 1
        if j != i :
            e['label'].append((list_loc[i][0], list_loc[j][1], 'LOC'))
            # print(e['text'][list_loc[i][0]:list_loc[j][1]])
        i = j + 1

def special_case_correct(e):
    if 'CASE' in e['name']:
        return 
    # remove all case-relative entities from non-case documents
    case_relative_ents = ['CRIME_LOCATION', 'CRIME_TIME', 'CRIME_TOOL', 'CRIMINAL', 'VICTIM', 'PETITIONER', 'RESPONDENT']
    e['label'] = [x for x in e['label'] if x[2] not in case_relative_ents]

def revise(data):
    new_data = []
    for d in tqdm(data):
        tmp = copy.deepcopy(d)
        special_case_correct(tmp)
        special_location_guess(tmp)
        special_location_correct(tmp)
        app_rule(rule_1, tmp)
        app_rule(rule_2, tmp)
        app_rule(rule_3, tmp)
        app_rule(rule_4, tmp)
        app_rule(rule_5, tmp)
        app_rule(rule_6, tmp)
        new_data.append(tmp)
    return new_data

def remake_data(data):
    # add ignore-case entities
    new_data = []
    cur = 0
    for d in tqdm(data):
        cur+=1
        text = d['text']
        ents = [(l[0], l[1], l[2]) for l in d['label']]

        tmp = {}
        tmp['text'] = text
        tmp['label'] = []
        hash_mem = {}
        for e in ents:
            if e[1] - e[0] < 3:
                tmp['label'].append(e)
                continue
            sss = text[e[0]:e[1]]
            sss = sss.replace('(', '\\(')
            sss = sss.replace(')', '\\)')
            sss = sss.replace('[', '\\[')
            sss = sss.replace(']', '\\]')
            if sss+'_'+e[2] in hash_mem:
                continue
            hash_mem[sss+'_'+e[2]] = 1
            all_match = [m.start() for m in re.finditer(sss.lower(), text.lower())]
            for e1 in all_match:
                st = e1
                ed = e1 + e[1]-e[0]
                lb = e[2]
                dup = False
                for e2 in tmp['label']:
                    if e2[0]==st and e2[1]==ed and e2[2]==lb:
                        dup = True
                        break
                if not dup:
                    tmp['label'].append((st, ed, lb))
        new_data.append(tmp)
    return new_data

def choose_sample_paths(data_paths_raw):
    prefix = {}
    data_paths = []
    for i in data_paths_raw:
        if i[:3] not in prefix:
            prefix[i[:3]] = 0
        prefix[i[:3]] += 1
        if prefix[i[:3]] <= 3:
            data_paths.append(i)
    return data_paths

def main():
    data_folder = 'data_phase_1/label_3h_150524_revise_caseignore'

    data_paths = sorted(os.listdir(data_folder))
    #data_paths = choose_sample_paths(data_paths)

    data = []
    for i in data_paths:
        with open(os.path.join(data_folder, i), 'r', encoding='utf-8') as f:
            tmp = json.load(f)
            tmp['name'] = i
            data.append(tmp)
    #data = remake_data(data)
    data = revise(data)
    write_folder = 'data_phase_1/label_3h_150524_revise_final'
    if not os.path.exists(write_folder):
        os.mkdir(write_folder)
    for id, i in enumerate(data):
        with open(os.path.join(write_folder, data_paths[id]), 'w', encoding='utf-8') as f:
            f.write(json.dumps(i, ensure_ascii=False))
    print('hehe')

if __name__ == '__main__':
    main()

