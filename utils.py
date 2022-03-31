from hashlib import sha256
from os import urandom
from base64 import b64decode, b64encode
from rich.progress import track, Progress
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy


def R(s: bytes, salt: int = None) -> bytes:

    start = 0
    while start < 30:
        _s = s[start: start+6]
        start += 6
        if salt is not None:
            _s = int.from_bytes(_s, 'little')
            _s = (_s ^ salt).to_bytes(6, 'little')
        _s = b64encode(_s)[:6]
        if _s.count(b'/') or _s[1:].count(b'+'):
            continue
        if _s[0] == 43:
            return _s[1:]
        return _s

    start = 0
    r = bytearray()
    while start < 30:
        _s = s[start: start+6]
        start += 6
        if salt is not None:
            _s = int.from_bytes(_s, 'little')
            _s = (_s ^ salt).to_bytes(6, 'little')
        for ch in b64encode(_s).replace(b'/', b''):
            if len(r) == 0 or ch != 43:
                r.append(ch)
        if len(r) >= 6:
            break
    else:
        if r[0] == 43:
            return bytes(r[1:]).ljust(5, b'A')
        return bytes(r).ljust(6, b'A')
    if r[0] == 43:
        return bytes(r[1:6])
    return bytes(r[:6])


def T(s: bytes) -> bytes:
    if len(s) in [3, 5]:
        s += b'+'
    if len(s) == 4:
        return b64decode(s)
    s += b'AA'
    return b64decode(s)[:5]


def revT(s: bytes) -> bytes:
    s = b64encode(s)
    if len(s) == 4:
        if s[-1] == 43:
            return s[:-1]
        return s
    if s[5] == 43:
        return s[:5]
    return s[:6]


if __name__ == '__main__':
    c = {}
    salt = int.from_bytes(b'\xdf\x1dLl\xce\xba', 'little')
    for _ in track(range(1000000)):
        s = urandom(32)
        t = R(s)
        _t = R(s, salt)
        if _t in c.keys():
            print(s, c[_t])
            break
        c[t] = s
        # print(s, T(s), revT(T(s)))
        # assert revT(T(s)) == s
        # assert revT(T(s[2:])) == s[2:]

    # print(b64encode(b'\xdf\x1dLl\xce\xba\xe3\x89I\xc62!eY:s\xdb\xf8I\xe2o\x08\xafD*\x18\xc4\x96\x84<\x19:'))
    # print(b64encode(b'\xdf\x1dLl\xc3\\\x01\x13\xdeWU\xcb\xbd\x1aJ\xd9{\x96\x1d/\x9c\x7f\x14\xc2\x120Y\xa5M\xc8c\x99'))
