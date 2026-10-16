from pathlib import Path
import hashlib,json,os,re,statistics,subprocess,time
r=Path(__file__).resolve().parent;decl=json.load(open(r/'DECLARATION.json'));require=lambda c,m:None if c else(_ for _ in()).throw(ValueError(m))
require(os.environ.get('NUMA_BUDGET_RELEASED')=='ROOT_RELEASED','coordinator budget release required')
root=r.parents[1];binary=Path(decl['immutable_binary']);ops=root/'product-exact-20261015/candidate-product-final25/ops.bin';reference=root/'product-early-filter-20261016/rows4096.jsonl';model=root/'prefilter-20261015/model-source'
h=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
require(h(binary)==decl['binary_sha256'],'changed binary');require(h(ops)==decl['candidate_stream_sha256'],'changed stream');require(h(reference)==decl['reference4096_sha256'],'changed disabled reference')
require(os.sched_getaffinity(0)==set(range(144)),'unbound parent affinity is restricted')
policy=subprocess.check_output(['numactl','--show'],text=True);require('policy: default' in policy,'unbound parent policy is not default')
require('membind: 0 1 2 3' in policy,'unbound parent memory binding restricted')
ref=sorted(map(json.loads,reference.read_text().splitlines()),key=lambda x:x['nonce']);require(len(ref)==4096 and[x['nonce']for x in ref]==list(range(1,4097)),'invalid reference coverage');require(all(x['authoritative_rejection']is False and x['proof_accepted']is False for x in ref),'reference gate enabled')
runtime={str(binary):h(binary),str(ops):h(ops),str(reference):h(reference)}
for p in sorted(model.rglob('*')):
 if p.is_file():runtime[str(p)]=h(p)
(r/'before.json').write_text(json.dumps(runtime,indent=2)+'\n');start=time.monotonic();records=[]
def resources(name):
 hardware=subprocess.check_output(['numactl','--hardware'],text=True);free=int(re.search(r'node 3 free: (\d+) MB',hardware)[1]);mem=Path('/proc/meminfo').read_text();available=int(re.search(r'MemAvailable:\s+(\d+) kB',mem)[1]);require(free>=16384 and available>=120000000,'insufficient memory')
 ps=subprocess.check_output(['ps','-eo','pid,psr,nlwp,pcpu,rss,args','--sort=-pcpu'],text=True);(r/(name+'-resources.json')).write_text(json.dumps(dict(numa=hardware,mem_available_kb=available,node3_free_mb=free,processes=ps),indent=2)+'\n')
def sample(pid):
 try:
  status=Path(f'/proc/{pid}/status').read_text();numa=Path(f'/proc/{pid}/numa_maps').read_text();pages={i:sum(int(x)for x in re.findall(rf'\bN{i}=(\d+)',numa))for i in range(4)}
  return dict(pid=pid,allowed=[line for line in status.splitlines()if line.startswith(('Cpus_allowed_list:','Mems_allowed_list:','Threads:'))],numa_pages=pages)
 except FileNotFoundError:return None
for trial,order in enumerate(decl['mode_order']):
 paired=[]
 for mode in order:
  require(time.monotonic()-start<decl['deadline_seconds'],'whole benchmark deadline')
  name=f'{mode}-{trial}';resources(name);env=os.environ.copy()
  for key in ['FAST_ZERO_DISPATCH','DEFER_EXPECTED_SUMS','DEFER_SUM_SHADOW','PACKED_ZERO_SHADOW','CANDIDATE_SEED_SHADOW','EARLY_FULLSTATE_SHADOW','FORCE_FULL_FALLBACK','SCALAR_FAST_LIB','RAIL_SHADOW']:env.pop(key,None)
  for key in['OMP_NUM_THREADS','RAYON_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:env[key]='1'
  require('FAST_ZERO_DISPATCH'not in env,'FAST dispatch present')
  command=(["numactl","--cpunodebind=3","--membind=3"]if mode=='numa3'else[])+[str(binary),str(ops),'1','4096','4',str(r/(name+'.jsonl')),str(model),'4096'];samples=[];st=time.monotonic()
  with(r/(name+'.log')).open('w')as out,(r/(name+'.err')).open('w')as err:
   p=subprocess.Popen(command,env=env,stdout=out,stderr=err)
   try:
    while p.poll()is None:
     samples.append(sample(p.pid));require(time.monotonic()-st<decl['per_process_timeout_seconds'],'owned trial timeout');time.sleep(2)
   except BaseException:
    p.terminate()
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:p.kill();p.wait()
    raise
   require(p.returncode==0,f'trial failed {name}: {p.returncode}')
  log=(r/(name+'.log')).read_text();wall=float(re.search(r'wall_seconds=([0-9.]+)',log)[1]);rows=sorted(map(json.loads,(r/(name+'.jsonl')).read_text().splitlines()),key=lambda x:x['nonce']);require(rows==ref,f'complete4096 row identity failed {name}');require(all(x['authoritative_rejection']is False and x['proof_accepted']is False for x in rows),'gate enabled')
  canonical=(json.dumps(rows,sort_keys=True,separators=(',',':'))+'\n').encode();record=dict(trial=trial,mode=mode,wall_seconds=wall,total_subprocess_seconds=time.monotonic()-st,rows=4096,canonical_rows_sha256=hashlib.sha256(canonical).hexdigest(),source_binary_sha256=h(binary),FAST_ZERO_DISPATCH_present=False,process_locality_samples=samples,command=command);records.append(record);paired.append(record);(r/(name+'-receipt.json')).write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items()if k not in['process_locality_samples','command']}),flush=True)
 require(paired[0]['canonical_rows_sha256']==paired[1]['canonical_rows_sha256'],'paired rows differ')
require({p:h(p)for p in runtime}==runtime,'runtime inputs changed');(r/'after.json').write_text(json.dumps(runtime,indent=2)+'\n');times={mode:[x['wall_seconds']for x in records if x['mode']==mode]for mode in['unbound','numa3']};result=dict(status='DISABLED_NUMA_PAIRED_ROWS_IDENTICAL',times_seconds=times,median_seconds={mode:statistics.median(v)for mode,v in times.items()},paired_ratio=[next(x['wall_seconds']for x in records if x['trial']==i and x['mode']=='numa3')/next(x['wall_seconds']for x in records if x['trial']==i and x['mode']=='unbound')for i in range(3)],all4096_rows_identical=True,FAST_ZERO_DISPATCH_present=False,total_repeated_timing_attempts=24576,distinct_timing_nonces=4096,active_worker_affinity_changed=False,production_changed=False,proof_gate=False,nonce_selected=None)
(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
