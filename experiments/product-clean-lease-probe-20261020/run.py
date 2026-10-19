import hashlib,json,os,resource,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;os.chdir(r)
os.environ.update(OMP_NUM_THREADS='1',RAYON_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',ANF_PAIR_WITNESSES='0',ANF_LINEAR_WITNESSES='0')
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
b=json.loads((r/'BINDING.json').read_text());assert all(sha(r/p)==h for p,h in b['source_files'].items())
assert all(sha(Path(p))==h for p,h in b['compiler_and_direct_dependencies'].items())
profile=json.loads(subprocess.check_output(['python3',str(ws/'autonomous-20261019/preflight_v15.py')],env=dict(os.environ,RESEARCH_SLOTS='1'),text=True));(r/'preflight.json').write_text(json.dumps(profile,indent=2)+'\n')
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
compiler=next(p for p in b['compiler_and_direct_dependencies'] if p.endswith('/rustc'));deps=ws/'product-order-20261019/target/release/deps'
args=[compiler,'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','linker=/usr/bin/gcc','-C','link-arg=-fuse-ld=bfd','-L','dependency='+str(deps)]
for lib in ['quantum_ecc','sha3','serde_json','zstd']:
 paths=[p for p in b['compiler_and_direct_dependencies'] if Path(p).name.startswith('lib'+lib+'-')];assert len(paths)==1;args+=['--extern',lib+'='+paths[0]]
for source,expected in [('base',12),('probe',15)]:
 with (r/('build-tests-'+source+'.log')).open('xb') as f:subprocess.run(args+['--test',source+'.rs','-o',source+'-tests.bin'],stdout=f,stderr=subprocess.STDOUT,check=True)
 with (r/('tests-'+source+'.log')).open('xb') as f:subprocess.run(['./'+source+'-tests.bin','--test-threads=1'],stdout=f,stderr=subprocess.STDOUT,check=True)
 assert str(expected)+' passed; 0 failed' in (r/('tests-'+source+'.log')).read_text()
 with (r/('build-'+source+'.log')).open('xb') as f:subprocess.run(args+[source+'.rs','-o',source+'.bin'],stdout=f,stderr=subprocess.STDOUT,check=True)
inp=ws/'product-copy-cache-native-20261020/candidate/ops.bin';assert sha(inp)==b['input_compressed_sha256']
for source in ['base','probe']:
 with (r/(source+'.log')).open('xb') as f:subprocess.run(['/usr/bin/time','-v','./'+source+'.bin',str(inp),str(r/(source+'.json')),b['input_raw_sha3_256']],stdout=f,stderr=subprocess.STDOUT,check=True)
base=json.loads((r/'base.json').read_text());probe=json.loads((r/'probe.json').read_text());extra=probe.pop('lease_probe');assert base==probe,'No original report/output/counter may change'
assert sha(inp)==b['input_compressed_sha256']
(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_STRONG_CLEAN_LEASE_BOUNDARIES_AND_COMPLETE_BASELINE_CONTROL_PASS','base_tests':12,'probe_tests':15,'all_prior_report_fields_and_complete_output_identical':True,'source_files':b['source_files'],'binary_hashes':{name:sha(r/(name+'.bin')) for name in ['base','probe']},'first_full_state':extra['first_full_width_post_state'],'epochs':len(extra['epochs']),'uncovered_high_touches':extra['touches']-sum(e['touches'] for e in extra['epochs']),'no_idle_donor_epochs':sum(e['untouched_nonABI_donor_count']==0 for e in extra['epochs']),'gate_or_nonce_or_score':False},indent=2)+'\n');print((r/'RESULT.json').read_text(),flush=True)
