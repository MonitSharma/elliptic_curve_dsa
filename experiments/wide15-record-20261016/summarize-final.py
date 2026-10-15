from pathlib import Path
import hashlib,json,math
root=Path(__file__).resolve().parent;e=root/'evidence';n=16384;rows=[];summary={'status':'diagnostic_final_fresh_census','label':'wide15-final-20261016','batches_each':n,'shots_each':n*64,'streams':{}}
for name,file in [('parent','final-parent-census.jsonl'),('candidate','final-census.jsonl')]:
 data=(e/file).read_bytes();r=[json.loads(x) for x in data.splitlines()];assert len(r)==n
 by={x['batch']:x for x in r};assert sorted(by)==list(range(n)) and all(x['shots']==64 for x in r)
 rows.append(by);failed=sum(bool(x['failures']) for x in r)
 summary['streams'][name]={'failed_batches':failed,'expected_failed_batches_per_packet':141*failed/n,'value_shots':sum(x['value_shots'] for x in r),'phase_shots':sum(x['phase_shots'] for x in r),'dirty_shots':sum(x['dirty_shots'] for x in r),'mean_executed_T':sum(x['toffoli'] for x in r)/(64*n),'census_sha256':hashlib.sha256(data).hexdigest()}
diff=[(rows[0][i]['toffoli']-rows[1][i]['toffoli'])/64 for i in range(n)];mean=sum(diff)/n
summary.update(paired_mean_T_saving=mean,saving_standard_error=math.sqrt(sum((x-mean)**2 for x in diff)/(n*(n-1))))
p,c=summary['streams']['parent'],summary['streams']['candidate']
summary['passes_final_failure_gate']=c['failed_batches']<=p['failed_batches'] and c['expected_failed_batches_per_packet']<=18 and c['dirty_shots']==0
(e/'final-census-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
result=json.loads((root/'RESULT.json').read_text());result.update(status='COMPLETE_LOCAL_PASS_QUEUE_ELIGIBLE' if summary['passes_final_failure_gate'] else 'COMPLETE_LOCAL_PASS_FINAL_CENSUS_GATE_FAILED',final_census=summary)
(root/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
