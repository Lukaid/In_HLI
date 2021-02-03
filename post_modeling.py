import pandas as pd
import itertools

result_2 = pd.read_csv("result_2.csv").drop('Unnamed: 0', axis=1)

len_result_2 = len(result_2['from'])

list_round, list_oneway, list_round_qaun = [], [], []
list_round_idx, list_oneway_idx, list_round_tuple_idx = [], [], []

for i, j in itertools.product(range(len_result_2), range(len_result_2)):
    if list(result_2.loc[i][0:2]) == list(result_2.loc[j][0:2])[::-1]:
        if i not in list_round_idx:
            list_round_idx.append(i)
            list_round_idx.append(j)
            list_round_tuple_idx.append((i, j))
    
for i in range(len_result_2):
    if i not in list_round_idx:
        list_oneway_idx.append(i)

for i in list_round_idx:
    list_round.append(list(result_2.loc[i]))

for i in list_oneway_idx:
    list_oneway.append(list(result_2.loc[i]))

for i in list_round_tuple_idx:
    tmp = []
    tmp.append('%d <-> %d' %(result_2.loc[i[0]]['from'],result_2.loc[i[0]]['to']))
    tmp.append(int(min(result_2.loc[i[0]]['Q_11'], result_2.loc[i[1]]['Q_11'])))
    tmp.append(int(min(result_2.loc[i[0]]['Q_8'], result_2.loc[i[1]]['Q_8'])))
    tmp.append(int(min(result_2.loc[i[0]]['Q_2.5'], result_2.loc[i[1]]['Q_2.5'])))
    tmp.append(int(result_2.loc[i[0]]['Q_11'] - tmp[1]))
    tmp.append(int(result_2.loc[i[1]]['Q_11'] - tmp[1]))
    tmp.append(int(result_2.loc[i[0]]['Q_8'] - tmp[2]))
    tmp.append(int(result_2.loc[i[1]]['Q_8'] - tmp[2]))
    tmp.append(int(result_2.loc[i[0]]['Q_2.5'] - tmp[3]))
    tmp.append(int(result_2.loc[i[1]]['Q_2.5'] - tmp[3]))
    list_round_qaun.append(tmp)

round = pd.DataFrame(list_round)
round.columns = [
    'from', 'to', 'Real Quantity', 'Total_Vehicle',
    'Q_11', 'Q_8', 'Q_2.5', 'Total_Arc_cost',
    'max_quan', 'loss ratio'
]

oneway = pd.DataFrame(list_oneway)
oneway.columns = [
    'from', 'to', 'Real Quantity', 'Total_Vehicle',
    'Q_11', 'Q_8', 'Q_2.5', 'Total_Arc_cost',
    'max_quan', 'loss ratio'
]

round_qaun = pd.DataFrame(list_round_qaun)
round_qaun.columns = [
    'arc', 'round_Q_11', 'round_Q_8', 'round_Q_2.5', 
    'oneway_up_Q_11', 'oneway_down_Q_11', 
    'oneway_up_Q_8', 'oneway_down_Q_8', 
    'oneway_up_Q_2.5', 'oneway_down_Q_2.5'
]


round.to_csv('round.csv')
oneway.to_csv('oneway.csv')
round_qaun.to_csv('round_qaun.csv')

