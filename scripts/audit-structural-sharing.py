"""Exact syntactic opportunities, never sampled-control gate deletion or scoring."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time

spec = importlib.util.spec_from_file_location('wire', Path(__file__).with_name('analyze-wire-lifetimes.py'))
wire = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wire)
NO = wire.NO


def audit(path):
    start = time.monotonic()
    depth = 0
    stack = []
    bit_write = {}
    last_write, last_read = {}, {}
    candidates = {}
    fanout = []
    phase_pairs = []
    phases = {}
    windows = {}
    absorption = []
    end_selected = -1
    fuse_end = -1
    fusion = []
    fuse_candidates = {}
    ccx = ccz = 0
    for i, row in wire.records(path):
        kind, pad, b, a, t, bit, cond, reg = row
        if kind == 15:
            depth += 1
            stack.append(i)
            continue
        if kind == 16:
            depth -= 1
            stack.pop()
            assert depth >= 0
            continue
        unconditional = depth == 0 and cond == NO
        guard = (tuple(stack), cond, bit_write.get(cond, -1))
        if kind in (3, 4, 5, 12):
            bit_write[bit] = i
        if kind == 13:
            ccx += 1
            key = tuple(sorted((a, b)))
            if True:
                key = (key, guard)
                old = candidates.get(key)
                if old:
                    j, u = old
                    if (j > end_selected and u != t and
                            last_write.get(a, -1) < j and last_write.get(b, -1) < j and
                            last_write.get(u, -1) == j and last_read.get(t, -1) < j):
                        fanout.append(dict(first=j, second=i, controls=key, donor=u, target=t))
                        end_selected = i
                candidates[key] = (i, t)
                for shared, other in ((a, b), (b, a)):
                    fk = (shared, t, guard)
                    old = fuse_candidates.get(fk)
                    if old:
                        j, u = old
                        if (j > fuse_end and u != other and
                                last_write.get(shared, -1) < j and last_write.get(u, -1) < j and
                                last_read.get(t, -1) < j):
                            fusion.append(dict(first=j, second=i, shared=shared, old_other=u,
                                               new_other=other, target=t, guard=guard))
                            fuse_end = i
                    fuse_candidates[fk] = (i, other)
        if kind == 14:
            ccz += 1
            if unconditional:
                qs = sorted((a, b, t))
                for k in range(3):
                    key = tuple(qs[v] for v in range(3) if v != k)
                    old = phases.get(key)
                    if old:
                        j, u = old
                        if all(last_write.get(q, -1) < j for q in (*key, u, qs[k])):
                            phase_pairs.append(dict(first=j, second=i, controls=key, thirds=[u, qs[k]]))
                    phases[key] = (i, qs[k])
        reads, writes = [], []
        if kind in (6, 8, 13):
            reads = ([a] if kind in (8, 13) else []) + ([b] if kind == 13 else [])
            writes = [t]
        elif kind in (7, 9, 14):
            reads = [t] + ([a] if kind in (9, 14) else []) + ([b] if kind == 14 else [])
        elif kind == 10:
            reads = writes = [a, t]
        elif kind in (11, 12):
            reads = writes = [t]
            w = windows.get(t)
            if kind == 12 and unconditional and w and w['ccx']:
                absorption.append(dict(measurement=i, target=t, **w))
        elif kind in (2, 17):
            reads = [q for q in (a, b, t) if q != NO]
        for q in reads:
            last_read[q] = i
            windows.pop(q, None)
        for q in writes:
            last_write[q] = i
        if kind in (6, 8, 13):
            w = windows.setdefault(t, dict(first=i, first_depth=depth, first_condition=cond,
                                          ccx=0, conditional_writes=0, writes=0))
            w['ccx'] += kind == 13
            w['writes'] += 1
            w['conditional_writes'] += not unconditional
    assert depth == 0
    return dict(scope='Structural opportunities only; no transformation, score or whole-point correctness claim',
                stream=str(path), stream_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                operations=i+1, emitted_ccx=ccx, emitted_ccz=ccz,
                greedy_disjoint_same_guard_fanout=fanout,
                greedy_disjoint_same_guard_control_fusion=fusion,
                unconditional_phase_pair_opportunities=phase_pairs,
                measurement_absorption_windows=absorption,
                elapsed_seconds=time.monotonic()-start)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stream', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    result = audit(a.stream)
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: len(v) if isinstance(v, list) else v for k, v in result.items()}, indent=2))
