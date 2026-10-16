from pathlib import Path
import json,re,collections,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');assert(r/'all-add-replay.exit').read_text().strip()=='0';assert(r/'all-add-stream-source-before.sha256').read_bytes()==(r/'all-add-stream-source-after.sha256').read_bytes()
lines=(r/'all-add-replay.log').read_text().splitlines();batches=[l for l in lines if l.startswith('ATTR_BATCH ')];shots=[l for l in lines if l.startswith('PAY_SHOT ')];assert len(batches)==413 and len(shots)==431;assert all('full64q_b_phase_T_equal=true original_census_flags_reproduced=true'in l for l in batches);assert all('final_bad=true'in l for l in shots)
events=[dict(re.findall(r'(\w+)=([^ ]+)',l))for l in lines if l.startswith('ADD_EVENT ')];groups=collections.Counter((x['phase'],x['tick'],x['rev'])for x in events);byshot=collections.defaultdict(list)
for x in events:byshot[int(x['shot'])].append(x)
out=dict(status='TERMINAL SAME431/413 ALL786 ADD INTERFACE REPLAY PASS',no_new_sampling=True,no_candidate=True,all_original_q_b_phase_T_and_failure_masks_reproduced=True,source_before_after_identical=True,log_sha256=hashlib.sha256((r/'all-add-replay.log').read_bytes()).hexdigest(),events=len(events),shots_with_local_add_mismatch=len(byshot),by_phase_tick_rev=[dict(phase=p,tick=int(t),rev=v=='true',events=n)for(p,t,v),n in sorted(groups.items())],remaining_shot38243_local_add_events=byshot.get(38243,[]),all_events=events)
(r/'ALL-ADD-ATTRIBUTION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='all_events'},indent=2))
