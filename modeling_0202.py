# Minimum Cost Flows Algorithm
# - Unit Cost를 기준으로 물동량을 Arc에 배치
# MIP Problem
# - 배치된 물동량을 기준으로 배차

# 링크에 물동량 배치 알고리즘
# 전제_1 : 모든 택배는 동일한 중량과 동일한 사이즈
# 전제_2 : 택배차량은 11, 8, 2.5이 존재함
# 전제_3 : 1차 물동량 배치는 단위 요금으로 정하고, 차량 배차시 각 링크에 걸리는 코스트 최소화
# 전제_4 : 
#

# 수정해야하는 사항: 허브에서의 혼합적재를 고려하지 못하고 있음
# sub의 경우, starting node와 from이 같으면 별도의 가공 X
# sub의 경우, starting node와 from이 다르면 아래 hub의 경우와 같이 처리
# hub의 경우, from & to 로 gruop_by하여 다시 배차해야할듯...

# ---- 위의 수정사항 수정 완료 ----

# 만약 period나 sequence를 고려하게 된다면?




# 필요한 패키지 설치

# Minimum Cost Flows Algorithm Solver
from ortools.graph import pywrapgraph
# MIP Problem Solver
from ortools.linear_solver import pywraplp

import pandas as pd
import itertools
import random
import math

# raw data 로드, dataframe형식
f_t_dis = pd.read_csv("from_to_distance.csv")
f_t_quan = pd.read_csv("f_t_quan.csv")
f_t_tml = pd.read_csv("f_t_tml.csv")

# Minimum Cost Flows 알고리즘에 필요한 리스트 정의
hud_node, supplies_total = [], []

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


start_nodes, end_nodes, capacities, unit_costs = [], [], [], []
supplies, tmp, quantity_on_link = [], [], []

# 주어진 OD를 리스트에 할당
for i in range(len(f_t_dis.tmlfrm)):
    start_nodes.append(int(f_t_dis.tmlfrm[i][-1]))
    end_nodes.append(int(f_t_dis.tmltto[i][-1]))

# unit_costs와 capacities를 정의 ## 해당 알고리즘이 필요함
for i in range(len(f_t_dis.tmlfrm)):
    if start_nodes[i] in hud_node or end_nodes[i] in hud_node:
        unit_costs.append(int(f_t_dis.distance[i]/5)) # 여기에 조업료?
        capacities.append(random.randrange(50, 100))
    else:
        unit_costs.append(int(f_t_dis.distance[i]))
        capacities.append(random.randrange(40, 50))




# Main Part: Minimum Cost Flow
# k개의 starting Node를 각각 Minimum Cost Flows 돌림
for k in range(len(f_t_tml.tmlcod)):
    
    tmp = []

    supplies = supplies_total[k] # k번째 start_node에서 나가는 물량

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
        pass

    else:
        print('%d:: There was an issue with the min cost flow input.' %k)

    for i in range(min_cost_flow.NumArcs()):
        tmp = []        
        if min_cost_flow.Flow(i) != 0:
            capacities[i] -= min_cost_flow.Flow(i) # i번째 arc에 물량을 둔 만큼 capa가 줄어듬
            
            tmp.append(k)
            tmp.append(min_cost_flow.Tail(i))
            tmp.append(min_cost_flow.Head(i))
            tmp.append(min_cost_flow.Flow(i))
            tmp.append(unit_costs[i])
            tmp.append(capacities[i])
            quantity_on_link.append(tmp)



quantity_on_link = pd.DataFrame(quantity_on_link)
quantity_on_link.columns = [
    'Starting Node' , 'From', 'To', 'Real Quantity', 'Arc Unit Cost', 'Remaining Capacities' ]
print(quantity_on_link)
result = quantity_on_link.groupby(['From', 'To'])['Real Quantity'].sum()
result = pd.DataFrame(result)
#result.columns = ['from', 'to', 'qauntity']
result = result.reset_index()

result.to_csv('result.csv')
print()
print(result)
print()
print(len(result['Real Quantity']))





# MIP Problem 계수, 변수 정의
V_cost = [15, 12, 8]
V_quantity = [11, 8, 2]
V_arc = [i for i in range(len(result['Real Quantity']))]
V_t = ['11', '8', '2.5']
V_idx = [idx for idx in range(20)]



solver = pywraplp.Solver.CreateSolver('SCIP')
status = solver.Solve()
infinity = solver.infinity()


Vehicle = []
for i in range(len(V_arc)):
    Vehicle.append([])
    for t in range(len(V_t)):
        Vehicle[i].append([])
        for idx in range(len(V_idx)):
            Vehicle[i][t].append([])
                

    for t, idx in itertools.product(range(len(V_t)), range(len(V_idx))):
        Vehicle[i][t][idx] = solver.IntVar(0.0, 1.0, 'V_%s_%d' %(V_t[t], idx))

result_2 = []
for i in range(len(V_arc)):

    tmp = []
    Qant = 0
    for t, idx in itertools.product(range(len(V_t)), range(len(V_idx))):
        Qant += V_quantity[t] * Vehicle[i][t][idx]
    solver.Add(Qant >= result['Real Quantity'][i])

    for t in range(len(V_t)):
        for idx in range(len(V_idx) - 1):
            solver.Add(Vehicle[i][t][idx] >= Vehicle[i][t][idx + 1])

    opt_value = 0
    for t, idx in itertools.product(range(len(V_t)), range(len(V_idx))):
        opt_value += V_cost[t] * Vehicle[i][t][idx]

    solver.Minimize(opt_value)
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
    count_V = 0
    for t, idx in itertools.product(range(len(V_t)), range(len(V_idx))):
        count_V += Vehicle[i][t][idx].solution_value()
    print(count_V)

    V_t_quan = []
    for t in range(len(V_t)):
        tmp_2 = []
        for idx in range(len(V_idx)):
            tmp_2.append(Vehicle[i][t][idx].solution_value())
        V_t_quan.append(sum(tmp_2))

    max_quan = V_quantity[0] * V_t_quan[0] + V_quantity[1] * V_t_quan[1] + V_quantity[2] * V_t_quan[2]


    tmp.append(result['From'][i])
    tmp.append(result['To'][i])
    tmp.append(count_V)
    tmp.append(V_t_quan[0])
    tmp.append(V_t_quan[1])
    tmp.append(V_t_quan[2])
    tmp.append(solver.Objective().Value())
    tmp.append(result['Real Quantity'][i])
    tmp.append(max_quan)
    tmp.append("%2.2f%%" %((1 - result['Real Quantity'][i] / max_quan)*100))
    result_2.append(tmp)


result_2 = pd.DataFrame(result_2)
result_2.columns = [
    'from', 'to', 'Total_Vehicle',
    'Q_11', 'Q_8', 'Q_2.5', 'Total_Arc_cost',
    'Real Quantity', 'max_quan', 'loss ratio'
]

result_2.to_csv('result_2.csv')
