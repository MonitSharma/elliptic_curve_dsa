import concurrent.futures,json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent
def one(k):
    with (r/f'zero-{k}.log').open('wb') as f:subprocess.run([sys.executable,str(r/'prove_zero.py'),str(k)],stdout=f,stderr=subprocess.STDOUT,check=True)
    d=json.loads((r/f'zero-{k}-result.json').read_text());return {'lookback':k,'verdict':d['verdict'],'seconds':d['seconds']}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(one,(32,64,128,512,2048)))
(r/'ZERO-RESULT.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2),flush=True)
