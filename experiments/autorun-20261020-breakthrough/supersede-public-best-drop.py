"""Stop only idle obsolete follow-ons; preserve initial finite search and gate."""
import hashlib,json,os,signal,socket,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ws=Path('/home/hclau/ecdsa_research');cont=ws/'breakthrough-public-best-drop-nonce-continuation-20261020';final=ws/'breakthrough-public-best-drop-final-20261020';initial=ws/'breakthrough-public-best-drop-nonce-v2-20261020';assert socket.gethostname()=='LHC-104-070'
with urllib.request.urlopen('https://api.ecdsa.fail/api/submissions/1829986e-675c-4fbf-bb28-22f2f95246c4',timeout=60)as response:public=json.load(response)
s=public['submission'];assert s['status']=='accepted'and s['officialScore']==932057476 and s['officialMetrics']=={'qubits':1234,'toffoli':755314};assert not(final/'candidate').exists()and not(final/'UPLOAD-STARTED.json').exists();assert not(cont/'SEARCH-RESULT.json').exists()and not list(cont.glob('production-*.jsonl'));assert not(initial/'run.exit').exists()
expected={3074390:str(cont/'run.py'),3078510:str(final/'watch.py'),3078511:str(final/'finalize.py')}
cmdlines={}
for pid,path in expected.items():
 command=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0');assert command[0].endswith(b'python3')and command[1].decode()==path,(pid,command);cmdlines[pid]=[x.decode()for x in command if x]
reason={'at_utc':datetime.now(timezone.utc).isoformat(),'status':'SUPERSEDED_BEFORE_CONTINUATION_OR_BENCHMARK_BY_NEW_PUBLIC_PRODUCT_RECORD','new_public_record':{k:s[k]for k in['id','officialMetrics','officialScore','submissionCommitSha']},'preserved_gate':'PASS remains final against exact publicacd0; no rerun/relabel or rejudgment','candidate_source_unchanged':True,'continuation_production_screens':0,'benchmark_attempts':0,'challenge_upload_attempts':0,'initial_finite_search':'Original1..65536 may complete unchanged; no infinite continuation or current-record claim. Preserve all completed screens and any protected historical packet result.','stopped_idle_processes':cmdlines,'scope':'Stop only verified idle follow-on processes. Current finite exact search, verifier controls/audits, unrelated jobs and chemistry untouched. Next work reproduces freshpublic3eef and constructs a new exact candidate with its own fresh declared gate.'}
for r in[cont,final]:
 assert not(r/'SUPERSEDED.json').exists();(r/'SUPERSEDED.json').write_text(json.dumps(reason,indent=2)+'\n');(r/'NEW-PUBLIC-RECORD.json').write_text(json.dumps(public,indent=2)+'\n')
for pid in[3074390,3078511,3078510]:os.kill(pid,signal.SIGTERM)
(cont/'superseded.exit').write_text('143\n');(final/'superseded.exit').write_text('143\n');(final/'review.exit').write_text('1\n');print(json.dumps(reason),flush=True)
