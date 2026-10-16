import hashlib,json,statistics,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'scalar-fast-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert (ROOT/'run.exit').read_text().strip()=='0'
r=json.loads((ROOT/'RESULT.json').read_text());assert r['status']=='PASS' and len(r['results'])==12
decl=json.loads((ROOT/'DECLARATION.json').read_text())
for name,h in decl['pins'].items(): assert sha(BASE/name)==h
for name,h in decl['experiment_source_pins'].items(): assert sha(ROOT/name)==h
reference=(ROOT/'protected-reference.log').read_text()
assert 'REFERENCE_VALIDATED shots=4096 scalars=8192 coordinates=24576' in reference
summary=[]
for w in decl['windows']:
 trials=[x for x in r['results'] if x['window']==w];assert len(trials)==3
 summary.append({'window':w,'us_per_pair':[x['us_per_pair'] for x in trials],
 'median_us_per_pair':statistics.median(x['us_per_pair'] for x in trials),
 'initialization_s':[x['init_ns']/1e9 for x in trials],
 'rss_after_init_MiB':[x['rss_after_init_bytes']/2**20 for x in trials],
 'peak_rss_MiB':[x['max_rss_bytes']/2**20 for x in trials],
 'nominal_table_MiB':trials[0]['nominal_table_bytes']/2**20})
analysis={'status':'PASS_COMPONENT_ONLY','authority':False,'summary':summary,
 'interpretation':'All timings are the same fixed4096-pair corpus repeated32times, not newly sampled/fresh-input throughput. Python ctypes call-loop overhead is included. All coordinates checked outside every measured pass. Sequential isolated processes under shared machine load; no8-thread or persistent search forecast.',
 'controls':'All12cases equal all24576 protected Rust coordinates and explicit oldwindow20 byte output; empty/1/7/63/64partial and invalid65/u32MAX controls pass. Secondinit rejects.',
 'scope':'No library rebuild, table/window/production change, new nonce sampling, circuit change or search.'}
(ROOT/'ANALYSIS.json').write_text(json.dumps(analysis,indent=2)+'\n')
copies=['fixed_table.c','batch_table.c','validation-vectors.tsv','reference-validation.log','reference-hashes.sha256','verify-reference/src/main.rs','verify-reference/Cargo.toml','verify-reference/Cargo.lock','scalar_fast.c','build.sh','batch.sh']
for name in copies:
 p=ROOT/'provenance'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((BASE/name).read_bytes())
curve=BASE.parent/'overnight-20261014/product-b3-baseline/src/weierstrass_elliptic_curve.rs'
assert sha(curve)=='ecfca15ee3b831c243fbea559ff4b8937be47fe591a4f14786ec2b9bfb30bded'
(ROOT/'provenance/protected-curve.rs').write_bytes(curve.read_bytes())
refs={str(BASE/name):h for name,h in decl['pins'].items() if name in ['libscalar_fast_batch.so','verify-reference/target/release/product_paired_diagnostic']}
(ROOT/'SERVER-HASHREFS.json').write_text(json.dumps(refs,indent=2)+'\n')
files=[p for p in ROOT.rglob('*') if p.is_file() and p.name not in ['evidence.tar.gz','ARCHIVE-RECEIPT.json','MANIFEST.json']]
manifest={str(p.relative_to(ROOT)):sha(p) for p in files}
(ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(ROOT/'evidence.tar.gz','w:gz') as tar:
 for p in sorted(files+[ROOT/'MANIFEST.json']):tar.add(p,arcname=str(p.relative_to(ROOT)))
with tarfile.open(ROOT/'evidence.tar.gz','r:gz') as tar:
 for name,h in manifest.items():assert hashlib.sha256(tar.extractfile(name).read()).hexdigest()==h
receipt={'status':'VERIFIED','archive_sha256':sha(ROOT/'evidence.tar.gz'),'verified_members':len(manifest),'server_hashrefs':refs,'analysis_sha256':sha(ROOT/'ANALYSIS.json')}
(ROOT/'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
