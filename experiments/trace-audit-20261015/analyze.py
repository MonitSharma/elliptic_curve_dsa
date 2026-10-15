"""Family-aware audit of complete value-trace logs; diagnostic only, score=None.

Reject incomplete logs instead of treating missing events as successful coverage.
No-event cases mean only no observed violation, not a proved fault location.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re

P = 2**256 - 2**32 - 977
EVENT = re.compile(r"\s*EVENT family=(\S+) shot=(\d+) at=(\d+) (\S+) (.*)")
TRACE = re.compile(r"TRACE family=(\S+) shot=(\d+) final_bad=(true|false) x_bad=(true|false) y_bad=(true|false) events=(\d+)$")
SUMMARY = re.compile(r"TRACE_SUMMARY family=(\S+) shots=(\d+) observer_equal=true score=NONE$")


def fields(text):
    return dict(re.findall(r"(\w+)=(\[[^\]]*\]|\S+)", text))


def magnitude_info(diff, width):
    if not 0 <= diff < P:
        raise ValueError("difference is not a canonical field element")
    magnitude = min(diff, P - diff)
    power = magnitude > 0 and magnitude & (magnitude - 1) == 0
    exponent = magnitude.bit_length() - 1 if power else None
    return {"target_difference": hex(diff), "target_zero": magnitude == 0,
            "target_nonzero_power_of_two": power, "target_exponent": exponent,
            "target_exponent_minus_width": exponent - width if power else None}


def representable(residue, width, parked_low):
    """Does a field residue have any lift in this signed rail encoding?"""
    if not 0 <= residue < P or width <= 0:
        raise ValueError("invalid field residue or width")
    lo, hi = -(1 << (width - 1)), (1 << (width - 1)) - 1
    if parked_low:
        lo, hi = 2 * lo + 1, 2 * hi + 1
    k_min, k_max = -((residue - lo) // P), (hi - residue) // P
    if parked_low:
        k_min += (1 - residue - k_min * P) % 2
    return k_min <= k_max


def analyze(text):
    events = defaultdict(list)
    traces, summaries = {}, {}
    unmatched, marks = [], []
    for line in text.splitlines():
        if match := EVENT.fullmatch(line):
            family, shot, at, kind, rest = match.groups()
            events[family, int(shot)].append({"at": int(at), "kind": kind, **fields(rest)})
        elif match := TRACE.fullmatch(line):
            family, shot, bad, xb, yb, count = match.groups()
            key = (family, int(shot))
            if key in traces:
                raise ValueError(f"duplicate TRACE {key}")
            if (bad == "true") != (xb == "true" or yb == "true"):
                raise ValueError(f"inconsistent final result {key}")
            traces[key] = {"final_bad": bad == "true", "event_count": int(count)}
        elif match := SUMMARY.fullmatch(line):
            family, shots = match.groups()
            if family in summaries:
                raise ValueError(f"duplicate summary {family}")
            summaries[family] = int(shots)
        elif line.startswith("UNMATCHED_REV "):
            unmatched.append(line)
        elif line.startswith("TRACE_MARKS "):
            marks.append(line)
        elif line.lstrip().startswith(("EVENT ", "TRACE ", "TRACE_SUMMARY ")):
            raise ValueError(f"malformed trace line: {line}")
    if not summaries or len(marks) != 1:
        raise ValueError("missing family completion or unique mark inventory")
    expected = {(family, shot) for family, count in summaries.items() for shot in range(count)}
    if set(traces) != expected or not set(events) <= expected:
        raise ValueError("missing/extra shot records or orphan events")
    result = {"score": None, "mark_inventory": marks[0], "unmatched_reverse": unmatched,
              "families": {}, "limitations": [
                  "No observed event does not locate an error outside the walk.",
                  "A power-of-two target delta alone does not prove rail overflow.",
                  "Source deltas are not present in this observer's FWD_RAIL events.",
                  "Raw observer equivalence and optimized stream equality are distinct checks."]}
    for family, count in summaries.items():
        rows, first_kinds, forward = [], Counter(), []
        for shot in range(count):
            key = (family, shot)
            ev = sorted(events[key], key=lambda e: (e["at"], e["kind"]))
            if len(ev) != traces[key]["event_count"]:
                raise ValueError(f"event count mismatch {key}")
            first = ev[0] if ev else None
            kind = f"{first['kind']} {first.get('phase', '')}" if first else "NO_OBSERVED_EVENT"
            first_kinds[kind] += 1
            row = {"shot": shot, **traces[key], "first": first}
            if first and first["kind"] == "FWD_RAIL":
                widths, tick = json.loads(first["widths"]), int(first["tick"])
                if len(widths) != 2 or min(widths) <= 0:
                    raise ValueError("invalid rail widths")
                item = {"shot": shot, "phase": first["phase"], "tick": tick,
                        "corrupt": first["corrupt"], "widths": widths,
                        **magnitude_info(int(first["diff_t"], 16), widths[tick % 2])}
                if "want_t" in first:
                    for rail, index in (("t", tick % 2), ("s", 1 - tick % 2)):
                        got, want = int(first[f"got_{rail}"], 16), int(first[f"want_{rail}"], 16)
                        if (got - want) % P != int(first[f"diff_{rail}"], 16):
                            raise ValueError("inconsistent rail delta")
                        item[f"expected_{rail}_representable"] = representable(want, widths[index], first["low"] == "true")
                forward.append(item)
            rows.append(row)
        result["families"][family] = {
            "shots": count, "final_bad": sum(r["final_bad"] for r in rows),
            "first_kind": dict(first_kinds), "forward_events": len(forward),
            "forward_corrupt": dict(Counter(r["corrupt"] for r in forward)),
            "target_nonzero_power_of_two": sum(r["target_nonzero_power_of_two"] for r in forward),
            "target_zero": sum(r["target_zero"] for r in forward),
            "target_other_nonzero": sum(not r["target_zero"] and not r["target_nonzero_power_of_two"] for r in forward),
            "forward": forward, "shots_detail": rows}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    raw = args.log.read_bytes()
    text = (gzip.decompress(raw) if args.log.suffix == ".gz" else raw).decode("utf-8")
    result = analyze(text)
    result["input"] = {"path": str(args.log), "sha256": hashlib.sha256(raw).hexdigest(),
                       "decoded_sha256": hashlib.sha256(text.encode()).hexdigest()}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({family: {k: v for k, v in data.items() if k not in ("forward", "shots_detail")}
                      for family, data in result["families"].items()}, indent=2))


if __name__ == "__main__":
    main()
