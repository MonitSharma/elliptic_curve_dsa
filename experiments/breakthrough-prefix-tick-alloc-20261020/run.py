import hashlib,json,os,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'observer';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();os.environ['PEBBLE_HARD_CAP']='1234'
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','build_circuit'],'build');streams={}
 for mode in ['control','mixed']:
  dest=r/mode;dest.mkdir();run([str(t/'target/release/build_circuit')],'generate-'+mode,dest,dict(os.environ,BREAK_TICK_MODE=mode));assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items());streams[mode]=sha(dest/'ops.bin')
  if mode=='control':assert streams[mode]=='13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b'
 comparisons=[]
 for tick in[129,130]:
  a=json.loads((r/'control'/f'tick-{tick}-allocation.json').read_text());b=json.loads((r/'mixed'/f'tick-{tick}-allocation.json').read_text());held=lambda s:set(range(s['next_bit']))-set(s['free_bits']);comparisons.append({'tick':tick,'live_quantum_roles_equal':a['roles']==b['roles'],'active_qubit_counts_equal':a['active']==b['active'],'free_qubit_sets_equal':sorted(a['free_qubits'])==sorted(b['free_qubits']),'free_qubit_orders_equal':a['free_qubits']==b['free_qubits'],'held_classical_bit_sets_equal':held(a)==held(b),'free_classical_orders_equal':a['free_bits']==b['free_bits'],'next_classical_counter_equal':a['next_bit']==b['next_bit'],'role_differences':sum(x!=y for x,y in zip(a['roles'],b['roles'])),'source_snapshots_sha256':{'control':sha(r/'control'/f'tick-{tick}-allocation.json'),'mixed':sha(r/'mixed'/f'tick-{tick}-allocation.json')}})
 (r/'RESULT.json').write_text(json.dumps({'status':'RAW_ALLOCATION_INTERFACE_DIAGNOSTICS_NOT_SCORED','stream_sha256':streams,'comparisons':comparisons,'scope':f['scope']},indent=2)+'\n');(r/'run.exit').write_text('0\n');print(json.dumps(comparisons),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\n');raise
