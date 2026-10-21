import ctypes
import ctypes.util
import struct
import bisect
import hashlib
import subprocess
import json
import os
from collections import defaultdict

z = ctypes.CDLL(ctypes.util.find_library("zstd"))
z.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
z.ZSTD_decompress.restype = ctypes.c_size_t
z.ZSTD_compress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
z.ZSTD_compress.restype = ctypes.c_size_t
z.ZSTD_compressBound.argtypes = [ctypes.c_size_t]
z.ZSTD_compressBound.restype = ctypes.c_size_t

NO = (1 << 64) - 1

def load_ops(path):
    with open(path, "rb") as f:
        d = f.read()
    assert d[:8] == b"QECCOPSZ"
    n = struct.unpack_from("<Q", d, 8)[0]
    out = ctypes.create_string_buffer(n * 56)
    dec = z.ZSTD_decompress(out, len(out), d[16:], len(d) - 16)
    assert dec == n * 56
    return n, out.raw

def save_ops(path, ops_bytes):
    n = len(ops_bytes) // 56
    bound = z.ZSTD_compressBound(len(ops_bytes))
    dst = ctypes.create_string_buffer(bound)
    csize = z.ZSTD_compress(dst, bound, ops_bytes, len(ops_bytes), 3)
    with open(path, "wb") as f:
        f.write(b"QECCOPSZ")
        f.write(struct.pack("<Q", n))
        f.write(dst.raw[:csize])

def hash128(tag: bytes) -> int:
    return int.from_bytes(hashlib.blake2b(tag, digest_size=16).digest(), "little")

def build_variant(n, raw, chain_unwrap_plan, target_lease_indices=None):
    pre_n = n - 96
    nq = 1234

    cval = {}
    cond_stack = []
    def current_cond():
        for b, v in cond_stack:
            if v == 0:
                return 0
            if v == -1:
                return -1
        return 1

    clean = [True] * nq
    ep = [None] * nq
    brigade_episodes = []

    for i in range(pre_n):
        k, qc2, qc1, qt, ct, cc, rt = struct.unpack_from("<7Q", raw, i * 56)
        if k == 15:
            cv = cval.get(cc, -1)
            if i >= 2 and cv == -1:
                k1, _, _, _, ct1, cc1, _ = struct.unpack_from("<7Q", raw, (i - 2) * 56)
                k2, _, _, _, ct2, cc2, _ = struct.unpack_from("<7Q", raw, (i - 1) * 56)
                if k1 == 5 and ct1 == cc and cc1 == NO and k2 == 3 and ct2 == cc and cc2 != NO:
                    cv = 1
            cond_stack.append((cc, cv))
            continue
        elif k == 16:
            cond_stack.pop()
            continue

        eff = current_cond()
        if cc != NO:
            v = cval.get(cc, -1)
            if v == 0:
                eff = 0
            elif v == -1 and eff == 1:
                eff = -1

        for q in (qc2, qc1, qt):
            if q != NO and ep[q] is not None:
                ep[q]["all_ops"].append(i)

        if k == 4:
            if eff == 1:
                cval[ct] = 0
            elif eff == -1:
                cval[ct] = -1
        elif k == 5:
            if eff == 1:
                cval[ct] = 1
            elif eff == -1:
                cval[ct] = -1
        elif k == 3:
            if eff == 1:
                pv = cval.get(ct, 0)
                cval[ct] = (1 - pv) if pv in (0, 1) else -1
            elif eff == -1:
                cval[ct] = -1
        elif k == 8 and qt == NO and qc1 == NO:
            if eff == 1:
                sv = cval.get(cc, 0)
                dv = cval.get(ct, 0)
                cval[ct] = (sv ^ dv) if (sv in (0, 1) and dv in (0, 1)) else -1
            elif eff == -1:
                cval[ct] = -1
        elif k == 11:
            if qt != NO:
                if eff == 1:
                    clean[qt] = True
                    ep[qt] = None
                elif eff == -1:
                    clean[qt] = False
                    ep[qt] = None
        elif k == 12:
            if eff != 0 and ct != NO:
                cval[ct] = -1
            if qt != NO:
                if eff == 1:
                    if ep[qt] is not None:
                        info = ep[qt]
                        info["end_op"] = i
                        info["hmr_ct"] = ct
                        info["cz_op"] = None
                        for j in range(i + 1, min(i + 5, pre_n)):
                            kj, _, qc1j, qtj, _, ccj, _ = struct.unpack_from("<7Q", raw, j * 56)
                            if kj == 9 and ccj == ct:
                                info["cz_op"] = j
                                info["cz_c1"] = qc1j
                                info["cz_c2"] = qtj
                                break
                        if info["valid"] and info["live_writes"] == 1 and info["live_reads"] == 1 and info["cond_touches"] == 0 and info["dead_touches"] > 0:
                            brigade_episodes.append(info)
                    clean[qt] = True
                    ep[qt] = None
                elif eff == -1:
                    if ep[qt] is not None:
                        ep[qt]["cond_touches"] += 1
                    clean[qt] = False
        elif eff != 0:
            if eff == 1 and k in (13, 8) and qt != NO and clean[qt]:
                clean[qt] = False
                ep[qt] = {
                    "donor": qt,
                    "start_op": i,
                    "write_kind": k,
                    "write_c2": qc2,
                    "write_c1": qc1,
                    "live_writes": 1,
                    "live_reads": 0,
                    "read_op": None,
                    "read_target": None,
                    "dead_touches": 0,
                    "cond_touches": 0,
                    "valid": True,
                    "all_ops": [i],
                }
                for c in (qc2, qc1):
                    if c != NO:
                        clean[c] = False
                        if ep[c] is not None:
                            if k == 8 and c == qc1:
                                ep[c]["live_reads"] += 1
                                ep[c]["read_op"] = i
                                ep[c]["read_target"] = qt
                            else:
                                ep[c]["valid"] = False
            else:
                for q in (qc2, qc1, qt):
                    if q != NO:
                        clean[q] = False
                        if ep[q] is not None:
                            if eff == -1:
                                ep[q]["cond_touches"] += 1
                            elif k == 8 and q == qc1:
                                ep[q]["live_reads"] += 1
                                ep[q]["read_op"] = i
                                ep[q]["read_target"] = qt
                            else:
                                ep[q]["valid"] = False
        else:
            for q in (qc2, qc1, qt):
                if q != NO and ep[q] is not None:
                    ep[q]["dead_touches"] += 1

    by_read_op = {b["read_op"]: b for b in brigade_episodes}
    by_start_op = {b["start_op"]: b for b in brigade_episodes}
    chains = []
    visited = set()
    for b in brigade_episodes:
        if b["start_op"] in visited:
            continue
        curr = b
        while curr["write_kind"] == 8 and curr["start_op"] in by_read_op:
            curr = by_read_op[curr["start_op"]]
        if curr["write_kind"] != 13:
            continue
        chain = [curr]
        visited.add(curr["start_op"])
        while curr["read_op"] in by_start_op:
            nxt = by_start_op[curr["read_op"]]
            chain.append(nxt)
            visited.add(nxt["start_op"])
            curr = nxt
        chains.append(chain)

    post_chains = [c for c in chains if c[0]["start_op"] >= 22638790]
    ops_to_delete = set()
    ops_to_replace = {}

    for chain_idx, k_tail in chain_unwrap_plan.items():
        chain = post_chains[chain_idx]
        assert 1 <= k_tail <= len(chain)
        suffix = chain[-k_tail:]
        tail = chain[-1]
        d1 = tail["read_target"]
        rep_op = tail["read_op"]
        for b in suffix:
            for op_idx in b["all_ops"]:
                if op_idx != rep_op:
                    ops_to_delete.add(op_idx)
            if b["cz_op"] is not None:
                ops_to_delete.add(b["cz_op"])
        if k_tail == len(chain):
            head = chain[0]
            ops_to_replace[rep_op] = (13, head["write_c2"], head["write_c1"], d1, NO, NO, NO)
        else:
            prev = chain[len(chain) - k_tail - 1]
            ops_to_replace[rep_op] = (8, NO, prev["donor"], d1, NO, NO, NO)

    # Scan unwrapped stream for the 15 unconditional leases
    q_state = [(0, 0) for _ in range(nq)]
    c_state = {}
    def get_c(bit_id):
        if bit_id not in c_state:
            c_state[bit_id] = (0, hash128(f"in_c_{bit_id}".encode()))
        return c_state[bit_id]

    cond_stack = []
    top_uncond_ccx_groups = defaultdict(list)
    raw_touches = [[] for _ in range(nq)]
    raw_resets = [[] for _ in range(nq)]

    for i in range(pre_n):
        if i in ops_to_delete:
            continue
        if i in ops_to_replace:
            k, qc2, qc1, qt, ct, cc, rt = ops_to_replace[i]
        else:
            k, qc2, qc1, qt, ct, cc, rt = struct.unpack_from("<7Q", raw, i * 56)

        if k in (11, 12) and qt != NO:
            raw_resets[qt].append(i)
        if k != 11:
            for q in (qc2, qc1, qt):
                if q != NO:
                    raw_touches[q].append(i)

        if k == 2:
            if qt != NO:
                q_state[qt] = (0, hash128(f"in_q_{qt}".encode()))
            if ct != NO:
                c_state[ct] = (0, hash128(f"in_c_{ct}".encode()))
            continue
        elif k == 15:
            c_val = get_c(cc)
            is_recomp = False
            if i >= 2 and c_val != (0, 0) and c_val != (1, 0):
                k1, _, _, _, ct1, cc1, _ = struct.unpack_from("<7Q", raw, (i - 2) * 56)
                k2, _, _, _, ct2, cc2, _ = struct.unpack_from("<7Q", raw, (i - 1) * 56)
                if k1 == 5 and ct1 == cc and cc1 == NO and k2 == 3 and ct2 == cc and cc2 != NO:
                    c_val = (1, 0)
                    is_recomp = True
            cond_stack.append((c_val, is_recomp))
            continue
        elif k == 16:
            cond_stack.pop()
            continue

        raw_eff = [c for c, _ in cond_stack]
        in_recomp = any(r for _, r in cond_stack)
        if cc != NO:
            raw_eff.append(get_c(cc))
        if any(c == (0, 0) for c in raw_eff):
            continue

        eff = tuple(c for c in raw_eff if c != (1, 0))
        is_uncond = (len(eff) == 0)

        if k == 6:
            q_state[qt] = (q_state[qt][0] ^ 1, q_state[qt][1]) if is_uncond else (q_state[qt][0], q_state[qt][1] ^ hash128(f"cx_{eff}".encode()))
        elif k == 8:
            q_state[qt] = (q_state[qt][0] ^ q_state[qc1][0], q_state[qt][1] ^ q_state[qc1][1]) if is_uncond else (q_state[qt][0], q_state[qt][1] ^ hash128(f"ccx_{eff}_{q_state[qc1]}".encode()))
        elif k == 10:
            if is_uncond:
                q_state[qc1], q_state[qt] = q_state[qt], q_state[qc1]
            else:
                d = (q_state[qc1][0] ^ q_state[qt][0], q_state[qc1][1] ^ q_state[qt][1])
                ch = hash128(f"cswap_{eff}_{d}".encode())
                q_state[qc1] = (q_state[qc1][0], q_state[qc1][1] ^ ch)
                q_state[qt] = (q_state[qt][0], q_state[qt][1] ^ ch)
        elif k == 11:
            q_state[qt] = (0, 0) if is_uncond else (0, hash128(f"cr_{eff}_{q_state[qt]}".encode()))
        elif k == 12:
            q_state[qt] = (0, 0)
            c_state[ct] = (0, hash128(f"hmr_{i}".encode()))
        elif k == 3:
            old = get_c(ct)
            c_state[ct] = (old[0] ^ 1, old[1]) if is_uncond else (old[0], old[1] ^ hash128(f"bi_{eff}".encode()))
        elif k == 4:
            c_state[ct] = (0, 0) if is_uncond else (0, hash128(f"bs0_{eff}_{get_c(ct)}".encode()))
        elif k == 5:
            c_state[ct] = (1, 0) if is_uncond else (0, hash128(f"bs1_{eff}_{get_c(ct)}".encode()))
        elif k == 13:
            X, Y = q_state[qc1], q_state[qc2]
            Z = (1 ^ X[0] ^ Y[0], X[1] ^ Y[1])
            triple = tuple(sorted([X, Y, Z]))
            prod_h = hash128(f"prod_{triple}".encode())
            if is_uncond:
                if not in_recomp and len(raw_eff) == 0:
                    top_uncond_ccx_groups[triple].append((i, qc2, qc1, qt))
                if in_recomp:
                    q_state[qt] = (0, prod_h)
                else:
                    q_state[qt] = (q_state[qt][0], q_state[qt][1] ^ prod_h)
            else:
                ch = hash128(f"ccx_cond_{eff}_{prod_h}".encode())
                q_state[qt] = (q_state[qt][0], q_state[qt][1] ^ ch)

    def find_donors(i0, i1):
        donors = []
        for q in range(nq):
            pos = bisect.bisect_left(raw_touches[q], i0)
            if pos < len(raw_touches[q]) and raw_touches[q][pos] <= i1:
                continue
            if pos == 0:
                if q >= 512:
                    donors.append(q)
            else:
                prev_t = raw_touches[q][pos - 1]
                rpos = bisect.bisect_left(raw_resets[q], prev_t)
                if rpos < len(raw_resets[q]) and raw_resets[q][rpos] == prev_t:
                    donors.append(q)
        return donors

    u_multi = {k: v for k, v in top_uncond_ccx_groups.items() if len(v) >= 2}
    candidates = []
    for triple, uses in u_multi.items():
        for idx in range(len(uses) - 1):
            i0, c2_0, c1_0, t_0 = uses[idx]
            i1, c2_1, c1_1, t_1 = uses[idx + 1]
            dr = find_donors(i0, i1)
            if dr:
                candidates.append((i1, i0, c2_0, c1_0, t_0, c2_1, c1_1, t_1, dr))

    candidates.sort(key=lambda x: (x[0], x[1]))
    busy_until = [-1] * nq
    used_endpoints = set()
    assigned = []
    for i1, i0, c2_0, c1_0, t_0, c2_1, c1_1, t_1, dr in candidates:
        if i0 in used_endpoints or i1 in used_endpoints:
            continue
        chosen = None
        best_busy = -2
        for d in dr:
            if busy_until[d] < i0 and busy_until[d] > best_busy:
                best_busy = busy_until[d]
                chosen = d
        if chosen is not None:
            busy_until[chosen] = i1
            used_endpoints.add(i0)
            used_endpoints.add(i1)
            assigned.append((i0, i1, chosen, c2_0, c1_0, t_0, c2_1, c1_1, t_1))

    if target_lease_indices is not None:
        assigned = [assigned[idx] for idx in target_lease_indices]

    print(f"Unwrapped {sum(chain_unwrap_plan.values())} links, assigned {len(assigned)} leases.")
    scratch_ct = 512
    start_map = {x[0]: x for x in assigned}
    end_map = {x[1]: x for x in assigned}

    zero_prod_op = 25991369
    ops_to_delete.add(zero_prod_op)

    out_chunks = []
    for i in range(n):
        if i in ops_to_delete:
            continue
        if i in start_map:
            i0, i1, d, c2_0, c1_0, t_0, c2_1, c1_1, t_1 = start_map[i]
            out_chunks.append(struct.pack("<7Q", 13, c2_0, c1_0, d, NO, NO, NO))
            out_chunks.append(struct.pack("<7Q", 8, NO, d, t_0, NO, NO, NO))
        elif i in end_map:
            i0, i1, d, c2_0, c1_0, t_0, c2_1, c1_1, t_1 = end_map[i]
            out_chunks.append(struct.pack("<7Q", 8, NO, d, t_1, NO, NO, NO))
            out_chunks.append(struct.pack("<7Q", 12, NO, NO, d, scratch_ct, NO, NO))
            out_chunks.append(struct.pack("<7Q", 9, NO, c1_1, c2_1, NO, scratch_ct, NO))
        elif i in ops_to_replace:
            out_chunks.append(struct.pack("<7Q", *ops_to_replace[i]))
        else:
            out_chunks.append(raw[i * 56 : (i + 1) * 56])

    return b"".join(out_chunks)

def main():
    n, raw = load_ops("/home/hclau/ecdsa_research/product179-native-20261017/candidate/ops.bin")
    bin_path = "/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2"

    # Plan A: 11 tail links unwrapped (Chains 0,1,2,4,5,7,9,10,67), 11 corresponding leases (indices 0..9 and 14)
    plan_11 = {0: 1, 1: 1, 2: 2, 4: 1, 5: 1, 7: 2, 9: 1, 10: 1, 67: 1}
    out_11 = build_variant(n, raw, plan_11, target_lease_indices=[0,1,2,3,4,5,6,7,8,9,14])
    save_ops("/tmp/product179_plus_11_5.ops.bin", out_11)

    # Plan B: 15 tail links unwrapped (add Chains 11,18,31,34), all 15 leases
    plan_15 = {0: 1, 1: 1, 2: 2, 4: 1, 5: 1, 7: 2, 9: 1, 10: 1, 11: 1, 18: 1, 31: 1, 34: 1, 67: 1}
    out_15 = build_variant(n, raw, plan_15, target_lease_indices=None)
    save_ops("/tmp/product179_plus_15_5.ops.bin", out_15)

    for p in ("/tmp/p179_base.jsonl", "/tmp/p179_11.jsonl", "/tmp/p179_15.jsonl"):
        if os.path.exists(p):
            os.remove(p)

    subprocess.run([bin_path, "/home/hclau/ecdsa_research/product179-native-20261017/candidate/ops.bin", "test-p179-align", "0", "16", "16", "/tmp/p179_base.jsonl", "0"], check=True)
    subprocess.run([bin_path, "/tmp/product179_plus_11_5.ops.bin", "test-p179-align", "0", "16", "16", "/tmp/p179_11.jsonl", "0"], check=True)
    subprocess.run([bin_path, "/tmp/product179_plus_15_5.ops.bin", "test-p179-align", "0", "16", "16", "/tmp/p179_15.jsonl", "0"], check=True)

    base_rows = sorted([json.loads(line) for line in open("/tmp/p179_base.jsonl")], key=lambda x: x["batch"])
    r11_rows = sorted([json.loads(line) for line in open("/tmp/p179_11.jsonl")], key=lambda x: x["batch"])
    r15_rows = sorted([json.loads(line) for line in open("/tmp/p179_15.jsonl")], key=lambda x: x["batch"])

    diffs_11 = []
    diffs_15 = []
    for b, r11, r15 in zip(base_rows, r11_rows, r15_rows):
        d11 = (b["toffoli"] - r11["toffoli"]) / 64.0
        d15 = (b["toffoli"] - r15["toffoli"]) / 64.0
        diffs_11.append(d11)
        diffs_15.append(d15)
        print(f"Batch {b['batch']:2d}: fail={len(b['failures'])}/{len(r11['failures'])}/{len(r15['failures'])} dirty={r11['dirty_shots']}/{r15['dirty_shots']} d11={d11:8.4f} d15={d15:8.4f}")
    print(f"Mean d11: {sum(diffs_11)/len(diffs_11):.6f}, Mean d15: {sum(diffs_15)/len(diffs_15):.6f}")

if __name__ == "__main__":
    main()
