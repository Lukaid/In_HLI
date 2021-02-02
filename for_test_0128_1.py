# 일단 모델 구현을 위해 심플하게 구성

# 가정_1 : 모든 택배는 동일한 중량과 동일한 사이즈를 가지고 있다.
# 가정_2 : 모든 차량은 11톤으로 통일한다.
# 가정_3 : 모든 택배차량은 Unique한 vclcod가 부여된다.
# 가정_4 : tmlcod와 vclcod는 0부터 차레대로 커지며 연속된 정수이다.


# 모델이 제대로 돌아가는지 Test


from ortools.linear_solver import pywraplp
from ortools.graph import pywrapgraph

import pandas as pd
import itertools
import random
import math


# solver정의
solver = pywraplp.Solver.CreateSolver('SCIP')
status = solver.Solve()
infinity = solver.infinity()


# 목적변수 생성

I = [0, 1, 2]
P = [0]
N = [0, 1, 2, 3]
M = [0, 1, 2, 3]
S = [0, 1, 2, 3, 4, 5] # 최대 6번까지 움직일 수 있음

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
    V[i][p][n][m][s] = solver.IntVar(0.0, 1.0, 'V_%d_%d_%d_%d_%d' %(i, p, n, m, s))


print('Number of variables =', solver.NumVariables())

# -------------------------

# cost_matrix 생성 from n to m

# 0, 1, 2 sub //// 3 hub
# sub to sub 경로의 cost를 의도적으로 999로 두고 
# sub to hub, hub to sub 은 1로 둠
cost_matrix = [
    [999, 999, 999, 1],
    [999, 999, 999, 1],
    [999, 999, 999, 1],
    [1, 1, 1, 999]
]
# ---------------------------

# quantity_matrix 생성 from n to m, box수

quantity_matrix = [
    [0, 1, 1, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]

quantity_matrix_to_m = [0] * len(quantity_matrix)

for i in range(len(quantity_matrix)):
    for j in range(len(quantity_matrix)):
        quantity_matrix_to_m[i] += quantity_matrix[j][i]



# ---------------------------

# Cosntraint

# 제약_1: 각각의 차량은 둘 이상의 arc에 배치되면 안된다.
for i, p, n, s in itertools.product(I, P, N, S):
    solver.Add(sum(V[i][p][n][m][s] for m in M) <= 1)

for i, p, m, s in itertools.product(I, P, M, S):
    solver.Add(sum(V[i][p][n][m][s] for n in N) <= 1)


# 제약_2: sequence는 연속되어야 함 (일단 period 생각 X)
for i, p, n, m in itertools.product(I, P, N, M):
    for s, k in itertools.product(range(len(S) - 1), M):
        solver.Add(V[i][p][n][m][s] >= V[i][p][m][k][s+1])
        solver.Add(V[i][p][n][m][s] + V[i][p][m][k][s] <= 1)

# for i, p, n, m in itertools.product(I, P, N, M):
#     for s in range(len(S) - 1):
#         solver.Add(V[i][p][n][m][s] >= V[i][p][n][m][s+1])

# 제약_3: 출발 노드에 배치되는 vcl수는 출발노드의 물건의 총합과 같음
for n in N:
    solver.Add(sum(V[i][0][n][m][s] for i, m, s in itertools.product(I, M, S)) >= 
    sum(quantity_matrix[n]))

for m in M:
    solver.Add(sum(V[i][0][n][m][s] for i, n, s in itertools.product(I, N, S)) >= 
    quantity_matrix_to_m[m])


# 제약_2: 최초 노드에 있는 숫자만큼 차량 할당... (우선은 이렇게..)
# for n in N:
#     solver.Add(sum([V[0][0][n][m][s] for m, s in itertools.product(M, S)]) == 1)

# for m in M:
#     solver.Add(sum([V[0][0][n][m][s] for n, s in itertools.product(N, S)]) == 1)

# for m, s in itertools.product(M, S):
#     for n in N:
#         Q[n] - V[0][0][n][m][s]

# for n, s in itertools.product(N, S):
#     for m in M:
#         Q[m] + V[0][0][n][m][s]


# solver.Add(Q == [[],[],[1]])

for i, n, s in itertools.product(I, N, S):
    solver.Add(V[i][0][n][n][s] == 0)


# cpt_1 = []
# for n, m in itertools.product(N, M):
#     solver.Add(sum([V[i][0][n][m][s] for s in  S]) >= quantity_matrix[n][m])
#     print(sum([V[i][0][n][m][s] for s in  S]) >= quantity_matrix[n][m])
#     cpt_1.append(sum([V[i][0][n][m][s] for s in  S]) >= quantity_matrix[n][m])
# print(cpt_1)

# 제약 3: Transship 이 가능해야 한다.

# 결국 hub에서 혼재해야 하니까... qauntity를 개별로 취급해야할거같은데...
# ex_ Q_S = [[1, 2, 1, 2, 2, 1], [0, 2, 0, 0, 2, 2], [1, 0, 0, 0, 1, 0, 1]]

# 해결해야 한는것, 
# 혼재 상차가 가능함, 허브에서 물건을 원래의 목적지로 보낼 수 있어야함
# 출발을 강제시킬 수 있어야하고, 도착도 강제되어야 함...................





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
    count_V = 0
    for i, p, n, m, s in itertools.product(range(len(I)), range(len(P)), range(len(N)), range(len(M)), range(len(S))):
        count_V += V[i][p][n][m][s].solution_value()
    
    print(count_V)

    for i, p, n, m, s in itertools.product(range(len(I)), range(len(P)), range(len(N)), range(len(M)), range(len(S))):
        if V[i][p][n][m][s].solution_value() != 0.0:
            print('V_%d_%d_%d_%d_%d = ' %(i, p, n, m, s), V[i][p][n][m][s].solution_value())

else:
    print('The problem does not have an optimal solution.')

print('\nAdvanced usage:')
print('Problem solved in %f milliseconds' % solver.wall_time())
print('Problem solved in %d iterations' % solver.iterations())
print('Problem solved in %d branch-and-bound nodes' % solver.nodes())