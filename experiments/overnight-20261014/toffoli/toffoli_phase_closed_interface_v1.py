"""Check a closed-subspace obstruction to all-free quadratic bank cleanup.

W is the post-loan live-function span, and D is the final low data/passengers.
If D lies inside a proper S subset W with P2(S) intersect W = S, no chain of
linear rebases and quadratic-phase measurements can shrink W to D while every
live function remains in W. Reverse the hypothetical erasures to prove this.
This does not cover temporary Toffolis, cubic/higher phase gates, or interfaces
that retain the original six hidden directions through the consumer.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load
from toffoli_check_obstruction import rank


def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('certificate',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    net=json.loads(a.netlist.read_text());receipt=json.loads(a.certificate.read_text());raw,targets,original=load(net)
    # The existing constructor certificate stores exact original-basis masks.
    print('certificate keys',list(receipt))
    prefix=receipt.get('closed_prefix_gates')
    if prefix is None:prefix=receipt.get('gates')
    assert prefix is not None
    s=Space(raw)
    for aa,bb in prefix:
        assert s.add(combination(aa,s.values)&combination(bb,s.values))
    w=Space(raw+targets)
    data=list(raw);data[1:7]=targets[21:27]
    product=s.values+[x&y for x,y in itertools.combinations(s.values,2)]
    sr=rank(s.values);wr=rank(w.values);pr=rank(product);ur=rank(product+w.values)
    contained=all(s.express(v) is not None for v in data)
    closed=pr+wr-ur==sr
    result={'status':'proper_closed_subspace_excludes_all_free_quadratic_cleanup' if contained and closed and sr<wr else 'obstruction_not_established',
            'source_lf_sha256':net['source_lf_sha256'],'netlist_sha256':hashlib.sha256(a.netlist.read_bytes()).hexdigest(),
            'constructor_certificate_sha256':hashlib.sha256(a.certificate.read_bytes()).hexdigest(),
            'domain_rows':1<<14,'final_data_rank':rank(data),'closed_span_rank':sr,'loan_interface_rank':wr,
            'quadratic_product_span_rank':pr,'product_plus_interface_rank':ur,'intersection_rank':pr+wr-ur,
            'final_data_inside_closed_span':contained,'closed_prefix_gates':prefix,
            'final_data_closed_coordinates':[s.express(v) for v in data],
            'argument':'All live functions after the six early erases lie in W. A reversible linear write/rebase preserves the current function span. A zero-Toffoli measurement erase with exact quadratic phase requires its measured function to belong to P2(the remaining span). Reverse any hypothetical cleanup chain from final D: induction keeps each restored function in S, since remaining spans are contained in S and P2(S) intersect W=S. The initial W has rank greater than S, contradiction.',
            'limits':'Only this complete W-to-D low-domain interface with quadratic (free Z/CZ) phase repair and no nonlinear value gates. Does not exclude cleanup with one or more Toffolis, higher-degree phase gates, retained hidden bank directions, or other consumer interfaces. Native full-circuit applicability requires boundary/domain proof.'}
    a.output.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:result[k] for k in ['status','closed_span_rank','loan_interface_rank','final_data_inside_closed_span']}))


if __name__=='__main__':main()
