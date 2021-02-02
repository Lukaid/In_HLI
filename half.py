import itertools

# Minimum Cost Flows Algorithm Solver
from ortools.graph import pywrapgraph
# MIP Problem Solver
from ortools.linear_solver import pywraplp

V_cost = [11, 8, 2]
V_quantity = [11, 8, 2]
Vehicle = []
V_t = ['11', '8', '2.5']
V_i = [i for i in range(20)]

solver = pywraplp.Solver.CreateSolver('SCIP')
status = solver.Solve()
infinity = solver.infinity()


Vehicle = [] 
for t in range(len(V_t)):
    Vehicle.append([])
    for i in range(len(V_i)):
        Vehicle[t].append([])

print(Vehicle)


for t, i in itertools.product(range(len(V_t)), range(len(V_i))):
    Vehicle[t][i] = (solver.IntVar(0.0, 1.0, 'V_%s_%d' %(V_t[t], i)))

    V_cost[t] * Vehicle[t][i]
    V_quantity[t] * Vehicle[t][i]

print(Vehicle)
print(Vehicle[1][1])
