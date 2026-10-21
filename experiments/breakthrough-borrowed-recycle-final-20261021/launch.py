import subprocess,json
from pathlib import Path
r=Path('/home/hclau/ecdsa_research/breakthrough-borrowed-recycle-final-20261021');assert not(r/'pipeline.pid').exists()
with(r/'pipeline.log').open('xb')as out:p=subprocess.Popen(['nohup','python3','-u',str(r/'run.py')],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
(r/'pipeline.pid').write_text(str(p.pid)+'\n');print(json.dumps({'pid':p.pid,'scope':'Wait for own first gate PASS, new exact engine qualification, ascending lowestnonce search, selected complete protected replay, unchanged benchmark. No upload until independent local source/evidence/strict-current-improvement review.'}))
