# Minimum Cost Flows Algorithm
# 링크에 물동량 배치 알고리즘
# 전제_1 : 모든 택배는 동일한 중량과 동일한 사이즈
# 전제_2 : 모든 택배 차량은 11톤으로 통일
# 

# 필요한 패키지 설치
from __future__ import print_function
from ortools.graph import pywrapgraph
import pandas as pd
import random

# raw data 로드, dataframe형식
f_t_dis = pd.read_csv("from_to_distance.csv")
f_t_quan = pd.read_csv("f_t_quan.csv")
f_t_tml = pd.read_csv("f_t_tml.csv")

# Minimum Cost Flows 알고리즘에 필요한 리스트 정의
hud_node, supplies_total = [], []
#Q_11 = 11 # 11톤 트럭에 들어가는 박스 수 (현재 모델은 scale down되었으므로 11개로 가정)


# 허브 노드 정의
for i in range(len(f_t_tml.tmlcod)):
    if f_t_tml.tmltyp[i] == 'hub':
        hud_node.append(i)

# supplies 리스트 정의
tmp_quan = list(f_t_quan.quantity)
for i in range(len(f_t_tml.tmlcod)):
    tmp = []
    for j in range(len(f_t_tml.tmlcod) - 1):
        tmp.append(-1*(tmp_quan[0]))
        tmp_quan.pop(0)
    tmp.insert(i, -1 * sum(tmp))
    supplies_total.append(tmp)

# Main Part: Minimum Cost
# start_nodes별로 할당

start_nodes, end_nodes, capacities, unit_costs = [], [], [], []
supplies, tmp, quantity_on_link = [], [], []

# 주어진 OD를 리스트에 할당
for i in range(len(f_t_dis.tmlfrm)):
    start_nodes.append(int(f_t_dis.tmlfrm[i][-1]))
    end_nodes.append(int(f_t_dis.tmltto[i][-1]))

# unit_costs와 capacities를 정의 ## 해당 알고리즘이 필요함
for i in range(len(f_t_dis.tmlfrm)):
    if start_nodes[i] in hud_node or end_nodes[i] in hud_node:
        unit_costs.append(int(f_t_dis.distance[i]/3)) # 허브의 경우 할인을 cost 할인
        capacities.append(random.randrange(500, 1000)) # 허브의 경우 capa도 증가
    else:
        unit_costs.append(int(f_t_dis.distance[i]))
        capacities.append(random.randrange(400, 500))

for k in range(len(f_t_tml.tmlcod)): # start_nodes 별로 최저비용으로 arc(link)에 물량 배치
    while True:
        supplies = supplies_total[k]

        # SimpleMinCostFlow solver.
        min_cost_flow = pywrapgraph.SimpleMinCostFlow()

        # Add each Link
        for i in range(0, len(start_nodes)):
            min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[i], end_nodes[i], 
            capacities[i], unit_costs[i])

        # Add node supplies.
        for i in range(0, len(supplies)):
            min_cost_flow.SetNodeSupply(i, supplies[i])

        # Find the minimum cost flow between start_node and end_node
        
        if min_cost_flow.Solve() == min_cost_flow.OPTIMAL:
            
            tmp.append(min_cost_flow.OptimalCost())
            for i in range(min_cost_flow.NumArcs()):
                tmp.append(min_cost_flow.Flow(i))
            quantity_on_link.append(tmp)
            
        else:
            print('%d:: There was an issue with the min cost flow input.' %k)

        # arc에 걸리는 qauntity가 한 차 (Q_11) 분량이 되지 않는 경우, 해당 arc의 비용을 올려 다른 arc로의 배차를 유도
        # if all(0 == item or item >= Q_11 for item in tmp):
        #     capacities[i] -= min_cost_flow.Flow(i)
        #     tmp = []
        #     break
        # else:
        #     for i in range(min_cost_flow.NumArcs()):
        #         if min_cost_flow.Flow(i) < 11:
        #             unit_costs[i] = 9999
        #     tmp = []

for i in range(min_cost_flow.NumArcs()):
    tmp.append('%1s -> %1s' %(min_cost_flow.Tail(i), min_cost_flow.Head(i)))
    
tmp.insert(0, 'cost')
quantity_on_link.insert(0, tmp)

quantity_on_link = pd.DataFrame(quantity_on_link)
print(quantity_on_link)
#quantity_on_link.info()
#quantity_on_link.to_csv('quantity_on_link_2.csv')

