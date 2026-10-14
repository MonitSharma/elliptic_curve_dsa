"""Independent admissible-Euclid-state/Q-loan audit, not gate simulation."""
import collections
import hashlib
import json
from pathlib import Path
import sys

P = 2**256 - 2**32 - 977


def cubes(lo, hi):
    result = []
    while lo <= hi:
        size = (lo & -lo) if lo else 128
        while size > hi - lo + 1:
            size //= 2
        mask = 127 ^ (size - 1)
        result.append((mask, lo & mask))
        lo += size
    return result


def audit(packet, output):
    small = cubes(1, 98)
    large = [(127, 0)] + cubes(99, 127)
    for sy in range(256):
        nsmall = sum((sy & m) == v for m, v in small)
        nlarge = sum((sy & m) == v for m, v in large)
        assert nsmall + nlarge == 1
        if 1 <= sy <= 128:
            assert bool(nsmall) == (sy <= 98)
    counts = collections.Counter()
    largest_park = 0
    minimum_sz = 256
    for line in packet.read_text().splitlines():
        if line.startswith('#'):
            continue
        words = line.split()
        tx, ty, ox, oy, ex, ey = [int(x, 16) for x in words[1:7]]
        for d in ((tx - ox) % P, (ex - ox) % P):
            r, t = [P, d], [0, 1]
            while r[-1]:
                q = r[-2] // r[-1]
                r.append(r[-2] - q * r[-1])
                t.append(t[-2] + q * t[-1])
            ph = False
            for j in range(1, len(r)-2):
                # This describes ideal stepping states only. The source also
                # has a switch/no-step column, excluded from V's active flag.
                if not ph and r[j].bit_length() <= 128:
                    delayed = r[j].bit_length() > t[j].bit_length()
                    if not delayed:
                        ph = True
                else:
                    delayed = False
                y, z = (r[j], t[j]) if ph else (t[j], r[j])
                sy, sz = y.bit_length(), z.bit_length()
                assert 1 <= sy <= 128
                assert P == t[j]*r[j-1] + t[j-1]*r[j]
                if not ph:
                    assert t[j] < (1 << 128)
                if sy <= 98:
                    assert y >> 121 == 0
                    # Every stored QB23 candidate fits in bits 0..22 even
                    # when the true quotient exceeds the cap.
                    last = sy + 22
                    assert last < 121
                    largest_park = max(largest_park, last)
                minimum_sz = min(minimum_sz, sz)
                counts['HT' if ph else 'delayed_HR' if delayed else 'HR'] += 1
                counts['small' if sy <= 98 else 'large'] += 1
                if sy in (98, 99, 128):
                    counts[f'boundary_SY{sy}'] += 1
                if delayed:
                    ph = True
    body = dict(scope='Ideal admissible Euclid states and selector truth table; no emitted-gate score',
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                packet_sha256=hashlib.sha256(packet.read_bytes()).hexdigest(),
                small_cubes=small, large_cubes=large,
                full_8bit_partition=True, inactive_high_bit_aliases_allowed_only_with_act_zero=True,
                stored_quotient_bits=23, borrowed_Q_indices=list(range(121,128)),
                largest_active_small_park_index=largest_park,
                counts=dict(counts), minimum_ideal_sz=minimum_sz,
                limitation='Source lifetime proof and native column tests are separate obligations; this audit does not prove actual faulty prior states admissible.')
    output.write_text(json.dumps(body, indent=2)+'\n')
    print(json.dumps(body, indent=2))


if __name__ == '__main__':
    audit(Path(sys.argv[1]), Path(sys.argv[2]))
