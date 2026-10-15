"""Report diagnostic changes only; never assign failed candidates a score."""
from pathlib import Path
import re,json,hashlib
root=Path(__file__).resolve().parent
parents={'narrow':{'q':1282,'independent':197312724,'structured':197306887,'candidate':6954670332},'wide':{'q':1464,'independent':192951219,'structured':192951488,'candidate':6801646424}}
rows={}
for mode in parents:
 assert int((root/(mode+'.exit')).read_text())==0
 generation=(root/(mode+'-generation.log')).read_text();peak=int(re.search(r'HEO_TOTAL .*? peak=(\d+)',generation)[1]);families={}
 for family in ['independent','structured','candidate']:
  log=(root/(mode+'-'+family+'.log')).read_text();line=next(l for l in log.splitlines() if l.startswith('FIXED_DIAGNOSTIC'))
  data={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)};data['wrong_indices']=list(map(int,re.findall(r'FINAL_BAD shot=(\d+)',log)))
  data['diagnostic_mean_delta_vs_parent']=(data['diagnostic_only_total_executed_t']-parents[mode][family])/data['shots'];families[family]=data
 phase=(root/(mode+'-phase.log')).read_text();rows[mode]={'score':None,'builder_peak_diagnostic_only':peak,'families':families,'phase_lines':[l for l in phase.splitlines() if l.startswith(('FULL_PHASE','BDD_WITNESS','PHASE_ORIGIN','PHASE_WITNESS','BDD_NATIVE','SINGLE_MEASUREMENT'))],'stream_sha256':(root/(mode+'-stream.sha256')).read_text().split()[0]}
result={'status':'both candidates fail qualification','score':None,'candidates':rows,'limitations':['Fixed diagnostic inputs, not an official benchmark.','Measurement events differ between streams: count changes are not an event-aligned savings proof.','Observed phase counts do not establish monotone correctness improvement.','Full BDD/native witness audit covers the first fixed zero-slope input only.']}
(root/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
