import pandas as pd
from collections import namedtuple
from copy import deepcopy
from itertools import combinations
from random import choice, shuffle, random
from itertools import zip_longest


scale = '25'
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
d[(0, 0)] = 0
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


def new_sol(old=None, new=None, go=None):
    sol = [[] for _ in vehicles]
    if old is None:
        for i in range(1, last):
            sol[choice(vehicles)].append(i)
        for i in sol:
            shuffle(i)
        return sol

    places_set = set(range(1, last))
    for n, (i, j) in enumerate(zip(old, new)):
        for k, l in zip_longest(i, j):
            sol[n].append(choice([k, l]))
        while None in sol[n]:
            sol[n].remove(None)
    csol = deepcopy(sol)
    for i, v in enumerate(csol):
        for j in v:
            if j not in places_set:
                sol[i].remove(j)
            if j in places_set:
                places_set.remove(j)
    for i in places_set:
        sol[choice(vehicles)].append(i)
    csol = deepcopy(sol)
    for i, v in enumerate(csol):
        for j in v:
            if random() < 0.03 or j in go:
                w = choice(vehicles)
                
                try:
                    sol[w].insert(choice(list(range(len(sol[w])))), j)
                except IndexError:
                    sol[w].append(j)
                sol[i].remove(j)

    return sol


def search():
    new = [new_sol() for _ in range(100)]
    pop = [(i, observe(i)) for i in new]
    pop.sort(key=lambda x: x[1])
    it = 0
    while it < 1000:
        new = [new_sol(pop[0][0], choice(pop)[0], pop[0][1][1]) for _ in range(20)]
        pop.extend([(i, observe(i)) for i in new])
        
        # new = [new_sol() for _ in range(10)]
        # pop.extend([(i, observe(i)) for i in new])
        pop.sort(key=lambda x: x[1][0])
        pop = pop[:10]
        
        it += 1
        if it % 100 == 0:
            print(f'Iteration:{it:9_} result:{pop[0][1][0]:9.2f}')
    return pop[0]


def observe(sol):
    travelled = 0
    penalty = 0
    wrong = []
    for i in sol:
        capacity = 200
        pos = 0
        time = 0
        for j in i:
            travelled += d[(pos, j)]
            capacity -= u[j]
            time += d[(pos, j)]
            if time < s[j]:
                time = s[j]
            if time > t[j]:
                penalty += (time - t[j]) * 100
                wrong.append(j)
            time += w[j]
            pos = j
        travelled += d[(pos, 0)]
        if time > t[0]:
            penalty += (time - t[0]) * 100
        if capacity < 0:
            penalty += -capacity * 200

    return travelled + penalty, wrong


def main():
    sol, v = search()
    print(v)
    for i in sol:
        print(i)
    # n = new_sol()
    # print(observe(n))

    return


if __name__ == '__main__':
    main()

