"""Two independent integer models of a generic full-precision leapfrog tick.

This is an interface feasibility study, not a model of the pinned finite-width
envelopes, payload, exceptional tail, measurement phases, or complete circuit.
"""
import json
import math
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

def forced(t, b):
    sign = ((t >> 1) ^ (b >> 1)) & 1
    out = (t + (1 - 2 * sign) * b) // 2
    assert out & 1
    return out, sign

def bits_choice(t, b, allow):
    dq = ((t >> 1) ^ (b >> 1)) & 1
    z2, z3, z4 = [((t >> i) ^ (b >> i) ^ dq) & 1 for i in (2,3,4)]
    eq = int((t < 0) ^ (b < 0)) ^ dq
    a2 = (1-z2) * (1-z3) * (1-z4)
    deep = 1 ^ a2 ^ (z2 * eq * (not allow))
    k2 = deep * (1-z2)
    k1 = deep ^ (k2 * z3)
    sign = dq ^ deep
    shift = 1 + k1 + 2*k2
    numerator = t + (1-2*sign)*b
    assert numerator % (1 << shift) == 0
    out = numerator >> shift
    assert out & 1
    return out, sign, k1, k2

def arithmetic_choice(t, b, allow):
    regular_sign = ((t >> 1) ^ (b >> 1)) & 1
    other_sign = regular_sign ^ 1
    deep_numerator = t + (1-2*other_sign)*b
    valuation = 10000 if deep_numerator == 0 else (abs(deep_numerator) & -abs(deep_numerator)).bit_length()-1
    equal_veto = int((t < 0) ^ (b < 0)) ^ regular_sign
    take_deep = 2 <= valuation <= 4 and (valuation != 2 or not equal_veto or allow)
    sign = other_sign if take_deep else regular_sign
    shift = valuation if take_deep else 1
    out = (t + (1-2*sign)*b) // (1 << shift)
    extra = shift-1
    return out, sign, extra & 1, extra >> 1

def tick(t, b, rule):
    t1, s0 = forced(t,b)
    t2, s1 = forced(t1,b)
    allow = rule == 'allow_all' or rule == 'full_compare' and abs(t2)>4*abs(b)
    actual = bits_choice(t2,b,allow)
    assert actual == arithmetic_choice(t2,b,allow), (t,b,rule,actual)
    out,s3,k1,k2 = actual
    label = s0 | s1<<1 | s3<<2 | k1<<3 | k2<<4
    return out,label

def main():
    results = {}
    for rule in ('forbid_window_override','allow_all','full_compare'):
        max_fiber = 0
        witness = None
        patterns = Counter()
        cases = 0
        for b in range(-255,256,2):
            fibers = {}
            for t in range(-1023,1024,2):
                out,label = tick(t,b,rule)
                fibers.setdefault(out,[]).append((t,label))
                patterns[label] += 1
                cases += 1
            for out, preimages in fibers.items():
                assert len({label for _,label in preimages}) == len(preimages), 'Saved tape must distinguish incoming states'
                if len(preimages)>max_fiber:
                    max_fiber=len(preimages)
                    witness={'source_rail':b,'outgoing_target_rail':out,'incoming_target_and_five_bit_tape':preimages}
        results[rule]={'cases':cases,'max_inverse_fiber':max_fiber,'minimum_bits_for_this_witness':math.ceil(math.log2(max_fiber)),
                       'different_tape_patterns_seen':len(patterns),'witness':witness,
                       'four_bit_local_encoding_refuted_on_this_model':max_fiber>16}
    result={'status':'GENERIC_INTEGER_INTERFACE_STUDY_NOT_A_CIRCUIT_RESULT','at_utc':datetime.now(timezone.utc).isoformat(),
            'source_specification':'leapfrog.rs pp_sign_into1, fast_choice, rail_barrel; two forced odd-preserving halves and one adaptive half/barrel',
            'both_bit_logic_and_valuation_models_agree':True,'results':results,
            'limitations':['Not a reachable-domain analysis of the seeded 256-bit circuit.','Does not model finite-width truncations, payload, tails or phase.','A fiber witness bounds only this interface; it does not bound alternate arithmetic or global history compression.']}
    out=Path(__file__).resolve().parent/'HISTORY-MODEL.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:{f:v[f] for f in ['cases','max_inverse_fiber','minimum_bits_for_this_witness','different_tape_patterns_seen','four_bit_local_encoding_refuted_on_this_model']}for k,v in results.items()},indent=2))

if __name__=='__main__':main()
