"""Prepare source-bound fifth checkpoint; exclude active follow-up artifacts."""
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
CYCLE=ROOT/'experiments/overnight-20261014'
report=CYCLE/'product/h45-width57-r3-results.md'
body=report.read_bytes()
try:
    body.decode('utf8')
except UnicodeDecodeError:
    archive=report.with_name('h45-width57-r3-results-original.cp1252.gz')
    archive.write_bytes(gzip.compress(body,mtime=0))
    report.write_bytes(body.decode('cp1252').replace('\r\n','\n').encode('utf8'))
    (CYCLE/'product/report-encoding-provenance.json').write_text(json.dumps({'original_report_sha256':hashlib.sha256(body).hexdigest(),'archive':archive.name,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'readable_report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),'change':'CP1252 report converted to readableUTF8LF; exact original bytes preserved in gzip; no scientific content changed'},indent=2)+'\n',encoding='utf8')
p=CYCLE/'cycle.json';d=json.loads(p.read_text())
d['fifth_checkpoint']={'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'public_records':1562,'eligible_records':1221,'pareto_points':45,'records_changed':False,'public_refresh_utc':'2026-10-14T15:39:00Z','original_qualified_candidates':[],
 'new_public_reproduction':{'source':'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7','qubits':1235,'rounded_toffoli':761156,'product':940027660,'shots':9024,'value_phase_ancilla_failures':[0,0,0],'receipt':'coordinator/b3-reference-full-receipt.json'},
 'b3_classical_factor_candidate':{'status':'FAILED_UNCHANGED_FULL_BENCHMARK','classical_failures':15,'phase_batches':14,'ancilla_batches':0,'same_candidate_packet_MR_original_B3_final_state_identical':True,'source_patch':'coordinator/b3-classical-failed.patch','qualified_score':None},
 'headflag':{'all_measurement_fixed_instances':116,'generated_ops':3500369588,'generated_referenced_qubits':692,'generated_stream_sha256':'6b0046e2470cabf150fa6d2892e0b8206a683d3975b5d268cd7b80ed2cfdc902','status':'Waiting authorized sequential official evaluator queue; no qualified score'},
 'N274':'Ideal model clears18048original+512fresh; physical sixthq21 quotient owner unresolved; no source prototype or widthclaim',
 'guarded_support':'108067additional clean boundaries but1234peak; onlyoneidentityCCX, standaloneclosed',
 'carry_cleanup':'Fin3 actualdrop1 and narrowedfin4 actualtop1/2drops native+ALLMR pass; lazyfin3−7/8 component expectation passes, no globalrecord',
 'H45':'Actual105contexts/all13.6million fixedinput ALLMR and512incomingpointprefix proofs pass; 104admitted. Mean−14.1484375 sample component sum cannot bridge167gap, originalpeakoutsidechangedfolds. Closed standalone; no metadataadapter/fullcandidatebuilder.'}
d['jobs_at_fifth_checkpoint']=[{'native_pid':2534382,'kind':'Original N275-v2 unchanged official9024benchmark active','log':'/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-v2-official-eval.log','memory_limit_GiB':256,'runtime_threads':1,'qualified_score':None},
 {'pid':2612039,'kind':'Headflag officialevaluation queue waiting originalnative terminal; no head vector allocated','log':'/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/headflag-v1-official-cycle.log','memory_limit_GiB':256,'runtime_threads':1,'qualified_score':None}]
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
paths=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()+subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
excluded=('_v7','-v7','_v8','-v8','arithmetic-compare','stages-v2','stage-replay-v2','n274-v1','create-n274')
selected=sorted({s for s in paths if (s.startswith('experiments/overnight-20261014/')or s.startswith('scripts/')or s in('README.md','docs/data/latest-leaderboard.json','docs/frontier-results.md','docs/overnight-20261014.md'))and not any(x in s for x in excluded)})
for s in selected:
 file=ROOT/s;assert file.is_file(),s
 if file.suffix=='.json':json.loads(file.read_text(encoding='utf-8-sig'))
 if file.suffix=='.patch':
  text=file.read_text(encoding='utf8',errors='replace');changed=re.findall(r'^diff --git a/(.*?) b/(.*?)$',text,re.M)
  assert changed and all(a.startswith('src/point_add/')and b.startswith('src/point_add/')for a,b in changed),s
 if file.stat().st_size>2_000_000:raise RuntimeError('Unexpected oversized checkpoint:'+s)
out=ROOT/'research-output/overnight-20261014/fifth-stage-paths.json';out.write_text(json.dumps(selected,indent=2)+'\n',encoding='utf8')
print(json.dumps({'files':len(selected),'bytes':sum((ROOT/s).stat().st_size for s in selected),'excluded_active':[s for s in paths if any(x in s for x in excluded)],'stage_list':str(out)}))
