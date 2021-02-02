# 일단 모델 구현을 위해 심플하게 구성

# 가정_1 : 모든 택배는 동일한 중량과 동일한 사이즈를 가지고 있다.
# 가정_2 : 모든 차량은 11톤으로 통일한다.
# 가정_3 : 모든 택배차량은 Unique한 vclcod가 부여된다.
# 가정_4 : tmlcod와 vclcod는 0부터 차레대로 커지며 연속된 정수이다.




#from __future__ import print_function
from ortools.linear_solver import pywraplp
from ortools.graph import pywrapgraph

import pandas as pd
import itertools
import random
import math

# raw data 로드, dataframe형식
f_t_dis = pd.read_csv("from_to_distance.csv")
f_t_dis_2 = pd.read_csv("from_to_distance_2.csv")
f_t_quan = pd.read_csv("f_t_quan.csv")
f_t_tml = pd.read_csv("f_t_tml.csv")
vclcod = pd.read_csv("vclcod.csv")
f_t_num = pd.read_csv("from_to_num.csv")

# solver정의
solver = pywraplp.Solver.CreateSolver('SCIP')
status = solver.Solve()
infinity = solver.infinity()



# 목적변수 생성

#I = [int(x[-3:]) for x in vclcod.vclcod] # 차량의 등록 서브, 
I = [x for x in range(1000)]
#P = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] # Period 시간 고려 변수, Time table을 참고하여 scale결정
P = [0]
N = [int(x[-3:]) for x in f_t_tml.tmlcod] # from node
M = [int(x[-3:]) for x in f_t_tml.tmlcod] # to node
S = [0, 1, 2, 3, 4, 5, 6] # 최대 6번까지 움직일 수 있음

V = [] 
for i in range(len(I)):
    V.append([])
    for p in range(len(P)):
        V[i].append([])
        for n in range(len(N)):
            V[i][p].append([])
            for m in range(len(M)):
                V[i][p][n].append([])
                for s in range(len(S)):
                    V[i][p][n][m].append([])

for i, p, n, m, s in itertools.product(range(len(I)), range(len(P)), range(len(N)), range(len(M)), range(len(S))):
    V[i][p][n][m][s] = solver.IntVar(0, 1, 'V_%d_%d_%d_%d_%d' %(i, p, n, m, s))


print('Number of variables =', solver.NumVariables())

# -------------------------




# cost_matrix 생성 from n to m
hud_node = [] # 허브 노드
for i in range(len(N)):
    if f_t_tml.tmltyp[i] == 'hub':
        hud_node.append(i)

cost_matrix = []
for i in range(len(N)):
    cost_matrix.append([])
    for j in range(len(N)):
        cost_matrix[i].append([])

for n, m in itertools.product(range(len(N)), range(len(M))):
    if N[i] in hud_node or M[i] in hud_node:
        cost_matrix[n][m] = f_t_dis_2.loc[n][m]/2 #low index, col index순
    else:
        cost_matrix[n][m] = f_t_dis_2.loc[n][m]
# ---------------------------

# time_matrix 생성 from n to m, 1이상 4이하의 정수
time_matrix = []
for i in range(len(N)):
    time_matrix.append([])
    for j in range(len(N)):
        time_matrix[i].append([])

for n, m in itertools.product(range(len(N)), range(len(M))):
        time_matrix[n][m] = math.ceil(f_t_dis_2.loc[n][m]/100) #low index, col index순
# ---------------------------

# quantity_matrix 생성 from n to m, box수
quantity_matrix = []
for i in range(len(N)):
    quantity_matrix.append([])
    for j in range(len(N)):
        quantity_matrix[i].append([])

for n, m in itertools.product(range(len(N)), range(len(M))):
        quantity_matrix[n][m] = f_t_num.loc[n][m]

# ---------------------------

# 현재 물건의 위치 


# Cosntraint
# 제약_1: sequence는 연속되어야 함
for i, p, n, m in itertools.product(I, P, N, M):
    for s in range(len(S) - 1):
        solver.Add(V[i][p][n][m][s] >= V[i][p][n][m][s+1])

# 제약_2: 최초 노드에 있는 숫자만큼 차량 할당... (우선은 이렇게..)
for n, m in itertools.product(N, M):
    solver.Add(sum([V[i][0][n][m][s] for i, s in itertools.product(I, S)]) >= quantity_matrix[n][m])


print('Number of constraints =', solver.NumConstraints())



# Objective Function

opt_value = 0

p = 0
for i, s in itertools.product(range(len(I)), range(len(S))):
    for n, m in itertools.product(range(len(N)), range(len(M))):
        opt_value += cost_matrix[n][m]*V[i][p][n][m][s]


solver.Minimize(opt_value)

status = solver.Solve()


ans_V = []
for i in range(len(I)):
    ans_V.append([])
    for p in range(len(P)):
        ans_V[i].append([])
        for n in range(len(N)):
            ans_V[i][p].append([])
            for m in range(len(M)):
                ans_V[i][p][n].append([])
                for s in range(len(S)):
                    ans_V[i][p][n][m].append([])






if status == pywraplp.Solver.OPTIMAL:
    print('Solution:')
    print('Objective value =', solver.Objective().Value())
    # print('x =', x.solution_value())
    # print('y =', y.solution_value())
    count_V = 0
    for i, p, n, m, s in itertools.product(range(len(I)), range(len(P)), range(len(N)), range(len(M)), range(len(S))):
        count_V += V[i][p][n][m][s].solution_value()
    
    print(count_V)




    # for i, p, n, m, s in itertools.product(range(len(I)), range(len(P)), range(len(N)), range(len(M)), range(len(S))):
    #     ans_V[i][p][n][m][s].append(V[i][p][n][m][s].solution_value())
    
    # for i, p, n, m, s in itertools.product(range(len(I)), range(len(P)), range(len(N)), range(len(M)), range(len(S))):
    #     if ans_V[i][p][n][m][s] == 1:
    #         print(enumerate(ans_V[i][p][n][m][s]))
    

else:
    print('The problem does not have an optimal solution.')

print('\nAdvanced usage:')
print('Problem solved in %f milliseconds' % solver.wall_time())
print('Problem solved in %d iterations' % solver.iterations())
print('Problem solved in %d branch-and-bound nodes' % solver.nodes())