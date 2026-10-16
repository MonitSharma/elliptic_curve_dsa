"""Check that preparation timings describe the frozen, row-identical fixture."""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile
base=Path(__file__).resolve().parents[2]/'experiments';root=base/'repair67-prep-profile-20261016';p=root/'evidence.tar.gz'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='c8b3551351a57a63d7eeb32edd8b16f53e09e10cca8842bdabc5494abcf56674'
with tarfile.open(p) as t,tarfile.open(base/'repair67-fused-filter-20261016/evidence.tar.gz') as old:
 names=t.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
 assert all(m.isfile() or m.isdir() for m in t.getmembers());read=lambda n:t.extractfile(n).read()
 manifest=json.loads(read('MANIFEST.json'));assert len(manifest['files'])==44
 for item in manifest['files']:
  raw=read(item['path']);assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256']
 prepared=json.loads(read('PREPARED_SOURCE.json'));assert len(prepared)==17
 for n,h in prepared.items():assert hashlib.sha256(read(n)).hexdigest()==h
 prior=json.load(old.extractfile('PREPARED_SOURCE.json'));assert set(prepared)==set(prior)|{'tool/src/profile.rs'}
 changed={n for n in prior if read(n)!=old.extractfile(n).read()}
 assert changed=={'tool/src/main.rs','tool/src/packed_body.rs','tool/src/fast_curve_c.rs','tool/src/rail_fast_ffi.rs'}
 assert b'const PROOF_ACCEPTED:bool=false;' in read('tool/src/packed_body.rs')
 def rows(a,n):
  rs=sorted(map(json.loads,a.extractfile(n+'.jsonl').read().splitlines()),key=lambda r:r['nonce']);assert len(rs)==4096 and [r['nonce']for r in rs]==list(range(1,4097))
  assert all(r['authoritative_rejection'] is False and r['proof_accepted'] is False for r in rs);return rs
 reference=rows(old,'fused-0');assert rows(t,'on')==rows(t,'off')==reference
 for name in ['on','off']:assert b'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS' in read(name+'.err')
 analysis=json.loads(read('ANALYSIS.json'));result=json.loads(read('RESULT.json'))
 metrics={v['name']:v for v in result['records'][1]['profile']['metrics']};assert len(metrics)==35
 assert metrics['prep_curve_C_paircall']['units']==metrics['prep_rail_C_walk']['units']==3139328
 assert metrics['prep_SHAKE_key_read']['units']==3139328*64
 for n,v in analysis['selected_worker_seconds'].items():assert metrics[n]['seconds']==v
 total=sum(analysis['selected_worker_seconds'].values());assert abs(total-analysis['selected_nonoverlap_worker_seconds'])<1e-8
 for n,v in analysis['selected_worker_fraction'].items():assert abs(v-analysis['selected_worker_seconds'][n]/total)<1e-12
 out=dict(status='INDEPENDENT_PROFILE_SOURCE_ALL_ROWS_AND_COUNTER_ARITHMETIC_PASS',archive_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),artifacts=44,prepared_source_files=17,row_comparisons=8192,scalar_pairs=3139328,startup_and_summed_worker_scopes_distinct=True,curve_worker_fraction=analysis['selected_worker_fraction']['prep_curve_C_paircall'],rail_worker_fraction=analysis['selected_worker_fraction']['prep_rail_C_walk'],limits='One instrumented loaded run; counters add overhead. No stable throughput gain, persistent-search time or production authority inferred.')
(root/'ROOT_TERMINAL_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
