K = 2 ** 13
C = 62 ** 5 + 62 ** 6

with open('plan', 'r') as f:
    plan = [x.strip().split(' ') for x in f.readlines()]
    plan = [(int(x), int(y)) for x, y in plan][::-1]
with open('progress', 'r') as f:
    counter = [int(x.strip()) for x in f.readlines()]

for (x, y), z in zip(plan, counter):
    print(x, y, z, f'{z/y*100:.5}%', sep='\t')

__idx = 0
exp = 0
for i in range(K):
    exp += counter[__idx] * (1 - exp) / C
    if i+1 == plan[__idx][0]:
        __idx += 1
print(exp)


__idx = 0
exp = 0
for i in range(K):
    exp += max(counter[__idx], plan[__idx][1]) * (1 - exp) / C
    if i+1 == plan[__idx][0]:
        __idx += 1
print(exp)