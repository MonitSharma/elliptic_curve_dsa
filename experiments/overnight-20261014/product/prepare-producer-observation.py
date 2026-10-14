"""Observe complete production square producers and real loan/consumer interfaces; no operations added."""
from pathlib import Path
folder=Path(__file__).parent;out=folder/'producer-observation-source';out.mkdir(exist_ok=True)
s=(folder/'unbound-full-cross-source/square.rs').read_bytes().decode()
needle='    let product = circ.alloc_qubits(2 * x.len());'
insert=needle+'''
    let observed_offset=k2r_offset(x.len(),false);
    let observe=|c:&Builder,stage:&str,pp:&[QubitId]| {
        eprintln!("PRODUCER_OBSERVE {} {} {} {:#x} {:?} {:?}", policy_name, stage, c.op_count(), observed_offset,
            x.iter().map(|q|q.0).collect::<Vec<_>>(), pp.iter().map(|q|q.0).collect::<Vec<_>>());
    };
    observe(circ,"input",&product);
'''
assert s.count(needle)==1;s=s.replace(needle,insert)
for needle,insert in [
 ('    let retained = tri_square_k2r(circ, x, &product);','    let retained = tri_square_k2r(circ, x, &product);\n    observe(circ,"producer",&product);'),
 ('    folds(circ, &consumer_product);','    observe(circ,"loan_consumer",&consumer_product);\n    folds(circ, &consumer_product);\n    observe(circ,"consumed",&consumer_product);'),
 ('    tri_square_k2r_inv(circ, x, &product, retained);','    tri_square_k2r_inv(circ, x, &product, retained);\n    observe(circ,"inverse",&product);')]:
 assert s.count(needle)==1;s=s.replace(needle,insert)
out.joinpath('square.rs').write_bytes(s.encode())
s=(folder/'unbound-full-cross-source/builder-v2.rs').read_text().replace('/unbound-full-cross-v2/raw-ops.bin','/producer-observation/raw-ops.bin')
out.joinpath('builder.rs').write_text(s,newline='\n')
out.joinpath('leapfrog.rs').write_bytes((folder/'unbound-full-cross-source/leapfrog.rs').read_bytes())
