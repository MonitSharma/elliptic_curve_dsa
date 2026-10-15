from pathlib import Path
import json,collections
r=Path('/home/hclau/ecdsa_research/phase-localization-20261016')
rows=[json.loads(l)for l in(r/'trace.jsonl').read_text().splitlines()]
traces=[{0:0,**dict(row['trace'])}for row in rows]
def delta(a,b):return [t[a]^t[b]for t in traces]
folds=json.loads((r.parent/'precision-repair-20261016/surviving-folds.json').read_text())['rows']
out=[]
for f in folds:
 if not f.get('found'):continue
 a=f['final_start'];b=a+f['ops'];d=delta(a,b)
 if any(d):out.append(dict(kind='fold',reverse=f['reverse'],tick=f['tick'],start=a,end=b,phase_delta_shots=sum(x.bit_count()for x in d),masks=[f'{x:016x}'for x in d]))
for name in['complete-helper-proof-spans.tsv','phase-lifetime-proof-spans.tsv','expanded-lifetime-proof-spans.tsv']:
 for line in(r.parent/'prefilter-macro-20261016/additional'/name).read_text().splitlines():
  if not line.strip():continue
  a,b=map(int,line.split()[:2]);d=delta(a,b)
  if any(d):out.append(dict(kind=name,start=a,end=b,phase_delta_shots=sum(x.bit_count()for x in d),masks=[f'{x:016x}'for x in d]))
summary=dict(seeds=len(rows),shots=64*len(rows),phase_shots=sum(int(x['phase_hex'],16).bit_count()for x in rows),value_shots=sum(int(x['value_hex'],16).bit_count()for x in rows),nonzero_regions=len(out),regions=out,protected_all_state_checks=all(x['protected_all_q_b_phase_rng_stats_equal']for x in rows))
(r/'phase-region-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print({k:v for k,v in summary.items()if k!='regions'})
for row in sorted(out,key=lambda x:-x['phase_delta_shots'])[:50]:print({k:v for k,v in row.items()if k!='masks'})
print('FOLDS')
for row in out:
 if row['kind']=='fold':print({k:v for k,v in row.items()if k!='masks'})
print('COARSE_CUMULATIVE')
for i in sorted(traces[0]):
 if i%1_000_000<20_000 or i==11630716:print(i,sum(t[i].bit_count()for t in traces))
