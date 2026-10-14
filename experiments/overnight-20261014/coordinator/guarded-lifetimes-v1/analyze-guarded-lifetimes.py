"""Sound conditional-reset support analysis; diagnostics only, no scored circuit."""
import argparse
import hashlib
import heapq
import importlib.util
import json
from pathlib import Path
import time

spec = importlib.util.spec_from_file_location('plain_lifetimes', Path(__file__).with_name('analyze-wire-lifetimes.py'))
plain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plain)
NO = plain.NO
TRUE = frozenset()
FALSE = None


def conjunction(a, b):
    if a is None or b is None:
        return None
    if any(-x in b for x in a):
        return None
    return a | b


def join(a, b):
    """A cube containing the union; used only for quantum may-be-one support."""
    if a is None:
        return b
    if b is None:
        return a
    return a & b


def implies(a, b):
    return a is None or (b is not None and a.issuperset(b))


class Support:
    """Classical cubes are exact expressions; fresh atoms name immutable values.

    Treating fresh values as independent forgets correlations and cannot invent
    a proof. Quantum cubes overapproximate the states where a wire can be one.
    """
    def __init__(self, locked=(), classical_inputs=()):
        self.q = {q: TRUE for q in locked}
        self.bits = {}
        self.atom = 0
        self.base = TRUE
        self.stack = []
        for bit in classical_inputs:
            self.bits[bit] = self.fresh()

    def fresh(self):
        self.atom += 1
        return frozenset((self.atom,))

    def bit(self, bit):
        return self.bits.get(bit, FALSE)

    def inverse(self, value):
        if value is FALSE:
            return TRUE
        if value == TRUE:
            return FALSE
        if len(value) == 1:
            return frozenset((-next(iter(value)),))
        return self.fresh()

    def step(self, row):
        kind, pad, c2, c1, target, bit, condition, register = row
        if pad or not 0 <= kind <= 17:
            raise ValueError('Invalid operation')
        guard = self.base if condition == NO else conjunction(self.base, self.bit(condition))
        if kind == 15:
            self.stack.append(self.base)
            self.base = conjunction(self.base, self.bit(condition))
            return False, guard
        if kind == 16:
            if not self.stack:
                raise ValueError('Unbalanced conditions')
            self.base = self.stack.pop()
            return False, guard
        old = self.q.get(target, FALSE)
        clean = False
        if kind in (6, 8, 13):
            change = guard
            for control in ((c1,) if kind == 8 else (c1, c2) if kind == 13 else ()):
                change = conjunction(change, self.q.get(control, FALSE))
            self.q[target] = join(old, change)
        elif kind == 10:
            other = self.q.get(c1, FALSE)
            self.q[target] = join(old, conjunction(guard, other))
            self.q[c1] = join(other, conjunction(guard, old))
        elif kind in (11, 12):
            clean = implies(old, guard)
            if clean:
                self.q[target] = FALSE
            if kind == 12:
                previous = self.bit(bit)
                random = self.fresh()  # Every executed or skipped Hmr consumes an outcome.
                if guard is FALSE:
                    pass
                elif implies(previous, guard):
                    self.bits[bit] = conjunction(guard, random)
                else:
                    self.bits[bit] = self.fresh()
        elif kind in (3, 4, 5) and guard is not FALSE:
            oldbit = self.bit(bit)
            if kind == 4:
                self.bits[bit] = FALSE if implies(oldbit, guard) else self.fresh()
            elif kind == 5:
                self.bits[bit] = guard if oldbit is FALSE else TRUE if oldbit == TRUE or guard == TRUE else self.fresh()
            elif guard == TRUE:
                self.bits[bit] = self.inverse(oldbit)
            elif oldbit is FALSE:
                self.bits[bit] = guard
            elif oldbit == guard:
                self.bits[bit] = FALSE
            elif implies(oldbit, guard) and len(oldbit - guard) == 1:
                self.bits[bit] = conjunction(guard, frozenset((-next(iter(oldbit - guard)),)))
            else:
                self.bits[bit] = self.fresh()
        return clean, guard


def analyze_rows(rows):
    """Accept a replayable iterator factory; precollect all input ABI declarations."""
    locked, inputbits = set(), set()
    for _, row in rows():
        if row[0] == 2:
            if row[4] != NO:
                locked.add(row[4])
            if row[5] != NO:
                inputbits.add(row[5])
    state = Support(locked, inputbits)
    starts, intervals = {}, []
    operations = width = extra = normal = unresolved = 0
    examples = []
    for index, row in rows():
        for q in row[2:5]:
            if q != NO:
                starts.setdefault(q, index)
                width = max(width, q + 1)
        clean, guard = state.step(row)
        kind, _, _, _, target, _, condition, _ = row
        if kind in (11, 12) and target not in locked:
            unconditional = not state.stack and condition == NO
            if clean:
                intervals.append((starts.pop(target), index, target))
                if unconditional:
                    normal += 1
                else:
                    extra += 1
                    if len(examples) < 20:
                        examples.append({'operation': index, 'qubit': target, 'guard': None if guard is None else sorted(guard)})
            else:
                unresolved += 1
        operations = index + 1
    if state.stack:
        raise ValueError('Unclosed conditions')
    intervals = [(s,e,q) for s,e,q in intervals if q not in locked]
    intervals += [(0 if q in locked else s, operations, q) for q,s in starts.items()]
    intervals += [(0, operations, q) for q in locked if q not in starts]
    intervals.sort()
    live, peak, first = [], 0, None
    for start, end, q in intervals:
        while live and live[0] < start:
            heapq.heappop(live)
        heapq.heappush(live, end)
        if len(live) > peak:
            peak, first = len(live), start
    return {'status': 'sound_support_allocation_diagnostic_only', 'operations': operations,
            'physical_width': width, 'fixed_abi_qubits': len(locked),
            'unconditional_clean_boundaries': normal, 'proved_conditional_clean_boundaries': extra,
            'unresolved_conditional_resets': unresolved, 'intervals': len(intervals),
            'conservative_peak_live_intervals': peak, 'first_peak_operation': first,
            'examples': examples, 'immutable_classical_atoms': state.atom,
            'qualification': 'No candidate source, gate deletion, benchmark or scored width claim'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stream', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    began = time.monotonic()
    result = analyze_rows(lambda: plain.records(args.stream))
    with args.stream.open('rb') as f:
        result['stream_sha256'] = hashlib.file_digest(f, 'sha256').hexdigest()
    result['elapsed_seconds'] = time.monotonic() - began
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
