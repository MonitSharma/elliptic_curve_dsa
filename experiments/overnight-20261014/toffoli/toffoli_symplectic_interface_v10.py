"""Derive an exact affine-product prefix from the TT-interface obstruction.

This is a constructive interface proposal, not a complete constructor or a
minimal-rank proof. All identities use all 16384 fourteen-bit assignments.
"""
import argparse, hashlib, itertools, json
from pathlib import Path
from toffoli_guided_joint import Space, combination
from toffoli_quadratic_closure import load
from toffoli_minaux_interfaces_v8 import projection

def digest(value):
    return hashlib.sha256(value.to_bytes(2048, 'little')).hexdigest()

def matrix(mask, pairs, dimension):
    rows = [0] * dimension
    for index, (i, j) in enumerate(pairs):
        if mask >> index & 1 and i and j:
            rows[i] ^= 1 << j
            rows[j] ^= 1 << i
    return rows

def matrix_rank(rows):
    return len(Space(rows).values)

def decompose(rows):
    rows = list(rows)
    factors = []
    while any(rows):
        i, j = next((i, j) for i, row in enumerate(rows)
                    for j in range(i+1, len(rows)) if row >> j & 1)
        a, b = rows[j], rows[i]
        previous = matrix_rank(rows)
        for k in range(len(rows)):
            rows[k] ^= (b if a >> k & 1 else 0) ^ (a if b >> k & 1 else 0)
        assert matrix_rank(rows) == previous - 2
        factors.append([a, b])
    return factors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('netlist', type=Path)
    parser.add_argument('seed_receipt', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    net = json.loads(args.netlist.read_bytes())
    seed_record = json.loads(args.seed_receipt.read_bytes())
    assert hashlib.sha256(args.netlist.read_bytes()).hexdigest() == seed_record['netlist_sha256']
    seed_row = next(row for row in seed_record['examined'] if row['representative'] == [13,14])
    prefix = seed_row['steps'][-1]['closure']['gates']
    raw, targets, old = load(net)
    s = Space(raw)
    for a,b in prefix:
        assert s.add(combination(a,s.values) & combination(b,s.values))
    assert len(s.values) == 24 and len(prefix) == 9
    d = Space(raw + targets + [raw[13] & raw[14]])
    pairs = list(itertools.combinations(range(24),2))
    products = [s.values[i] & s.values[j] for i,j in pairs]
    table, kernel = {}, []
    for index, value in enumerate(products):
        residual, mask = projection(value,d), 1 << index
        while residual:
            bit = residual.bit_length()-1
            if bit not in table:
                table[bit] = residual,mask
                break
            other,other_mask = table[bit]
            residual ^= other
            mask ^= other_mask
        if not residual:
            kernel.append(mask)
    known = [k for k in kernel if s.express(combination(k,products)) is not None]
    extensions = [k for k in kernel if s.express(combination(k,products)) is None]
    assert len(kernel) == 53 and len(known) == 52 and len(extensions) == 1
    current = extensions[0]
    initial_rank = matrix_rank(matrix(current,pairs,24))
    toggles = []
    while True:
        best = min((matrix_rank(matrix(current^k,pairs,24)),i) for i,k in enumerate(known))
        if best[0] >= matrix_rank(matrix(current,pairs,24)):
            break
        toggles.append(best[1])
        current ^= known[best[1]]
    rows = matrix(current,pairs,24)
    factors = decompose(rows)
    assert len(factors) * 2 == matrix_rank(rows)
    values = [combination(a,s.values) & combination(b,s.values) for a,b in factors]
    quadratic_truth = combination(current,products)
    total = combination((1 << len(values))-1, values)
    # Boolean diagonal terms and constant-index terms lie in the known span.
    diagonal_correction = s.express(total ^ quadratic_truth)
    assert diagonal_correction is not None
    assert d.express(total) is not None and s.express(total) is None
    candidate = Space(d.values + values)
    extra = []
    expanded = Space(d.values)
    for index,value in enumerate(values):
        if expanded.add(value):
            extra.append(index)
    program = [list(gate) for gate in prefix]
    replay = list(raw)
    for a,b in program:
        replay.append(combination(a,replay) & combination(b,replay))
    assert replay == s.values
    for a,b in factors:
        program.append([a,b])
        replay.append(combination(a,replay)&combination(b,replay))
    assert replay[-len(factors):] == values
    report = {
        'status':'exact_symplectic_prefix_interface_proposal',
        'source_lf_sha256':net['source_lf_sha256'],
        'netlist_sha256':hashlib.sha256(args.netlist.read_bytes()).hexdigest(),
        'seed_receipt_sha256':hashlib.sha256(args.seed_receipt.read_bytes()).hexdigest(),
        'domain_rows':16384,'seed_span_rank':24,'seed_ANDs':prefix,
        'base_interface_rank':len(d.values),'pair_products':len(pairs),
        'kernel_basis_hex':[hex(k) for k in kernel],
        'known_kernel_basis_count':len(known),'extension_kernel_basis_count':len(extensions),
        'extension_relation_hex':hex(extensions[0]),'selected_relation_hex':hex(current),
        'greedy_known_relation_toggles':toggles,'initial_alternating_rank':initial_rank,
        'selected_alternating_rank':matrix_rank(rows),'selected_matrix_rows':rows,
        'affine_product_factors':factors,'diagonal_known_correction_mask':diagonal_correction,
        'product_truth_sha256':[digest(v) for v in values],
        'products_inside_S24':[s.express(v) is not None for v in values],
        'products_inside_base_interface':[d.express(v) is not None for v in values],
        'products_inside_original_V46':[Space(old).express(v) is not None for v in values],
        'independent_extra_product_indices':extra,'candidate_interface_rank':len(candidate.values),
        'candidate_value_AND_budget':len(candidate.values)-15,
        'prefix_ANDs':program,'prefix_AND_count':len(program),
        'combined_product_truth_sha256':digest(total),
        'combined_product_is_base_interface_extension':True,
        'independent_truth_rows_replayed':16384,
        'limits':'Greedy rank reduction is not a minimum-rank proof. Prefix only; no complete target witness, cleanup, native phase, width or full score.',
        'qualified_score':None}
    args.output.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({k:report[k] for k in ['status','candidate_interface_rank','candidate_value_AND_budget','prefix_AND_count','products_inside_original_V46','independent_extra_product_indices']}))

if __name__ == '__main__':
    main()
