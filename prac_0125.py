# 링크에 물동량 배치 알고리즘
# 전제_1 : 모든 택배는 동일한 중량과 동일한 사이즈

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
hud_node = []
supplies_total = []

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

test = []
for k in range(len(f_t_tml.tmlcod)):

    start_nodes = []
    end_nodes   = []
    capacities  = []
    unit_costs  = []
    supplies = []

    # 주어진 OD를 리스트에 할당
    for i in range(len(f_t_dis.tmlfrm)):
        start_nodes.append(int(f_t_dis.tmlfrm[i][-1]))
        end_nodes.append(int(f_t_dis.tmltto[i][-1]))

    # unit_costs와 capacities를 정의 ## 해당 알고리즘이 필요함
    for i in range(len(f_t_dis.tmlfrm)):
        if start_nodes[i] in hud_node or end_nodes[i] in hud_node:
            unit_costs.append(int(f_t_dis.distance[i]/5))
            capacities.append(random.randrange(90, 100))
        else:
            unit_costs.append(int(f_t_dis.distance[i]))
            capacities.append(random.randrange(10))

    supplies = supplies_total[k]

    # SimpleMinCostFlow solver.
    min_cost_flow = pywrapgraph.SimpleMinCostFlow()

    # Add each arc
    for i in range(0, len(start_nodes)):
        min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[i], end_nodes[i], 
        capacities[i], unit_costs[i])

    # Add node supplies.
    for i in range(0, len(supplies)):
        min_cost_flow.SetNodeSupply(i, supplies[i])

    # Find the minimum cost flow between start_node and end_node
    if min_cost_flow.Solve() == min_cost_flow.OPTIMAL:
        print('%d:: Minimum cost:' %k, min_cost_flow.OptimalCost())
        test.append('\n')
        test.append('%d optimum' %k)
        test.append(min_cost_flow.OptimalCost())
        test.append('\n')
        print('')
        for i in range(min_cost_flow.NumArcs()):
            tmp = []
            cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
            print('%1s -> %1s   %3s  / %3s       %3s      %s' % (
                min_cost_flow.Tail(i),
                min_cost_flow.Head(i),
                min_cost_flow.Flow(i),
                min_cost_flow.Capacity(i),
                cost,
                unit_costs[i]))
            tmp.append(min_cost_flow.Tail(i))
            tmp.append(min_cost_flow.Head(i))
            tmp.append(min_cost_flow.Flow(i))
            tmp.append(min_cost_flow.Capacity(i))
            tmp.append(cost)
            tmp.append(unit_costs[i])
            test.append(tmp)
        print('')
    else:
        print('%d:: There was an issue with the min cost flow input.' %k)

print(test)
    
with open('test.txt' , 'w') as file:
    file.writelines(map(str, test))