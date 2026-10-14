"""Conservative constant propagation for proof premises; never changes gates."""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research-output/parallel-20261014"
NONE = 2**32 - 1
UNKNOWN = -1


def conjunction(a, b):
    return 0 if a == 0 or b == 0 else 1 if a == b == 1 else UNKNOWN


def exclusive(a, b):
    return UNKNOWN if a == UNKNOWN or b == UNKNOWN else a ^ b


def census():
    ops = np.memmap(ROOT / "agents/product/research-output/pre-extra-guards.u32", dtype="<u4", mode="r").reshape(-1, 7)
    targets = {r["start"] for r in json.loads((OUT / "proof-candidates.json").read_text())}
    q, b = [0] * 1300, [0] * 70000
    base, stack, result = 1, [], {}
    for index, row in enumerate(ops[:max(targets) + 1]):
        if index in targets:
            result[str(index)] = {
                "q": {str(i): v for i, v in enumerate(q) if v != UNKNOWN},
                "b": {str(i): v for i, v in enumerate(b[:20000]) if v != UNKNOWN},
                "base": base,
                "stack": stack.copy(),
            }
        kind, c2, c1, t, ct, cc, reg = map(int, row)
        cond = base if cc == NONE else conjunction(base, b[cc])
        if kind == 15:
            stack.append(base)
            base = cond
        elif kind == 16:
            base = stack.pop()
        elif kind == 2 and reg < 4:
            if t != NONE:
                q[t] = UNKNOWN
            else:
                b[ct] = UNKNOWN
        elif kind in (6, 8, 13):
            v = cond
            if kind != 6:
                v = conjunction(v, q[c1])
            if kind == 13:
                v = conjunction(v, q[c2])
            q[t] = exclusive(q[t], v)
        elif kind == 10:
            if cond == 1:
                q[c1], q[t] = q[t], q[c1]
            elif cond == UNKNOWN and q[c1] != q[t]:
                q[c1] = q[t] = UNKNOWN
        elif kind in (11, 12):
            if cond == 1:
                q[t] = 0
            elif cond == UNKNOWN and q[t] != 0:
                q[t] = UNKNOWN
            if kind == 12 and cond != 0:
                b[ct] = UNKNOWN
        elif kind == 3:
            b[ct] = exclusive(b[ct], cond)
        elif kind in (4, 5):
            value = kind - 4
            if cond == 1:
                b[ct] = value
            elif cond == UNKNOWN and b[ct] != value:
                b[ct] = UNKNOWN
    (OUT / "known-prefix.json").write_text(json.dumps(result) + "\n")
    print(json.dumps({k: {"known_q": len(v["q"]), "known_b": len(v["b"]), "depth": len(v["stack"])} for k, v in result.items()}))


if __name__ == "__main__":
    census()
