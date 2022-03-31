from hashlib import sha256
from os import urandom
from base64 import b64decode, b64encode
from rich.progress import track, Progress
from copy import deepcopy
from utils import R, T, revT
from multiprocessing import Pool


K = 2 ** 13
LAYER = 15


with open('plan', 'r') as f:
    plan = [x.strip().split(' ') for x in f.readlines()]
    plan = [(int(x), int(y)) for x, y in plan][::-1]
rev_plan = {}
for idx, x in enumerate(plan):
    rev_plan[x[0]] = idx


with open('salt', 'rb') as f:
    salt_raw = f.read(6 * K)
assert len(salt_raw) == 6 * K
salt = [int.from_bytes(salt_raw[i: i+6], 'little') for i in range(0, 6 * K, 6)]


def get_table(layer: int, k: bytes):
    try:
        with open(f'data/{plan[layer][0]}/{k.decode()}', 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        return []
    table = []
    for i in range(0, len(data), 8):
        table += [(revT(data[i: i+5]), revT(data[i+5: i+8]))]
    return table


def crack(s: bytes):
    assert len(s) == 32
    for i in track(range(K, 0, -1)):
        _s = R(s, salt[i-1])
        for j in range(i, K):
            if rev_plan.get(j) is not None:
                table = get_table(rev_plan.get(j), _s[:2])
                for start, now in table:
                    if now == _s[2:]:
                        now = start
                        for k in range(i-1):
                            now = R(sha256(now).digest(), salt[k])
                        if sha256(now).digest() == s:
                            print('Found:', now)
                            return now
            _s = R(sha256(_s).digest(), salt[j])
        table = get_table(rev_plan.get(K), _s[:2])
        for start, now in table:
            if now == _s[2:]:
                now = start
                for k in range(i-1):
                    now = R(sha256(now).digest(), salt[k])
                if sha256(now).digest() == s:
                    print('Found:', now)
                    return now
    print('Crack Failed.')


def crack_no_progress(s: bytes):
    assert len(s) == 32
    for i in range(K, 0, -1):
        _s = R(s, salt[i-1])
        for j in range(i, K):
            if rev_plan.get(j) is not None:
                table = get_table(rev_plan.get(j), _s[:2])
                for start, now in table:
                    if now == _s[2:]:
                        now = start
                        for k in range(i-1):
                            now = R(sha256(now).digest(), salt[k])
                        if sha256(now).digest() == s:
                            return True
            _s = R(sha256(_s).digest(), salt[j])
        table = get_table(rev_plan.get(K), _s[:2])
        for start, now in table:
            if now == _s[2:]:
                now = start
                for k in range(i-1):
                    now = R(sha256(now).digest(), salt[k])
                if sha256(now).digest() == s:
                    return True
    return False


if __name__ == '__main__':
    # print(crack(bytes.fromhex('81c31c70e41a7b091e3145c24dd72cf96caf1ca857920921b6dfe23d3c4a0ffc')))
    input = [sha256(R(urandom(32))).digest() for _ in range(100000)]
    with Progress() as progress:
        c = {True: 0, False: 0}
        task_id = progress.add_task(
            total=len(input), description=f'Working... SUCC/FAIL={c[True]}/{c[False]}')
        with Pool(32) as pool:
            try:
                for result in pool.imap_unordered(crack_no_progress, input):
                    c[result] += 1
                    progress.update(
                        task_id, advance=1, description=f'Working... SUCC/FAIL={c[True]}/{c[False]}')
            except KeyboardInterrupt:
                pass
