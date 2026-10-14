"""Conservative arbitrary-input Boolean value identities; diagnostic only.

Immutable atoms represent inputs, measurements, nonlinear expressions, or
forgotten expressions. Clearing the expression cache only loses correlations.
All classical guard snapshots remain immutable. No sampled values are used.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time

spec = importlib.util.spec_from_file_location('stream', Path(__file__).with_name('analyze-wire-lifetimes.py'))
stream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stream)
NO = stream.NO
ZERO = (0, frozenset())
ONE = (1, frozenset())

class Values:
    def __init__(self, qubits=(), bits=(), term_cap=128, cache_cap=100_000):
        self.atom = 0
        self.cache = {}
        self.term_cap, self.cache_cap = term_cap, cache_cap
        self.forgotten = self.cache_resets = 0
        self.q = {q: self.fresh() for q in qubits}
        self.bits = {b: self.fresh() for b in bits}
        self.base, self.stack = ONE, []

    def fresh(self):
        self.atom += 1
        return (0, frozenset((self.atom,)))

    def named(self, key):
        if key in self.cache:
            return self.cache[key]
        if len(self.cache) >= self.cache_cap:
            self.cache.clear()
            self.cache_resets += 1
        value = self.fresh()
        self.cache[key] = value
        return value

    def xor(self, a, b):
        value = (a[0] ^ b[0], a[1] ^ b[1])
        if len(value[1]) <= self.term_cap:
            return value
        self.forgotten += 1
        return self.named(('xor_forget', value))

    def inverse(self, a):
        return (a[0] ^ 1, a[1])

    def and_(self, a, b):
        if a == ZERO or b == ZERO: return ZERO
        if a == ONE: return b
        if b == ONE or a == b: return a
        if a == self.inverse(b): return ZERO
        return self.named(('and', frozenset((a, b))))

    def guard(self, row):
        return self.base if row[6] == NO else self.and_(self.base, self.bits.get(row[6], ZERO))

    def identity(self, row):
        kind, _, c2, c1, target, _, _, _ = row
        if kind not in (7,8,9,13,14): return None
        controls = (target,) if kind == 7 else (c1,) if kind == 8 else (c1,target) if kind == 9 else (c1,c2) if kind == 13 else (c1,c2,target)
        term = self.guard(row)
        for control in controls: term = self.and_(term, self.q.get(control, ZERO))
        if term == ZERO: return 'zero_guarded_product'
        if kind == 13:
            a, b = (self.q.get(q, ZERO) for q in (c1,c2))
            if a == b: return 'equal_quantum_controls'
            if a == ONE or b == ONE: return 'constant_one_control'
        return None

    def step(self, row):
        kind, pad, c2, c1, target, bit, condition, register = row
        assert pad == 0 and 0 <= kind <= 17
        guard = self.guard(row)
        old = self.q.get(target, ZERO)
        if kind == 15:
            self.stack.append(self.base)
            self.base = self.and_(self.base, self.bits.get(condition, ZERO))
        elif kind == 16:
            self.base = self.stack.pop()
        elif kind in (6,8,13):
            term = guard
            for control in ((c1,) if kind == 8 else (c1,c2) if kind == 13 else ()):
                term = self.and_(term, self.q.get(control,ZERO))
            self.q[target] = self.xor(old,term)
        elif kind == 10:
            other = self.q.get(c1,ZERO)
            change = self.and_(guard,self.xor(old,other))
            self.q[target],self.q[c1] = self.xor(old,change),self.xor(other,change)
        elif kind in (11,12):
            self.q[target] = self.and_(old,self.inverse(guard))
            if kind == 12:
                before = self.bits.get(bit,ZERO)
                self.bits[bit] = self.xor(before,self.and_(guard,self.xor(before,self.fresh())))
        elif kind == 3:
            self.bits[bit] = self.xor(self.bits.get(bit,ZERO),guard)
        elif kind in (4,5):
            before = self.bits.get(bit,ZERO)
            value = ONE if kind == 5 else ZERO
            self.bits[bit] = self.xor(before,self.and_(guard,self.xor(before,value)))

def analyze(path):
    began = time.monotonic()
    locked, classical = set(),set()
    for _, row in stream.records(path):
        if row[0] == 2: locked.update(q for q in row[2:5] if q != NO)
        if row[0] == 1: classical.add(row[5])
    state = Values(locked,classical)
    counts, examples = {},[]
    ccx = 0
    for index,row in stream.records(path):
        identity = state.identity(row)
        if row[0] == 13: ccx += 1
        if identity:
            key = str(row[0]) + ':' + identity
            counts[key] = counts.get(key,0)+1
            if row[0] == 13 and len(examples)<200:
                examples.append({'index':index,'row':row,'identity':identity})
        state.step(row)
    assert not state.stack
    return {'scope':'Exact arbitrary-input Boolean identities under conservative immutable expression abstraction; no transformed circuit or scored savings',
            'stream_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'operations':index+1,'emitted_ccx':ccx,'identities':counts,'ccx_examples':examples,
            'atoms':state.atom,'forgotten_expressions':state.forgotten,'cache_resets':state.cache_resets,
            'term_cap':state.term_cap,'cache_cap':state.cache_cap,'seconds':time.monotonic()-began}

if __name__ == '__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('stream',type=Path); a.add_argument('output',type=Path)
    args=a.parse_args()
    result=analyze(args.stream)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='ccx_examples'}))
