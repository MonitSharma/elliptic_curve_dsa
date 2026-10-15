"""Read-only compact source-bound progress and completed proof receipts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,sys
r=Path('/home/hclau/ecdsa_research/q692_readiness_20261015')
def text(name):
 p=r/name;return p.read_text(encoding='utf8',errors='replace')if p.exists()else''
result=dict(collected_utc=datetime.now(timezone.utc).isoformat(),scope='Research diagnostics/proofs; no changed candidate full benchmark has qualified',jobs={},variants={})
for name in ['components-v1','phase-v1','counter-v1','components-v2','differential-v2','differential-v2-repair','components-v3','primitive-v3','generate-v3','generate-v3-r2','cache-v4','components-v5','components-v6','rotation-v6','generate-v6','normal-benchmark-v6','components-v7','reflection-v7','failed-packet-v6','failed-packet-v6-r2','fixed-input-replay-v6','policy-census-v8','components-v8','large25-v8','components-v9','fixed-column-v9','fixed-column-v9-r2','fixed-column-v9-r4','fixed-column-v9-r5','map-limit-v9','independent-policy-v9','generate-v9','fixed-replay-v9','independent-curves-v9','fixed-packet-v9','validate-v9-sequence']:
 result['jobs'][name]=dict(pid=text(name+'.pid').strip()or None,exit=text(name+'.exit').strip()or None)
for name in ['frozen','control-fold-v1','control-fold-v2','control-fold-v3','control-fold-v4','control-fold-v5','control-fold-v6','control-fold-v7','control-fold-v9']:
 log=text('counter-'+name+'.log');count=re.findall(r'^COUNT_SINK (.+)$',log,re.M)
 top=re.findall(r'LOWQ_EXACT_STREAM Q=(\d+) T=(\d+) N=(\d+) width=(\d+)',log)
 entry=dict(component_profiles=[json.loads(s)for s in re.findall(r'^PROFILE (.+)$',text('profile-'+name+'.log'),re.M)],whole_count=json.loads(count[-1])if count else None,top=list(map(int,top[-1]))if top else None,profile={key:dict(calls=int(c),emitted_t=int(t))for key,c,t in re.findall(r'^F1_PROFILE (\S+) calls=(\d+) emitted_t=(\d+)',log,re.M)})
 if name!='frozen':
  version=name.split('-')[-1];entry['native_tests']=re.findall(r'test result: ok\. (\d+) passed; 0 failed',text('components-'+version+'.log'))[:5]
  entry['phase_tests']=re.findall(r'test result: ok\. (\d+) passed; 0 failed',text('phase-'+version+'-proof.log'))
  entry['fixed_input_all_measurement_audits']=text('phase-'+version+'-proof.log').count('DECISION_DIAGRAM_PHASE_PROOF')
  entry['differential_pass']=re.findall(r'DIFFERENTIAL_PASS cases=(\d+)',text('differential-'+version+'-proof.log'))
  if version=='v2':entry['differential_pass']=re.findall(r'DIFFERENTIAL_PASS cases=(\d+)',text('differential-v2-repair-proof.log'))
 result['variants'][name]=entry
result['primitive_v3']=re.findall(r'PRIMITIVE_PASS cases=(\d+)',text('primitive-v3-proof.log'))
result['rotation_v6']=dict(pass_cases=re.findall(r'ROTATION_PASS cases=(\d+)',text('rotation-v6-proof.log')),profiles=re.findall(r'ROTATION_PROFILE (.+)',text('rotation-v6-proof.log')))
result['reflection_v7']=dict(pass_cases=re.findall(r'REFLECTION_PASS cases=(\d+)',text('reflection-v7-proof.log')),profiles=re.findall(r'REFLECTION_PROFILE (.+)',text('reflection-v7-proof.log')))
log=text('normal-benchmark-v6-official.log')
result['normal_v6']=dict(status='FAILED'if 'correctness FAILED:'in log else'PENDING',shots=re.findall(r'tested shots\s*:\s*(\d+)',log),value_failures=re.findall(r'classical mismatches\s*:\s*(\d+)',log),phase_batches=re.findall(r'phase-garbage batches\s*:\s*(\d+)',log),ancilla_batches=re.findall(r'ancilla-garbage batches\s*:\s*(\d+)',log),first_reason=re.findall(r'correctness FAILED: (.+)',log),elapsed=re.findall(r'Elapsed \(wall clock\) time[^:]+:\s*(.+)',log),max_rss_kib=re.findall(r'Maximum resident set size \(kbytes\):\s*(\d+)',log),canonical_score_exists=(r/'clean-replay-v6-binary/score.json').exists(),scope='complete unchanged normal benchmark; failed, unscored')
result['stream_v6']=dict(metadata=re.findall(r'LOWQ_EXACT_STREAM Q=(\d+) T=(\d+) N=(\d+) width=(\d+)',text('stream-v6-generation.log')),sha256=text('stream-v6.sha256').strip()or None)
result['stream_v3']=dict(metadata=re.findall(r'LOWQ_EXACT_STREAM Q=(\d+) T=(\d+) N=(\d+) width=(\d+)',text('stream-v3-generation.log')),sha256=text('stream-v3.sha256').strip()or None)
result['stream_v9']=dict(metadata=re.findall(r'LOWQ_EXACT_STREAM Q=(\d+) T=(\d+) N=(\d+) width=(\d+)',text('stream-v9-generation.log')),sha256=text('stream-v9.sha256').strip()or None)
for label,path in [('fixed_original','fixed-input-original-vs-v6.json'),('fixed_v6','fixed-input-v6-replay.json'),('fixed_v9','fixed-input-v9-replay.json'),('independent_curves_v9','independent-curves-v9-result.json')]:
 p=r/path
 if p.exists():
  v=json.loads(p.read_text(encoding='utf8'));result[label]={key:v[key] for key in ['scope','physical_ops','fixed_failed_shots','lanes','value_mismatch_lanes','phase_word','ancilla_garbage']}
p=r/'independent-policy-v9.json'
if p.exists():result['independent_policy_v9']={k:v for k,v in json.loads(p.read_text(encoding='utf8')).items()if k!='flagged'}
result['fixed_column_v9']=re.findall(r'FIXED_COLUMN_SUITE_PASS cases=(\d+)',text('fixed-column-v9-r5-proof.log'))
result['map_limit_v9']=re.findall(r'MAP_LIMIT_PASS (.+)',text('map-limit-v9-proof.log'))
result['file_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(r.iterdir())if p.is_file()and(p.name.endswith(('.log','.py','.sh','.patch','.json')))}
print(json.dumps(result,indent=2))
