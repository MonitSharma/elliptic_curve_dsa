"""Verify all four-process timing rows; keep startup and program timers distinct."""
from pathlib import Path,PurePosixPath
import hashlib,json,re,statistics,tarfile
root=Path(__file__).resolve().parents[2]/'experiments/repair67-cost-20261016'
p=root/'evidence.tar.gz';receipt=json.loads((root/'ARCHIVE-RECEIPT.json').read_text())
assert hashlib.sha256(p.read_bytes()).hexdigest()==receipt['archive_sha256']=='65f6dc1f99d22808038c73aa107e698c8e850d4c72ad4e40c102e42f1f2cd10a'
with tarfile.open(p) as t:
 names=t.getnames();assert len(names)==len(set(names));assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
 assert all(m.isfile() or m.isdir() for m in t.getmembers())
 read=lambda n:t.extractfile(n).read()
 manifest=json.loads(read('manifest.json'));assert len(manifest['files'])==87
 for n,v in manifest['files'].items():
  raw=read(n);assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'],n
 assert read('run.exit').strip()==b'0'
 results=json.loads(read('RESULT.json'));assert len(results['trials'])==4 and results['cost_gate_pass'] is False and results['additional_search_authority'] is False
 ref=None;proxies=[]
 for trial,mode in enumerate(['raw','fused','fused','raw']):
  combined=[];walls=[]
  for worker in range(4):
   stem=f'trial{trial}-{mode}-worker{worker}';assert read(stem+'.exit').strip()==b'0'
   rows=sorted(map(json.loads,read(stem+'.jsonl').splitlines()),key=lambda v:v['nonce'])
   first=1+worker*4096;assert len(rows)==4096 and [r['nonce'] for r in rows]==list(range(first,first+4096))
   assert all(r['proof_accepted'] is False and r['authoritative_rejection'] is False for r in rows)
   assert b'CANDIDATE_OWN_FIAT_PROTECTED_4096_BYTE_CONTROLS_PASS' in read(stem+'.err')
   walls.append(float(re.search(rb'wall_seconds=([0-9.]+)',read(stem+'.log'))[1]));combined.extend(rows)
  if ref is None:ref=combined
  else:assert combined==ref
  r=results['trials'][trial];assert r['program_wall_seconds']==walls and r['mode']==mode
  assert abs(r['aggregate_nonces_per_second']-16384/r['elapsed_seconds_including_startup'])<1e-9
  assert abs(r['forecast_mean_hours']-181165677.0769668*r['elapsed_seconds_including_startup']/16384/3600)<1e-8
  proxies.append(dict(trial=trial,mode=mode,max_program_timer_seconds=max(walls),program_timer_only_forecast_hours=181165677.0769668*max(walls)/16384/3600))
 out=dict(status='INDEPENDENT_ALL_65536_ROWS_AND_FIXED_COST_PROTOCOL_PASS',archive_sha256=receipt['archive_sha256'],artifacts=87,unique_timing_nonces=16384,semantic_rows_compared=65536,complete_4process_8thread_scope=True,restart_inclusive_forecast_hours=results['forecast_mean_hours'],program_timer_only_proxies=proxies,gate_pass=False,proposal_remains_disabled=True,limitation='Restart-inclusive forecast repeats one-time source hashing/compilation/library startup per4096 rows. Program-timer proxies remove observed startup but do not measure persistent-worker warm throughput. Neither is a64-thread measurement; no extrapolated launch authority.',no_nonce_selected=True,no_new_census=True)
(root/'ROOT_TERMINAL_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
