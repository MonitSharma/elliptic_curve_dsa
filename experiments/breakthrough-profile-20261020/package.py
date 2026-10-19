"""Seal the baseline observation audit, including exact original-replay control."""
import hashlib,json,re,statistics,math,subprocess,tarfile,shutil
from pathlib import Path
from datetime import datetime,timezone
r=Path(__file__).resolve().parent;t=r/'observer'
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
for name in ['run.exit','replay.exit','original-control.exit']:assert(r/name).read_text().strip()=='0'
freeze=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert all(sha(t/name)==digest for name,digest in{**freeze['source_files'],**freeze['protected_files']}.items())
assert sha(t/'ops.bin')==freeze['expected_final_stream_sha256']
phase=json.loads((r/'PHASE-PROFILE.json').read_text())
assert sha(t/'prepass.ops.bin')==phase['prepass_stream_sha256']
a=[json.loads(l)for l in(r/'phase-census.jsonl').read_text().splitlines()]
b=[json.loads(l)for l in(r/'original-replay.jsonl').read_text().splitlines()]
assert len(a)==len(b)==512 and[x['batch']for x in a]==list(range(512))
for x,y in zip(a,b):assert{k:v for k,v in x.items()if k!='regional_toffoli'}==y and sum(x['regional_toffoli'])==x['toffoli']
mapping=[line.split('\t')for line in(r/'phase-final.tsv').read_text().splitlines()]
mean=sum(x['toffoli']for x in a)/32768
cost={'status':'DIAGNOSTIC_EXECUTED_COST_PROFILE_NOT_A_NEW_SCORE','at_utc':datetime.now(timezone.utc).isoformat(),
 'label':'breakthrough-cost-profile-20261020-v1','batches':512,'shots':32768,'mean_executed_toffoli':mean,
 'phases':[{'phase':name,'mean_executed_toffoli':statistics.mean(x['regional_toffoli'][i]/64 for x in a),
            'standard_error':statistics.stdev(x['regional_toffoli'][i]/64 for x in a)/math.sqrt(512),
            'fraction_of_total':sum(x['regional_toffoli'][i]for x in a)/(mean*32768)}for i,(name,*_)in enumerate(mapping)],
 'value_failing_shots':sum(x['value_shots']for x in a),'phase_failing_shots':sum(x['phase_shots']for x in a),
 'dirty_shots':sum(x['dirty_shots']for x in a),'failed_batches':sum(bool(x['failures'])for x in a),
 'all_512_rows_match_unchanged_original_replay':True,'all_region_sums_match_exact_executed_totals':True}
(r/'EXECUTED-COST-PROFILE.json').write_text(json.dumps(cost,indent=2)+'\n')
log=(r/'generate.log').read_text();groups=[]
for count,phase_name,origin in re.findall(r'PEAK_OWN count=(\d+) phase=(\S+) caller=(\S+)',log):
 groups.append({'count':int(count),'phase':phase_name,'caller':origin})
assert sum(g['count']for g in groups)==1234
(r/'WORKSPACE-OWNERS.json').write_text(json.dumps({'status':'ADMITTED_BASELINE_FIRST_PEAK_OWNER_REPORT','peak_active':1234,'phase':'divide','groups':groups,'scope':'Build-time live ownership; not a lower bound or a reduced-width circuit.'},indent=2)+'\n')
copies=r/'added-source';copies.mkdir(exist_ok=False)
shutil.copyfile(t/'src/point_add/break_profile.rs',copies/'break_profile.rs')
compiler=subprocess.check_output(['/home/hclau/.cargo/bin/rustup','which','--toolchain','1.93.0','rustc']).decode().strip()
runtime={'rustc':compiler,'rustc_sha256':sha(Path(compiler)),'rustc_version':subprocess.check_output([compiler,'--version']).decode().strip(),
 'replay_binary_sha256':sha(r/'tool/target/release/phase-replay'),'mapper_binary_sha256':sha(r/'tool/target/release/map-phases'),
 'accepted_stream_sha256':sha(t/'ops.bin'),'prepass_stream_sha256':sha(t/'prepass.ops.bin'),
 'original_replay_binary_sha256':sha(r.parent/'simd-census-v2-20261016/bin/simd_census_v2'),
 'final_tool_source_files':{p.relative_to(r/'tool').as_posix():sha(p)for p in sorted((r/'tool').rglob('*'))if p.is_file()and'target'not in p.relative_to(r/'tool').parts}}
(r/'RUNTIME-BINDING.json').write_text(json.dumps(runtime,indent=2)+'\n')
files=[]
for p in sorted(r.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(r)
 if any(x in rel.parts for x in ['observer','target','__pycache__']):continue
 if p.name.endswith('.ops.bin')or p.name in ['evidence.tar.gz','EVIDENCE-MANIFEST.json','LOCAL-VERIFICATION.json']:continue
 if 'resource-preflight' in p.name:continue # Raw server process arguments stay server-side.
 files.append(p)
manifest={p.relative_to(r).as_posix():sha(p)for p in files}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':manifest,'streams_retained_on_server':runtime},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for p in files+[r/'EVIDENCE-MANIFEST.json']:archive.add(p,arcname=p.relative_to(r).as_posix())
receipt={'status':'BASELINE_COST_AND_WORKSPACE_AUDIT_SEALED','archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json'),'no_new_gate_nonce_or_score':True}
(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
