"""Independent exact-integer audit of exported compact benchmark inputs.

This flags retained map-valuation assumptions; it does not simulate or score
the circuit. Source formulas: frogdrop_sched.rs shot and predict_n_geometry.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

P = 2**256 - 2**32 - 977


def valuation(x):
    return (x & -x).bit_length() - 1 if x else 999


def over(w, z, k=24):
    sz = z.bit_length()
    s = sz - k
    if s < 0:
        return None
    zh = (z >> s) | 1
    f = ((1 << (256 - s)) - 1) // zh
    u = max(0, 257 - sz - 26)
    return (w >> u) > (f >> u)


def search_events(r, t, nn, head_bits=24):
    result = []
    for j in range(1, nn - 1):
        ph = 0 if r[j].bit_length() > 128 or (r[j].bit_length() <= 128 and r[j].bit_length() > t[j].bit_length()) else 1
        # After a delayed crossing, later steps are HT even if r is small.
        if j > 1 and r[j - 1].bit_length() <= 128:
            ph = 1
        q = r[j - 1] // r[j]
        if q >= 1 << 23:
            result.append(dict(kind="quotient_cap", euclid_step=j, quotient=q))
        z, y = (r[j], t[j]) if ph == 0 else (t[j], r[j])
        bb = 258 - z.bit_length() - y.bit_length()
        if ph == 0:
            w = t[j - 1]
            for kk in range(22, -1, -1):
                if kk >= bb:
                    continue
                tr = w + (y << kk)
                if not over(tr, z, head_bits):
                    w = tr
            if w != t[j + 1]:
                result.append(dict(kind="reciprocal_hr", euclid_step=j, head_bits=head_bits,
                                   quotient=q, got=hex(w), expected=hex(t[j + 1]),
                                   z=hex(z), y=hex(y), bb=bb))
        else:
            c, x = q, r[j - 1]
            for kk in range(23):
                if kk >= bb:
                    continue
                if c & (1 << kk):
                    x -= y << kk
                if not over(x + (y << kk), z, head_bits):
                    c ^= 1 << kk
            if c or x != r[j + 1]:
                result.append(dict(kind="reciprocal_ht", euclid_step=j, head_bits=head_bits,
                                   quotient=q, residual_q=c, got=hex(x), expected=hex(r[j + 1]),
                                   z=hex(z), y=hex(y), bb=bb))
    return result


def traversal(x, head_bits=24):
    r, t = [P, x], [0, 1]
    while r[-1]:
        q = r[-2] // r[-1]
        r.append(r[-2] - q * r[-1])
        t.append(t[-2] + q * t[-1])
    nn = len(r) - 1
    maps = []
    j, ph, c, dq = 1, 0, 0, False
    while not (ph == 1 and j == nn - 1):
        if dq:
            kind = "Dq"
            maps.append((c, kind, t[j], r[j + 1], r[j], t[j + 1], 278))
            j += 1
            dq = False
        elif ph == 1:
            kind = "Ht"
            maps.append((c, kind, t[j], r[j + 1], r[j], t[j + 1], 278))
            j += 1
        elif r[j].bit_length() <= 128 and r[j].bit_length() > t[j].bit_length():
            kind = "Dl"
            maps.append((c, kind, t[j + 1], r[j], t[j], r[j + 1], 277))
            ph, dq = 1, True
        elif r[j].bit_length() <= 128:
            kind = "Sw"
            maps.append((c, kind, t[j - 1], r[j], t[j], r[j - 1], 277))
            ph = 1
        else:
            kind = "Hr"
            maps.append((c, kind, r[j], t[j + 1], t[j], r[j + 1], 278))
            j += 1
        c += 1
    failures = search_events(r, t, nn, head_bits)
    for c, kind, z, x, y, zn, n in maps:
        vx, vy = valuation(x), valuation(y)
        cut = n - max(x.bit_length(), y.bit_length())
        need = max(z.bit_length() + vx, zn.bit_length() + vy)
        if vx > 21 or vy > 21 or need > cut:
            failures.append(dict(column=c, kind=kind, v2_x=vx, v2_y=vy,
                                 cut=cut, need=need, retained_emax=21,
                                 valuation_exceeded=vx > 21 or vy > 21,
                                 map_region_exceeded=need > cut,
                                 z=hex(z), x=hex(x), y=hex(y), z_next=hex(zn)))
    tailv = valuation(r[nn - 2])
    if tailv > 21:
        failures.append(dict(kind="tail", v2=tailv, retained_emax=21))
    return dict(columns=c, events=failures,
                max_v2=max([valuation(x) for x in r[:-1] + t[1:]]))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("packet", type=Path)
    a.add_argument("output", type=Path)
    a.add_argument("--head-bits", type=int, default=24)
    args = a.parse_args()
    failures = []
    details = []
    for line in args.packet.read_text().splitlines():
        if line.startswith("#"):
            continue
        w = line.split()
        idx = int(w[0])
        tx, ty, ox, oy, ex, ey = map(lambda v: int(v, 16), w[1:7])
        for division, dx in ((1, (tx - ox) % P), (2, (ex - ox) % P)):
            tr = traversal(dx, args.head_bits)
            rec = dict(shot=idx, division=division, input=hex(dx), **tr)
            if tr["events"]:
                failures.append(rec)
            if idx == 1170:
                details.append(rec)
    report = dict(scope="Independent classical map-domain audit; diagnostic only, no score",
                  packet_sha256=hashlib.sha256(args.packet.read_bytes()).hexdigest(),
                  source_formulas="c95b9325 frogdrop_sched.rs shot/predict_n_geometry",
                  retained_emax=21, events=failures, shot1170=details,
                  head_bits=args.head_bits, quotient_cap_bits=23,
                  flagged_shots=sorted(set(r["shot"] for r in failures)))
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"flagged_shots": report["flagged_shots"],
                      "event_divisions": len(failures), "shot1170": details}, indent=2))


if __name__ == "__main__":
    main()
