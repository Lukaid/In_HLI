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

I = [0]
P = [0]
N = [0, 1, 2]
M = [0, 1, 2]
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

# 0 -> 2 경로의 cost를 의도적으로 9999999로 두고 
# 0 -> 1 , 1 -> 2 경로는 각각 1, 1로 둠
cost_matrix = [[999, 1, 9999999],[1, 999, 1],[999, 1, 999]]
# ---------------------------

# quantity_matrix 생성 from n to m, box수
# 0 -> 2 의 수 1
quantity_matrix = [[0, 0, 1], [0, 0, 0], [0, 0, 0]]


# ---------------------------

# Cosntraint
# # 제약_1: sequence는 연속되어야 함
# for i, p, n, m in itertools.product(I, P, N, M):
#     for s in range(len(S) - 1):
#         solver.Add(V[i][p][n][m][s] >= V[i][p][n][m][s+1])
# period를 고려하게 된다면 아래와 같이 해야하지않을까
# for i, n, m in itertools.product(I, N, M):
#     for s in range(len(S) - 1):
#         solver.Add(V[i][p-1][n][m][s] >= V[i][p][n][m][s+1])

# 제약_2: 최초 노드에 있는 숫자만큼 차량 할당... (우선은 이렇게..)
# for n, m in itertools.product(N, M):
#     solver.Add(sum([V[i][0][n][m][s] for s in  S]) >= quantity_matrix[n][m])

# for n, m in itertools.product(N, M):
#     solver.Add(sum([V[i][0][n][m][s] for s in  S]) >= quantity_matrix[n][m])


Qauntity_in_Node_m = [0 for x in range(len(M))]

for i, n, s in itertools.product(I, N, S):
    for m in M:
        Qauntity_in_Node_m[m] += V[i][0][n][m][s]

solver.Add(Qauntity_in_Node_m == [0, 0, 1])



# Objective Function

opt_value = 0


for i, s in itertools.product(range(len(I)), range(len(S))):
    for n, m in itertools.product(range(len(N)), range(len(M))):
        opt_value += cost_matrix[n][m]*V[i][p][n][m][s]



solver.Minimize(opt_value)

status = solver.Solve()



print('Number of constraints =', solver.NumConstraints())


if status == pywraplp.Solver.OPTIMAL:
    print('Solution:')
    print('Objective value =', solver.Objective().Value())
    count_V = 0
    for i, p, n, m, s in itertools.product(range(len(I)), range(len(P)), range(len(N)), range(len(M)), range(len(S))):
        count_V += V[i][p][n][m][s].solution_value()
    
    print(count_V)

    for i, p, n, m, s in itertools.product(range(len(I)), range(len(P)), range(len(N)), range(len(M)), range(len(S))):
        print('V_%d_%d_%d_%d_%d = ' %(i, p, n, m, s), V[i][p][n][m][s].solution_value())

else:
    print('The problem does not have an optimal solution.')

print('\nAdvanced usage:')
print('Problem solved in %f milliseconds' % solver.wall_time())
print('Problem solved in %d iterations' % solver.iterations())
print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
#print(Qauntity_in_Node_m)