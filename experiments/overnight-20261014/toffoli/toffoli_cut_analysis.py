"""Source-guided cut bounds for joint constructor resynthesis."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("ctor", HERE / "toffoli_constructor.py")
ctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctor)


def main():
    model, targets = ctor.constructor()
    def mask(value):
        answer = 0
        while value:
            v, m = model.pivots[value.bit_length() - 1]
            value ^= v
            answer ^= m
        return answer
    operands = [(mask(a), mask(b)) for _, a, b, _ in model.gates]
    out = [mask(v) for v in targets]
    cuts = []
    for i in range(len(operands)):
        for j in range(i + 2, len(operands) + 1):
            pmask = ((1 << (j-i)) - 1) << (i + 15)
            boundary = [x & pmask for pair in operands[j:] for x in pair] + [x & pmask for x in out]
            required = ctor.fc.rank(boundary)
            if required < j - i:
                cuts.append({"first": model.gates[i][0], "last": model.gates[j-1][0],
                             "AND_count": j-i, "boundary_span_dimension": required,
                             "gap": j-i-required})
    cuts.sort(key=lambda x: (x["AND_count"], -x["gap"]))
    bundles = []
    for cut in cuts[:20]:
        i = model.names.index(cut["first"]) - 15
        j = model.names.index(cut["last"]) - 14
        pmask = ((1 << (j-i)) - 1) << (i + 15)
        def value(m):
            return ctor.fc.combination(m, model.vals)
        external = [ctor.ONE] + [value(x & ~pmask) for pair in operands[i:j] for x in pair]
        piv = {}
        independent = []
        for v in external:
            reduced = v
            while reduced and (b := reduced.bit_length()-1) in piv:
                reduced ^= piv[b]
            if reduced:
                piv[reduced.bit_length()-1] = reduced
                independent.append(v)
        boundary = [x & pmask for pair in operands[j:] for x in pair] + [x & pmask for x in out]
        target_masks = []
        tp = {}
        for m in boundary:
            reduced = m
            while reduced and (b := reduced.bit_length()-1) in tp:
                reduced ^= tp[b]
            if reduced:
                tp[reduced.bit_length()-1] = reduced
                target_masks.append(m)
        bundles.append({"cut": cut, "input_rank_including_constant": len(independent),
                        "input_columns_hex": [hex(v) for v in independent],
                        "target_columns_hex": [hex(value(m)) for m in target_masks],
                        "target_masks": target_masks})
    ctor.ROOT.joinpath("research-output/overnight-20261014/toffoli/cut-targets.json").write_text(json.dumps(bundles) + "\n")
    result = {"cuts_with_value_rank_gap": cuts, "status": "Synthesis leads; cleanup/phase may require additional directions."}
    HERE.joinpath("cut-analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"smallest_cuts": cuts[:20], "count": len(cuts)}, indent=2))


if __name__ == "__main__":
    main()
