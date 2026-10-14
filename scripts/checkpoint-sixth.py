"""Stage-list preparation for completed sixth evidence and frozen running sources."""
import datetime
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
CYCLE=ROOT/'experiments/overnight-20261014'
p=CYCLE/'cycle.json';d=json.loads(p.read_text())
d['sixth_checkpoint']={'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'public_refresh_utc':'2026-10-14T17:46:43Z','public_records':1562,'eligible_records':1221,'pareto_points':45,'records_changed':False,
 'original_qualified_candidates':[],
 'n275_v2':{'status':'FAILED_UNCHANGED_COMPLETE_BENCHMARK','shots':9024,'value_phase_ancilla_failures':[1,1,1],'first_value_failure':2379,'exit':1,'qualified_score':None,'receipt':'coordinator/n275-v2-full-failed-receipt.json'},
 'failed_packet_integer_model':{'shot2379_division2':'HTcol86 quotient22815568 needs25bits; exceeds public23 and mixed22 capacity','predicted_candidate_flagged_divisions':1,'scope':'Ideal event prediction, not inherited/introduced gate-level proof'},
 'headflag':{'native_pid':2662310,'status':'Unchanged official9024benchmark ACTIVE; no qualified score','only_giant_evaluator':True},
 'n274_v4':{'patch_sha256':'d471e44041f41919516f10ae5a472bd91a6ca91cf306dcb6ebb063799400e9e0','native_tests':18,'exact_phase_tests':15,'exact_fixed_input_audits':378,'status':'FullgenerationACTIVE; new25bitquotient counterexample requires repair before officialqualification','no_scored_width_claim':True},
 'constructor':'v8/v9/v11 selected89/236/256 interfaces negative; exact3-product prefix survives butcompletionnegative; v12parallel2-product trustedUNSAT. Changedconsumer v13–v16 exactalgebra andselectedfamiliesnegative; no implementedfull saving.',
 'product_localization':'Exact Y33 transform corrects oldprefixmapping failure. Native249 firstmultiplyfault; native8033 B3firstdividefault. Finite unboundedinteger tick model identifies249 rail109 loss2^57,8033 payload75 difference2^51. No resourcecandidate.',
 'global_controls_and_recolor':'Initial classicalABI initialization failure preserved/retracted. Correct immutableBoolean scan only3equal-controlCCXs; boundedANF findsnone; exact-zero recolor stillpeak1234 at1444991. Standaloneclosed.'}
d['jobs_at_sixth_checkpoint']=[
 {'native_pid':2662310,'kind':'Sole large unchanged headflag officialbenchmark','log':'/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/headflag-v1-official-eval.log','memory_limit_GiB':256,'runtime_threads':1,'qualified_score':None},
 {'pid':2691773,'native_pid':2692372,'kind':'N274-v4 fullgeneration; officialevaluation gated on newquotientcounterexample','log':'/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n274-v4-full-build.log','memory_limit_GiB':16,'build_threads':4,'runtime_threads':1},
 ]
d['sixth_checkpoint']['fixed_packet_export']={'status':'COMPLETE_DIAGNOSTIC_EXIT0','pid':2679094,'native_pid':2680130,'shots':9024,'packet_sha256':'bdba0f9ac464903dc9838cc2c05f7120f31941937226167f0a406e122dd4ec7d','elapsed':'12:55.20','native_export_RSS_KiB':10368,'operation_vector_allocated':False}
d['sixth_checkpoint']['n274_v4']['status']='GENERATION_COMPLETE_DIAGNOSTIC_KNOWN2379_FAILURE_BLOCKS_QUALIFICATION'
d['sixth_checkpoint']['n274_v4']['generated_diagnostics']={'ops':2258490788,'referenced_qubits':691,'stream_sha256':'afc10211f95bd28a131dfd4a3a3c67284597c308b2a8a2e10682e56207f8ba93','scope':'Generated stream only, not a scored or qualified resource result'}
d['jobs_at_sixth_checkpoint']=[job for job in d['jobs_at_sixth_checkpoint']if job.get('native_pid')!=2692372]
p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
paths=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
paths+=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
paths+=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines()
excluded=('fold75','rail109','quotient25','cap25','high-q25','2379-regression','2379-base-regression','diag2379')
def deferred(s):
    return any(x in s for x in excluded)or bool(re.search(r'[_-]v(?:1[7-9]|[2-9][0-9])(?:[_\-.]|$)',s))
selected=sorted({s for s in paths if (s.startswith('experiments/overnight-20261014/')or s.startswith('scripts/')or s in('README.md','docs/data/latest-leaderboard.json','docs/figures/frontier.png','docs/frontier-results.md','docs/research-plan.md','docs/SERVER_HANDOFF.md','docs/overnight-20261014.md'))and not deferred(s)})
for s in selected:
    file=ROOT/s;assert file.is_file(),s
    if file.suffix=='.json':json.loads(file.read_text(encoding='utf-8-sig'))
    if file.suffix=='.patch':
        changed=re.findall(r'^diff --git a/(.*?) b/(.*?)$',file.read_text(encoding='utf8',errors='replace'),re.M)
        assert changed and all(a.startswith('src/point_add/')and b.startswith('src/point_add/')for a,b in changed),s
    assert file.stat().st_size<=2_000_000,('Unexpected oversized evidence',s,file.stat().st_size)
out=ROOT/'research-output/overnight-20261014/sixth-stage-paths.json';out.write_text(json.dumps(selected,indent=2)+'\n',encoding='utf8')
print(json.dumps({'files':len(selected),'bytes':sum((ROOT/s).stat().st_size for s in selected),'excluded_active':[s for s in paths if deferred(s)]}))
