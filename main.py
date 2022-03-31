from itertools import count
from timeit import Timer
from hashlib import sha256
from os import urandom
from typing import final
from rich.progress import track, Progress
from copy import deepcopy
from bloom_filter import BloomFilter
from utils import R, T, revT
from multiprocessing import Lock, Pool


K = 2 ** 13
PERROUND = 1000
LAYERS = 15


with open('plan', 'r') as f:
    plan = [x.strip().split(' ') for x in f.readlines()]
    plan = [(int(x), int(y)) for x, y in plan][::-1]
with open('progress', 'r') as f:
    counter = [int(x.strip()) for x in f.readlines()]
with open('shared_mem', 'r') as f:
    shared_mem = [x.strip() for x in f.readlines()]
assert len(plan) == LAYERS


try:
    with open('salt', 'rb') as f:
        salt_raw = f.read(6 * K)
    assert len(salt_raw) == 6 * K
except Exception:
    salt_raw = urandom(6 * K)
    with open('salt', 'wb') as f:
        f.write(salt_raw)
salt = [int.from_bytes(salt_raw[i: i+6], 'little') for i in range(0, 6 * K, 6)]


def task(num: int):
    c = {}
    counter = [0 for _ in range(LAYERS)]
    for _ in range(num):
        while True:
            start = now = R(urandom(32))
            __idx = 0
            __now = None
            for i in range(K):
                now = R(sha256(now).digest(), salt[i])
                if i+1 == plan[__idx][0]:
                    if bf[__idx].set_bytes(now):
                        break
                    __now = now
                    __idx += 1
            if __idx == 0:
                continue
            counter[__idx - 1] += 1
            key = (__idx - 1, __now[:2])
            if key in c.keys():
                c[key].append((start, __now[2:]))
            else:
                c[key] = [(start, __now[2:])]
            break

    for __idx, k in c.keys():
        with open(f'data/{plan[__idx][0]}/{k.decode()}', 'ab') as f:
            for start, now in c[(__idx, k)]:
                f.write(T(start)+T(now))
    for i in range(LAYERS-1, 0, -1):
        counter[i-1] += counter[i]
    return counter


def main():
    global bf
    bf = [BloomFilter(str(x), y, epi=0.00001, smn=z)
          for (x, y), z in zip(plan, shared_mem)]
    with Progress() as progress:
        task_ids = [progress.add_task(f'Layer: {x:4}', total=y, completed=c)
                    for (x, y), c in zip(plan, counter)]
        with Pool(30) as pool:
            try:
                while True:
                    params = [PERROUND for _ in range(1000)]
                    for result in pool.imap_unordered(task, params):
                        for t, r in zip(task_ids, result):
                            progress.update(t, advance=r)
                        with open('progress', 'w') as f:
                            for i in range(LAYERS):
                                counter[i] += result[i]
                                f.write(str(counter[i])+'\n')
                    for i in range(LAYERS):
                        if counter[i] < plan[i][1]:
                            break
                    else:
                        break
            except KeyboardInterrupt:
                pass


if __name__ == '__main__':
    main()
