"""Find exact phase-only AND boxes in a final stream, without touching measurements."""
from pathlib import Path
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NONE = 2**32 - 1


def find(track):
    path = ROOT / "agents" / track / "research-output/final.u32"
    ops = np.memmap(path, dtype="<u4", mode="r").reshape(-1, 7)
    kind = ops[:, 0]
    before_depth = np.cumsum((kind == 15).astype(np.int32) - (kind == 16).astype(np.int32))
    before_depth = np.concatenate(([0], before_depth[:-1]))
    writes, reads = {}, {}
    for column, kinds in [(3, [6, 8, 10, 11, 12, 13]), (2, [10])]:
        ix = np.flatnonzero(np.isin(kind, kinds))
        qs = ops[ix, column]
        for q in np.unique(qs):
            writes.setdefault(int(q), []).append(ix[qs == q])
    for column, kinds in [(3, [7, 9, 14]), (2, [8, 9, 10, 13, 14]), (1, [13, 14])]:
        ix = np.flatnonzero(np.isin(kind, kinds))
        qs = ops[ix, column]
        for q in np.unique(qs):
            reads.setdefault(int(q), []).append(ix[qs == q])
    writes = {q: np.sort(np.concatenate(v)) for q, v in writes.items()}
    reads = {q: np.unique(np.concatenate(v)) for q, v in reads.items()}
    candidates = []
    examined = 0
    for p in np.flatnonzero(kind == 13):
        p = int(p)
        o = ops[p]
        a, b, t = map(int, (o[2], o[1], o[3]))
        if o[5] != NONE or before_depth[p] != 0:
            continue
        w = writes[t]
        loc = int(np.searchsorted(w, p))
        if loc + 1 == len(w):
            continue
        previous = int(w[loc - 1]) if loc else -1
        clean = (previous == -1 and t >= 512) or (previous >= 0 and kind[previous] in (11, 12) and ops[previous, 5] == NONE and before_depth[previous] == 0)
        if not clean:
            continue
        e = int(w[loc + 1])
        if e - p > 10000 or before_depth[e] != 0 or ops[e, 5] != NONE:
            continue
        if kind[e] == 13:
            if set(map(int, ops[e, 1:3])) != {a, b}:
                continue
            fix = None
        elif kind[e] == 12:
            fix = None
            cb = int(ops[e, 4])
            for f in range(e + 1, min(e + 17, len(ops))):
                v = ops[f]
                if v[4] == cb:
                    break
                if kind[f] == 9 and set(map(int, (v[2], v[3]))) == {a, b} and v[5] == cb and before_depth[f] == 0:
                    fix = f
                    break
            if fix is None:
                continue
        else:
            continue
        end = fix if fix is not None else e
        if any(np.searchsorted(writes[q], end, side="right") != np.searchsorted(writes[q], p, side="right") for q in (a, b)):
            continue
        ri = reads.get(t, np.array([], dtype=np.int64))
        ri = ri[np.searchsorted(ri, p, side="right"):np.searchsorted(ri, e)]
        if len(ri) > 16 or any(kind[i] not in (7, 9, 14) for i in ri):
            continue
        replacements, added_weight = {}, 0.0
        supported = True
        for i in ri:
            i = int(i)
            v = ops[i].copy()
            operands = [int(v[3])]
            if kind[i] in (9, 14):
                operands.append(int(v[2]))
            if kind[i] == 14:
                operands.append(int(v[1]))
            degree = sorted(({a, b} | set(operands)) - {t})
            if len(degree) > 3:
                supported = False
                break
            v[1:4] = NONE
            if len(degree) == 2:
                v[0] = 9
                v[2], v[3] = degree
            else:
                v[0] = 14
                v[1:4] = degree
                added_weight += 2.0 ** -(int(before_depth[i]) + int(v[5] != NONE))
            replacements[i] = v.tolist()
        if not supported:
            continue
        saving = (2.0 if fix is None else 1.0) - added_weight
        if saving <= 0:
            continue
        examined += 1
        candidates.append({"start": p, "end": end + 1, "compute": p, "erase": e, "fix": fix, "clean_after": previous, "target": t, "controls": [a, b], "replacements": replacements, "expected_saved_T": saving})
    # Keep intervals disjoint, so one removed temporary cannot be another box's input.
    selected, last = [], -1
    for c in sorted(candidates, key=lambda c: c["end"]):
        if c["start"] >= last:
            selected.append(c)
            last = c["end"]
    out = ROOT / "agents" / track / "research-output/phase-boxes.json"
    out.write_text(json.dumps(selected, indent=2) + "\n")
    print(json.dumps({"track": track, "eligible": examined, "disjoint": len(selected), "expected_saved_T": sum(c["expected_saved_T"] for c in selected)}, indent=2), flush=True)


if __name__ == "__main__":
    find(sys.argv[1])
