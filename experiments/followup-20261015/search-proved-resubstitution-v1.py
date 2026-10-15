"""Propose with independent signatures; admit ONLY bounded-cone Boolean UNSAT.

No curve packets or stream-hash seeds are used. Forgotten cone nodes are fresh
unconstrained boundary variables, so proofs apply to a superset of reachability.
The pass leaves measurements and phase operations untouched. No scorer.
"""
import argparse
from collections import defaultdict, deque, Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import time
import z3

spec = importlib.util.spec_from_file_location('wire', Path(__file__).with_name('analyze-wire-lifetimes.py'))
wire = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wire)
NO = wire.NO
MASK = (1 << 256) - 1


class Cone:
    def __init__(self, cap=60000):
        self.nodes = {}
        self.order = deque()
        self.serial = 0
        self.cap = cap
        self.rng = random.Random('ecdsa-exact-resubstitution-20261015-v1')

    def fresh(self):
        self.serial += 2
        return self.serial, self.rng.getrandbits(256)

    def neg(self, a):
        return a[0] ^ 1, a[1] ^ MASK

    def make(self, kind, a, b):
        if kind == 'and':
            if a[0] == 0 or b[0] == 0 or a[0] == (b[0] ^ 1): return (0, 0)
            if a[0] == 1: return b
            if b[0] == 1 or a[0] == b[0]: return a
            sig = a[1] & b[1]
        else:
            if a[0] == 0: return b
            if b[0] == 0: return a
            if a[0] == b[0]: return (0, 0)
            if a[0] == (b[0] ^ 1): return (1, MASK)
            if a[0] == 1: return self.neg(b)
            if b[0] == 1: return self.neg(a)
            sig = a[1] ^ b[1]
        self.serial += 2
        self.nodes[self.serial] = (kind, a[0], b[0])
        self.order.append(self.serial)
        if len(self.order) > self.cap:
            del self.nodes[self.order.popleft()]
        return self.serial, sig

    def prove_zero(self, root, max_nodes=5000):
        if root == 0: return 'unsat', [], 0
        todo, seen, equations = [root & ~1], set(), []
        while todo:
            u = todo.pop()
            if not u or u in seen: continue
            seen.add(u)
            if len(seen) > max_nodes: return 'cone_limit', [], len(seen)
            n = self.nodes.get(u)
            if n:
                equations.append([u, *n])
                todo.extend((n[1] & ~1, n[2] & ~1))
        symbols = {u: z3.Bool('n'+str(u)) for u in seen}
        def lit(u):
            if u < 2: return z3.BoolVal(bool(u))
            v = symbols[u & ~1]
            return z3.Not(v) if u & 1 else v
        s = z3.Solver()
        s.set(timeout=150)
        for u, kind, a, b in equations:
            s.add(symbols[u] == (z3.And(lit(a), lit(b)) if kind == 'and' else z3.Xor(lit(a), lit(b))))
        s.add(lit(root))
        answer = str(s.check())
        return answer, equations if answer == 'unsat' else [], len(seen)


def search(path, out):
    began = time.monotonic()
    nq = nb = 0
    abi_q, abi_b = set(), set()
    for _, row in wire.records(path):
        _, _, b, a, t, bt, c, _ = row
        nq = max([nq] + [v+1 for v in (a,b,t) if v != NO])
        nb = max([nb] + [v+1 for v in (bt,c) if v != NO])
        if row[0] == 2:
            if t != NO: abi_q.add(t)
            if bt != NO: abi_b.add(bt)
    g = Cone()
    zero, one = (0,0), (1,MASK)
    q = [g.fresh() if i in abi_q else zero for i in range(nq)]
    bits = [g.fresh() if i in abi_b else zero for i in range(nb)]
    index = defaultdict(set)
    for i, v in enumerate(q): index[v[1]].add(i)
    def setq(i, v):
        index[q[i][1]].remove(i)
        if not index[q[i][1]]: del index[q[i][1]]
        q[i] = v
        index[v[1]].add(i)
    base, stack = one, []
    counts = Counter()
    hits = []
    out.mkdir(parents=True, exist_ok=True)
    trace = (out/'queries.jsonl').open('w')
    for at, row in wire.records(path):
        k, _, b, a, t, bt, c, _ = row
        guard = base if c == NO else g.make('and', base, bits[c])
        if k == 15:
            stack.append(base); base = guard
        elif k == 16:
            base = stack.pop()
        elif k in (6,8,13):
            product = one if k == 6 else q[a] if k == 8 else g.make('and', q[a], q[b])
            if k == 13:
                counts['ccx'] += 1
                proposals = []
                if product[1] == 0: proposals.append(('drop', -1, False, zero))
                if product[1] == MASK: proposals.append(('x', -1, False, one))
                for complement in (False, True):
                    sig = product[1] ^ (MASK if complement else 0)
                    # Trivial zero holders do not multiply the same query.
                    for witness in sorted(index.get(sig, ())):
                        if witness != t:
                            proposals.append(('cx', witness, complement, g.neg(q[witness]) if complement else q[witness]))
                            break
                # Guarded control implication is a different exact contract.
                if guard[1].bit_count() >= 16:
                    v = product[1] & guard[1]
                    for name, w, replacement in [('drop',-1,zero),('cx',a,q[a]),('cx',b,q[b])]:
                        if replacement[1] & guard[1] == v and not any(p[:3] == (name,w,False) for p in proposals):
                            proposals.append((name,w,False,replacement))
                for name, witness, complement, replacement in proposals:
                    delta = g.make('and', guard, g.make('xor', product, replacement))
                    if delta[1]: continue
                    answer, equations, size = g.prove_zero(delta[0])
                    counts[answer] += 1
                    query = dict(op=at, kind=name, witness=witness, complement=complement,
                                 status=answer, cone_nodes=size)
                    trace.write(json.dumps(query)+'\n')
                    if answer == 'unsat':
                        hit = dict(**query, original=list(row), root=delta[0], equations=equations,
                                   guard=guard[0], product=product[0], replacement=replacement[0], depth=len(stack))
                        hits.append(hit)
                        print('PROVED', at, name, witness, complement, size, flush=True)
                        break
            setq(t, g.make('xor', q[t], g.make('and', guard, product)))
        elif k == 10:
            v = g.make('and', guard, g.make('xor', q[t], q[a]))
            qa, qt = g.make('xor', q[a], v), g.make('xor', q[t], v)
            setq(a, qa); setq(t, qt)
        elif k in (11,12):
            setq(t, g.make('and', q[t], g.neg(guard)))
            if k == 12:
                bits[bt] = g.make('xor', bits[bt], g.make('and', guard, g.make('xor', bits[bt], g.fresh())))
        elif k == 3:
            bits[bt] = g.make('xor', bits[bt], guard)
        elif k in (4,5):
            bits[bt] = g.make('xor', bits[bt], g.make('and', guard, g.make('xor', bits[bt], one if k == 5 else zero)))
        if at and at % 1_000_000 == 0:
            print('PROGRESS', at, dict(counts), round(time.monotonic()-began,1), flush=True)
    trace.close()
    assert not stack
    result = dict(status='proof-backed rewrite leads; not a scored circuit', stream_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  input_stream=str(path), operations=at+1, counts=dict(counts), hits=hits,
                  solver=z3.get_version_string(), cone_node_cap=5000, retained_node_cap=g.cap,
                  elapsed_seconds=time.monotonic()-began)
    (out/'proofs.json').write_text(json.dumps(result, indent=2)+'\n')
    print('FINISHED',dict(counts),flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stream', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    search(a.stream, a.output)
