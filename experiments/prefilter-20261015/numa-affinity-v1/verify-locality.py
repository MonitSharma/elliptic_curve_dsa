from pathlib import Path
import json
r=Path(__file__).parent;result=json.load(open(r/'RESULT.json'));assert result['status']=='DISABLED_NUMA_PAIRED_ROWS_IDENTICAL'
probe=(r/'bound-policy-probe.txt').read_text();assert 'policy: bind' in probe and 'membind: 3' in probe
expected=set(range(54,72))|set(range(126,144))
def expand(text):
 out=set()
 for part in text.split(','):
  ends=list(map(int,part.strip().split('-')))
  out.update(range(ends[0],ends[-1]+1))
 return out
checks=[]
for trial in range(3):
 for mode in['unbound','numa3']:
  x=json.load(open(r/f'{mode}-{trial}-receipt.json'));samples=[]
  for s in x['process_locality_samples']:
   if not s:continue
   fields={key.strip():value.strip()for line in s['allowed']for key,_,value in[line.partition(':')]}
   cpus=expand(fields['Cpus_allowed_list']);mems=expand(fields['Mems_allowed_list']);wantcpus=expected if mode=='numa3'else set(range(144));wantmems=set(range(4));valid=cpus==wantcpus and mems==wantmems
   samples.append((valid,s))
  assert samples and samples[-1][0],f'final actual process affinity mismatch{mode}/{trial}'
  after_first_match=False
  for valid,s in samples:
   if valid:after_first_match=True
   if after_first_match:assert valid,'binding unexpectedly changed after verified exec'
  final=samples[-1][1];peak=max((s for valid,s in samples if valid),key=lambda s:sum(s['numa_pages'].values()));pages={int(k):v for k,v in peak['numa_pages'].items()};total=sum(pages.values());
  if mode=='numa3':assert pages[3]/total>.95,'node3 did not hold dominant resident pages'
  checks.append(dict(mode=mode,trial=trial,samples=len(samples),last_allowed=final['allowed'],last_numa_pages=pages,node3_page_fraction=pages[3]/total if total else None,actual_affinity_verified=True))
report=dict(status='ACTUAL_CHILD_CPU_BINDING_NODE3_RESIDENCY_AND_POLICY_PROBE_VERIFIED',Mems_allowed_list_is_cgroup_limit_not_numactl_policy=True,matching_numactl_probe_policy='bind3',checks=checks,active_worker_affinity_changed=False,production_changed=False)
(r/'LOCALITY_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
