from multiprocessing.managers import SharedMemoryManager
from bloom_filter import BloomFilter
from time import sleep


with open('plan', 'r') as f:
    plan = [x.strip().split(' ') for x in f.readlines()]
    plan = [(int(x), int(y)) for x, y in plan][::-1]


with open('progress', 'w') as f:
    f.write('\n'.join(['0' for _ in plan]))


with SharedMemoryManager() as smm:
    bf = [BloomFilter(str(x), y, epi=0.00001, smm=smm) for x, y in plan]
    bf_buf_name = [x.share_mem.name for x in bf]
    with open('shared_mem', 'w') as f:
        f.write('\n'.join(bf_buf_name))
    try:
        while True:
            sleep(3600)
    except KeyboardInterrupt:
        pass
