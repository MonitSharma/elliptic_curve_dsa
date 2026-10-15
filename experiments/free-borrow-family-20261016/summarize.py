from pathlib import Path
import json,collections,hashlib
r=Path('/home/hclau/ecdsa_research/free-borrow-family-20261016');d=json.loads((r/'affine-lower-audit.json').read_text());rows=d['rows']
seeded=[x for x in rows if x['seed']is not None and x['lower']];assert len(seeded)==2468
assert all(x['seed']==x['lower'][0]['b_q']for x in seeded)
assert all(x['lower'][0]['b_q']!=x['lower'][1]['b_q']and x['lower'][0]['a_q']not in[x['lower'][0]['b_q'],x['lower'][1]['b_q']]for x in seeded)
seams=[]
for line in(r/'source-map.log').read_text().splitlines():
 f=line.split('\t')
 if f[0]=='PHASE_HMR'and f[4].endswith('leapfrog.rs')and int(f[5])in[3983,4050,4101]:seams.append(dict(raw_op=int(f[1]),q=int(f[2]),measurement_bit=int(f[3]),source_line=int(f[5]),family={3983:'front classical',4050:'T6 quantum',4101:'back classical'}[int(f[5])]))
out=dict(raw_identity_verified=(r/'raw-verification.exit').read_text().strip()=='0',raw_sha256=d['raw_stream_sha256'],queries=d['queries'],counts=d['counts_by_family'],existing_seed_equals_next_lower_source_count=len(seeded),distinct_source_low1_low2_and_accumulator=True,lower_source_classifications=dict(collections.Counter(x['b']['type']for row in rows for x in row['lower'])),lower_accumulator_classifications=dict(collections.Counter(x['a']['type']for row in rows for x in row['lower'])),no_positive_constant_or_classical_lower_bit_certificates=True,unknown_is_not_nonclassical_proof=True,retaining_seed_while_widening_is_redundant='MAJ(!a,b,b)=b',moving_seed_to_next_position_generically_nonlinear=True,semantics='source-wide gate-inert diagnostic; no candidate source change, no finite inference elevated to proof',seams=seams)
(r/'family-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
