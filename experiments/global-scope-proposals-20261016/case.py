from pathlib import Path
import hashlib,json,os,subprocess,sys
r=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['original4b','product95']
assert not (r/(case+'.exit')).exists()
e=r.parent/'product-exact-20261015'
if case=='original4b':source=e/'tip/ops.bin';expected='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
else:
    freeze=json.loads((e/'PRODUCT95_FREEZE.json').read_text());source=e/freeze['external_stream'];expected=freeze['external_stream_sha256']
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
env=dict(os.environ,CACHE_ATOM_CAP='512',CACHE_PRODUCT_CAP='1000000',CACHE_PAIR_CAP='64',CACHE_SPLIT='1',CACHE_RANK='density',EXACT_MODE='cache-retained')
(r/(case+'-INPUT.json')).write_text(json.dumps({'source':str(source),'sha256':expected,'settings':{k:env[k] for k in ['CACHE_ATOM_CAP','CACHE_PRODUCT_CAP','CACHE_PAIR_CAP','CACHE_SPLIT','CACHE_RANK']},'no_output_stream':True},indent=2)+'\n')
exe=r/'tool/target/release/product_paired_diagnostic'
with (r/(case+'.log')).open('w') as out:
    p=subprocess.run(['timeout','--signal=TERM','1800','prlimit','--as=17179869184','--',str(exe),str(source),str(r/'NEVER-EMIT.bin')],env=env,stdout=out,stderr=subprocess.STDOUT)
assert not (r/'NEVER-EMIT.bin').exists()
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
(r/(case+'.exit')).write_text(str(p.returncode)+'\n');print(case,p.returncode,flush=True)
