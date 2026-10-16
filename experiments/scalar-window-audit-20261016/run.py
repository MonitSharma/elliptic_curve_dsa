import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'scalar-fast-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
decl=json.loads((ROOT/'DECLARATION.json').read_text())
assert decl['order']==[[20,13,16,18],[18,16,13,20],[13,20,18,16]]
for name,h in decl['pins'].items(): assert sha(BASE/name)==h,(name,sha(BASE/name))
verifier=BASE/'verify-reference/target/release/product_paired_diagnostic'
with (ROOT/'protected-reference.log').open('w') as log:
 subprocess.run([str(verifier),str(BASE/'validation-vectors.tsv')],stdout=log,stderr=subprocess.STDOUT,check=True)
results=[]
for trial,order in enumerate(decl['order']):
 for window in order:
  start=time.monotonic()
  with (ROOT/f'trial-{trial}-{window}.log').open('w') as log:
   subprocess.run([sys.executable,str(ROOT/'worker.py'),str(window),str(trial)],stdout=log,stderr=subprocess.STDOUT,check=True)
  r=json.loads((ROOT/f'trial-{trial}-{window}.json').read_text());r['process_elapsed_s']=time.monotonic()-start
  results.append(r)
  print(f'trial={trial} window={window} us_per_pair={r["us_per_pair"]:.6f} init_s={r["init_ns"]/1e9:.6f}',flush=True)
baseline=(ROOT/'output-0-20.bin').read_bytes()
for r in results: assert (ROOT/f'output-{r["trial"]}-{r["window"]}.bin').read_bytes()==baseline
for name,h in decl['pins'].items(): assert sha(BASE/name)==h
(ROOT/'RESULT.json').write_text(json.dumps({'status':'PASS','all_outputs_equal_old20_and_preserved_protected_Rust':True,'results':results,'authority':False},indent=2)+'\n')
print('TERMINAL_PASS all12completeoutputs_equal protected_Rust_and_window20',flush=True)
