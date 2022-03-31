import os
from math import log2, log
from math import e as EXP
from multiprocessing import Pool
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.resource_tracker import unregister
from utils import R


class BloomFilter:
    def __init__(self, name: str, N: int, epi: float = 0.001, smm=None, smn: str = None) -> None:
        self.name = name
        self.filename = f'mmap/{name}'
        self.N = N
        self.M = round(self.N * log2(1 / epi) * log2(EXP))
        self.S = (self.M // 8 // 1024 + 1) * 1024
        assert self.M <= 8 * 1024 * 1024 * 1024 * 8  # 8GB
        self.K = round(log(2) * self.M / self.N)
        print('BloomFilter', self.N, self.M, self.K, self.S)

        self.mem_init = smm is None and smn is None
        self.mem_copy = smn is not None
        if self.mem_init:
            self.share_mem = SharedMemory(create=True, size=self.S)
        elif self.mem_copy:
            self.share_mem = SharedMemory(name=smn)
        else:
            self.share_mem = smm.SharedMemory(size=self.S)
        self.mem = self.share_mem.buf

        def __R(x: int, p: int) -> int:
            return (x ^ p) % self.M
        self.R = [lambda s, p=int.from_bytes(os.urandom(8), 'little'): __R(s, p)
                  for _ in range(self.K)]

    def __del__(self):
        self.share_mem.close()
        if self.mem_init:
            self.share_mem.unlink()
        elif self.mem_copy:
            unregister(self.share_mem._name, 'shared_memory')

    def __get(self, pos: int) -> int:
        return (self.mem[pos >> 3] >> (pos & 7)) & 1

    def __set(self, pos: int) -> bool:
        """ return the value before set """
        if self.mem[pos >> 3] & (1 << (pos & 7)):
            return True
        self.mem[pos >> 3] |= (1 << (pos & 7))
        return False

    def get(self, x: int) -> bool:
        for R in self.R:
            if not self.__get(R(x)):
                return False
        return True

    def set(self, x: int) -> bool:
        """ return the value before set """
        ret = True
        for R in self.R:
            ret &= self.__set(R(x))
        return ret

    def get_bytes(self, s: bytes) -> bool:
        return self.get(int.from_bytes(s.rjust(8), 'little'))

    def set_bytes(self, s: bytes) -> bool:
        return self.set(int.from_bytes(s.rjust(8), 'little'))


def test():
    bf = BloomFilter('test', 100000, 0.0001, init=True)
    input = [R(os.urandom(32)) for i in range(100000)]
    for x in input:
        assert not bf.get_bytes(x)
    result = {True: 0, False: 0}
    for x in input:
        result[not bf.set_bytes(x)] += 1
    for x in input:
        assert bf.get_bytes(x)
    print(result)


def task(x):
    return bf.set_bytes(x)


def test_pool():
    global bf
    bf = BloomFilter('test', 638666967, 0.0001, init=True)
    with Pool(30) as pool:
        params = [R(os.urandom(32)) for i in range(30)]
        print([x for x in pool.imap(task, params)])
        params = params[3:] + params[:3]
        print([x for x in pool.imap(task, params)])
        x = R(os.urandom(32))
        params = [x for i in range(30)]
        print([x for x in pool.imap(task, params)])
    del bf


if __name__ == '__main__':
    test()
    test_pool()
