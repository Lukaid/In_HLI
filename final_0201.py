# Minimum Cost Flows Algorithm
# - Unit Cost를 기준으로 물동량을 Arc에 배치
# MIP Problem
# - 배치된 물동량을 기준으로 배차

# 링크에 물동량 배치 알고리즘
# 전제_1 : 모든 택배는 동일한 중량과 동일한 사이즈
# 전제_2 : 택배차량은 11, 8, 2.5, TR이 존재함
# 전제_3 : 1차 물동량 배치는 단위 요금으로 정하고, 차량 배차시 각 링크에 걸리는 코스트 최소화
# 전제_4 : 
# 

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
        unit_costs.append(int(f_t_dis.distance[i]/10)) # 여기에 조업료?
        capacities.append(random.randrange(500, 1000))
    else:
        unit_costs.append(int(f_t_dis.distance[i]))
        capacities.append(random.randrange(400, 500))


# MIP Problem 계수, 변수 정의
V_cost = [15, 12, 8]
V_quantity = [11, 8, 2]
V_t = ['11', '8', '2.5']
V_idx = [idx for idx in range(20)]

solver = pywraplp.Solver.CreateSolver('SCIP')
status = solver.Solve()
infinity = solver.infinity()


# Main Part: Minimum Cost
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
        # tmp_2 = []
        # for i in range(min_cost_flow.NumArcs()):
        #     tmp_2.append(min_cost_flow.Flow(i))
        # print(tmp_2)

    else:
        print('%d:: There was an issue with the min cost flow input.' %k)

    #quantity_on_link.append(tmp)

    for i in range(min_cost_flow.NumArcs()):        
        if min_cost_flow.Flow(i) != 0:
            Vehicle = [] 
            for t in range(len(V_t)):
                Vehicle.append([])
                for idx in range(len(V_idx)):
                    Vehicle[t].append([])

            for t, idx in itertools.product(range(len(V_t)), range(len(V_idx))):
                Vehicle[t][idx] = solver.IntVar(0.0, 1.0, 'V_%s_%d' %(V_t[t], idx))

            Qant = 0
            for t, idx in itertools.product(range(len(V_t)), range(len(V_idx))):
                Qant += V_quantity[t] * Vehicle[t][idx]
            solver.Add(Qant >= min_cost_flow.Flow(i))

            for t in range(len(V_t)):
                for idx in range(len(V_idx) - 1):
                    solver.Add(Vehicle[t][idx] >= Vehicle[t][idx + 1])

            opt_value = 0
            for t, idx in itertools.product(range(len(V_t)), range(len(V_idx))):
                opt_value += V_cost[t] * Vehicle[t][idx]

            solver.Minimize(opt_value)
            status = solver.Solve()
            if status == pywraplp.Solver.OPTIMAL:
                print('Solution:')
                print('Objective value =', solver.Objective().Value())
            count_V = 0
            for t, idx in itertools.product(range(len(V_t)), range(len(V_idx))):
                count_V += Vehicle[t][idx].solution_value()
            print(count_V)

            for t, idx in itertools.product(range(len(V_t)), range(len(V_idx))):
                if Vehicle[t][idx].solution_value() != 0.0:
                    print('V_%s_%d = ' %(V_t[t], idx), Vehicle[t][idx].solution_value())
            tmp_tmp_quan = []
            for t in range(len(V_t)):
                tmp_tmp = []
                for idx in range(len(V_idx)):
                    tmp_tmp.append(Vehicle[t][idx].solution_value())
                tmp_tmp_quan.append(sum(tmp_tmp))
        
            max_quan = V_quantity[0] * tmp_tmp_quan[0] + V_quantity[1] * tmp_tmp_quan[1] + V_quantity[2] * tmp_tmp_quan[2]
            tmp.append(k)
            tmp.append('%s -> %s' %(min_cost_flow.Tail(i), min_cost_flow.Head(i)))
            tmp.append(unit_costs[i])
            tmp.append(solver.Objective().Value())
            tmp.append(tmp_tmp_quan[0])
            tmp.append(tmp_tmp_quan[1])
            tmp.append(tmp_tmp_quan[2])
            tmp.append(min_cost_flow.Flow(i))
            tmp.append(max_quan)
            tmp.append("%0.2f%%" %(1 - min_cost_flow.Flow(i) / max_quan))
            print(tmp)

            quantity_on_link.append(tmp)
            tmp = []


tmp.append('Starting Node')
tmp.append('From To')
tmp.append('Arc Cost')
tmp.append('Vehicle Cost')
tmp.append('Q_11')
tmp.append('Q_8')
tmp.append('Q_2.5')
tmp.append('Real Quantity')
tmp.append('Maxium Quantity')
tmp.append('Loss Ratio')


quantity_on_link.insert(0, tmp)

quantity_on_link = pd.DataFrame(quantity_on_link)
print(quantity_on_link)

quantity_on_link.to_csv('quantity_on_link.csv')
