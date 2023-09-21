"""
sets:
I: places, denotes as i,j
K: trucks, denotes as k

parameter:
d_ij: distance from i to j
s_i: start time for i
t_i: end time for i
u_i: demand for i
w_i: service time for i
v: truck speed
c: capacity

variables:
x_ijk: from i to j by truck k, binary
y_ik: whether to i by truck k, binary
z_i: time to arrive at i, integer

objective:
min sum(x_ijk * d_ij) of all i,j,k

constraints:
1)
2)
3)
4)
... Check gurobi file


"""
from docplex.mp.model import Model
import pandas as pd
from itertools import combinations
from copy import deepcopy
import csv
scale = '75'
customer_path = f'C:/Users/una12/Desktop/碩一/整數規劃/project/Input_files/customer_info_{scale}.csv'
vehicle_path = f'C:/Users/una12/Desktop/碩一/整數規劃/project/Input_files/vehicle_info_{scale}.csv'

# data preprocessing
customers = pd.read_csv(customer_path)
first = 0
last = len(customers.index)

customers.loc[len(customers.index)] = customers.loc[0]
customers.loc[len(customers.index) - 1, 'cust no.'] = last
places = customers['cust no.'].to_list()
# distance
xy = [(r[0], r[1], r[2]) for r in customers.itertuples(index=False)]
d = {(i[0], j[0]): (abs(i[1] - j[1])**2 + abs(i[2] - j[2])**2)**(1/2) for i, j in combinations(xy, 2)}
cd = deepcopy(d)
for (i, j), v in cd.items():
    d[(j, i)] = v
# other parameters
s = customers['start time'].to_numpy()
t = customers['due time'].to_numpy()
u = customers['demand'].to_numpy()
w = customers['service time'].to_numpy()

with open(vehicle_path, 'r') as f:
    next(f)
    line = f.readline().split(',')
    vehicles = list(range(int(line[0])))
    vehicle_capacity = int(line[1])
M = 2**50


# model
m = Model(name='ip2023_finalproject')
m.set_time_limit(2969490)

# variables
x = {(i, j, k): m.binary_var(name="x_{0}_{1}_{2}".format(i,j,k)) for i in places for j in places for k in vehicles }
y = {(i, k): m.binary_var(name="y_{0}_{1}".format(i,k)) for i in places for k in vehicles}
print(y)
z = {(i): m.continuous_var(name="z_{0}".format(i)) for i in places}


# objective
m.minimize( m.sum(x[i, j, k] * d[(i, j)] for i in places for j in places for k in vehicles if i != j))


# constraints
m.add_constraints((m.sum(x[i, j, k] for i in places if i != j) - m.sum(x[j, i, k] for i in places if i != j) == 0
                   for j in places for k in vehicles if j != first and j != last))#
m.add_constraints((m.sum(x[first, j, k] for j in places) == 1 for k in vehicles))##
m.add_constraints((m.sum(x[i, last, k] for i in places) == 1 for k in vehicles))##
m.add_constraints((m.sum(y[i, k] for k in vehicles) == 1 for i in places if i != first and i != last))##
m.add_constraints((y[i, k] == 1 for i in places for k in vehicles if i == first and i == last))##
m.add_constraints((m.sum(x[i, j, k] for i in places for k in vehicles) == 1 for j in places if j != first and j != last))#
m.add_constraints((m.sum(x[i, j, k] for j in places for k in vehicles) == 1 for i in places if i != first and i != last))#
m.add_constraints((m.sum(x[i, j, k] for i in places) - y[j, k] <= 0 for j in places for k in vehicles if j != first and j != last))#
m.add_constraints((m.sum(x[i, j, k] for j in places) - y[i, k] <= 0 for i in places for k in vehicles if i != first and i != last))#no
m.add_constraints((m.sum(y[i, k] * u[i] for i in places) - vehicle_capacity <= 0 for k in vehicles))#
m.add_constraints((x[i, j, k]*M + z[i] - z[j] <= M - d[(i, j)] - w[i]
                   for i in places for j in places for k in vehicles if j != i and j != first and i != last))#
m.add_constraints((z[i] - s[i] >= 0 for i in places))#
m.add_constraints((z[i] - t[i] <= 0 for i in places))#
m.add_constraints((x[last, j, k]==0 for j in places for k in vehicles))#

m.add_constraints(x[i,j,k]==0 for i in places for j in places for k in vehicles if i==j)#

m.solve(log_output=True, )

m.print_solution()

x_list= list(m.solution.get_value_dict(x).values())
y_list= list(m.solution.get_value_dict(y).values())
z_list= list(m.solution.get_value_dict(z).values())


xidx1= [_ for _ in range(0,len(x_list),len(vehicles))]
xidx2= [_ for _ in range(1,len(x_list),len(vehicles))]
xidx3= [_ for _ in range(2,len(x_list),len(vehicles))]
k=0
def result(k):
    xidx1= [_ for _ in range(k,len(x_list),len(vehicles))]
    head,tail=[],[]
    for i in range(0, last+1):
        x_idx1= xidx1[i*(last+1):(i+1)*(last+1)]
        for j in range(len(x_idx1)):
            if x_list[x_idx1[j]]==1:
                tail.append(i)
                head.append(j)
    df= pd.DataFrame({"tail": tail, "head": head})
    print(df)
    node_result1= [0]
    a= 0
    print('last',last)
    while a!=last:
        head= df['head'].iloc[df.index[df['tail'] == a]].tolist()
        node_result1.extend(head)
        a= head[0]
        i+=1
    
    print(node_result1)
    dist1=[]
    for i in node_result1:
        dist1.append(z_list[i])
    print(dist1)
    return node_result1, dist1  
content=[]
for k in range(len(vehicles)):
    number= ['vehicle'+str(k)+':']
    node_result, dist=result(k)
    dist= [round(i,2) for i in dist]
    content.append(number)
    content.append(node_result)
    content.append(dist)

obj= round(m.solution.get_objective_value(),4)
time=m.get_solve_details().time
content.append(['objective value','time used'])
content.append([obj,time])
#content=[['vehicle1:'],node_result1, dist1,['vehicle2:'],node_result2, dist2,['vehicle3:'],node_result3, dist3,['objective value','time used'],[obj,time]]
with open('C:/Users/una12/Desktop/碩一/整數規劃/project/Team1_output_'+scale+'.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(content)