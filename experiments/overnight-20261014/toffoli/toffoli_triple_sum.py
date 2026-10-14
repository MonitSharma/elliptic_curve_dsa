"""Bound fused low-sum/triple interfaces without assuming retained sums are free."""
import json
from pathlib import Path
import importlib.util

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("ctor", HERE / "toffoli_constructor.py")
ctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctor)


def rank(xs):
    return ctor.fc.rank(xs)


def main():
    n = 64
    raw = [(1 << n) - 1] + [sum((r >> i & 1) << r for r in range(n)) for i in range(6)]
    sums = [sum((((r & 7) + (r >> 3)) >> i & 1) << r for r in range(n)) for i in range(4)]
    triple = [sum(((3 * ((r & 7) + (r >> 3))) >> i & 1) << r for r in range(n)) for i in range(6)]
    results = []
    for name, targets in [("triple-only", triple), ("triple-and-low-two-sum-bits", triple + sums[:2]),
                          ("triple-and-full-sum", triple + sums)]:
        results.append({"interface": name, "AND_rank_bound": rank(raw + targets) - rank(raw),
                        "cases": n, "input_count": 6, "output_count": len(targets)})
    payload = {"interfaces": results, "limits": "Value-only bounds; full constructor consumes signed upper sum and cleanup controls."}
    HERE.joinpath("triple-sum-analysis.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
