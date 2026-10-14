"""Collect finite paired evidence; never promote failures to a resource record."""
from pathlib import Path
import collections, hashlib, json, re

root = Path(__file__).resolve().parents[3]
evidence = root / 'research-output/overnight-20261014/product/b3-paired'
out = Path(__file__).parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
log = (evidence/'run.log').read_text()
results = []
blocks = log.split('DIAGNOSTIC_ONLY ')
for mode, block, tail in zip(['independent', 'structured', 'candidate_official_packet'], blocks, blocks[1:]):
    line = tail.splitlines()[0]
    fields = dict(re.findall(r'(\w+)=(\w+)', line))
    fields = {k: int(v) if v.isdigit() else v for k,v in fields.items()}
    assert fields['unequal_batches'] == 0 and fields['score'] == 'NONE'
    bad = collections.Counter(re.findall(r'B3_COUNTEREXAMPLE index=\d+ family=(\w+)', block))
    failures=[dict(re.findall(r'(\w+)=(\S+)',l))for l in block.splitlines()if l.startswith('B3_COUNTEREXAMPLE ')]
    xbad=sum(v['left_x']!=v['expected_x']for v in failures)
    ybad=sum(v['left_y']!=v['expected_y']for v in failures)
    results.append({'packet_mode': mode, **fields, 'left_x_bad':xbad,'right_x_bad':xbad,'left_y_bad':ybad,'right_y_bad':ybad,'classical_failure_families': dict(bad)})
assert [r['shots'] for r in results] == [256, 256, 9024]
first249 = next(l for l in log.splitlines() if l.startswith('B3_COUNTEREXAMPLE index=249 '))
streams = (evidence/'streams.sha256').read_text().splitlines()
assert streams[0].split()[0] == '0f10de57f45349c89163faf6e5ab0694aec3d3bfa720f10ee8b185a9fb2914ce'
assert streams[1].split()[0] == 'ffcf319ca344c29e3b8cb6d04578c0a886b328fd64b4c18558d6a5ee7da9c93c'
summary = {'status': 'completed_finite_paired_equivalence_with_inherited_failures', 'qualified_score': None,
 'baseline_revision': 'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7',
 'baseline_stream_sha256': streams[0].split()[0], 'candidate_stream_sha256': streams[1].split()[0],
 'native_sha256': (evidence/'native.sha256').read_text().split()[0],
 'source_binding': 'Dedicated replay crate compiled against clean detached B3; protected evaluator/Simulator/circuit hashes recorded; source includes embedded clean checkout path.',
 'official_packet_transcript': 'Candidate Fiat-Shamir seed over right stream;9024 scalar-pair draws;official skip rules;post-point-generation XOF cloned and advanced continuously per batch for both streams.',
 'measurement_order_check': 'Complete R/Hmr Op sequence equality, including wires, classical slots and explicit conditions, asserted before replay.',
 'comparison': 'Every final quantum slot, every final classical slot and phase mask before scratch clearing;same active lane mask.',
 'independent_packet_domain': 'product-b3-independent-structured-v1', 'independent_measurement_domain': 'product-b3-paired-fixed-measurement-v1',
 'results': results, 'first_official_counterexample_249': first249,
 'files_sha256': {p.name: sha(p) for p in evidence.iterdir() if p.is_file()},
 'baseline_receipt_sha256': sha(out/'b3-baseline-receipt.json'),
 'limitations': ['Finite native equivalence tests do not prove global circuit exactness.', 'The candidate official benchmark failed; both original and candidate retain the same observed value and phase failures.', 'No nonce search, packet tuning, protected source changes, scorer changes or diagnostic score writes.']}
(out/'b3-paired-receipt.json').write_text(json.dumps(summary, indent=2)+'\n', newline='\n')
(out/'b3-first249.txt').write_text(first249+'\n', newline='\n')
print(json.dumps(results, indent=2))
