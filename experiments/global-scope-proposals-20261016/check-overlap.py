from pathlib import Path
import json
r=Path(__file__).resolve().parent;answer={}
for case in ['original4b','product95']:
    report=json.loads((r/(case+'-BOUND-AUDIT.json')).read_text());by_donor={}
    for p in report['plans']:by_donor.setdefault(p['donor'],[]).append(p)
    overlaps=[]
    for donor,plans in by_donor.items():
        plans.sort(key=lambda p:(p['start'],p['new_end']))
        # New leases must be disjoint. Retaining an earlier old endpoint can
        # overlap more than just its immediate neighbor; inspect every overlap.
        for i,a in enumerate(plans):
            if i+1<len(plans):assert a['new_end']<=plans[i+1]['start']
            for b in plans[i+1:]:
                if b['start']>=a['old_LCA_end']:break
                overlaps.append({'donor':donor,'old_lease_start':a['start'],'old_cleanup':a['old_LCA_end'],
                    'next_start':b['start'],'next_proxy_only':b['source_proxy_only']})
    selected_proxy=sum(p['source_proxy_only'] for p in report['plans'])
    answer[case]={k:v for k,v in report.items() if k!='plans'}
    answer[case].update(selected_proxy_only=selected_proxy,joint_old_same_donor_lifetime_overlaps=overlaps,
        joint_old_overlap_count=len(overlaps),all_selected_new_intervals_disjoint=True,
        no_generator_or_measured_T_claim=True)
(r/'JOINT-BOUND-REVIEW.json').write_text(json.dumps(answer,indent=2)+'\n')
print(json.dumps({case:{k:v for k,v in row.items() if k!='joint_old_same_donor_lifetime_overlaps'} for case,row in answer.items()}))
