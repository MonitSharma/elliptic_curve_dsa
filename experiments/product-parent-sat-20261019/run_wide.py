import concurrent.futures,json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent
def one(k):
    with (r/f'wide-02-{k}.log').open('wb') as f:
        subprocess.run([sys.executable,str(r/'prove_wide.py'),'2',str(k)],stdout=f,stderr=subprocess.STDOUT,check=True)
    d=json.loads((r/f'wide-02-{k}-result.json').read_text());return {'lookback':k,'verdict':d['verdict'],'seconds':d['seconds'],'source_start':d['input']['start']}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(one,(16,64,256,1024,4096,16384,65536)))
(r/'WIDE-RESULT.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2),flush=True)
