"""Freeze a source-only proposal; run pure fixture tests, never build/launch."""
from pathlib import Path
import hashlib,json,difflib,subprocess,sys,tarfile,io
r=Path(__file__).resolve().parent
old=r.parent/'product25-operational-20261016'
assert not (r/'tool').exists() and not (r/'ACCEPTANCE.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p,j):p.write_bytes((json.dumps(j,indent=2)+'\n').encode())
p=r/'DECLARATION.json';j=json.loads(p.read_text());j['GiB_per_worker_max']=12;j['aggregate_worker_GiB_max']=48
j['memory_reason']='Worst-case4096 packets retain about7.1GB point triples plus actual source/zeroIR/compact programs, curve table and protected pass-copy. Resource preflight must leave at least100GiB available.'
j['deadline']='Stop starting new windows five minutes before24h; at24h kill only owned child Popen workers still active. Any killed worker prevents prefix certification.'
js(p,j)
p=r/'coordinator.py';s=p.read_text().replace("receipt['aggregate_memory_GiB_max']==24","receipt['aggregate_memory_GiB_max']==48").replace('6*1024**3,6*1024**3','12*1024**3,12*1024**3');p.write_bytes(s.encode())
p=r/'search.rs';s=p.read_text().replace('row["aggregate_memory_GiB_max"],24','row["aggregate_memory_GiB_max"],48');p.write_bytes(s.encode())
p=r/'ACCEPTANCE-REQUIREMENTS.json';j=json.loads(p.read_text())
j['resource_gate']={'worker_processes':4,'threads_each':2,'total_threads':8,'GiB_per_process':12,'aggregate_GiB_limit':48,'minimum_available_GiB_after_reservation':100,'failure_disposition':'Any child abort, nonzero exit, missing row or incomplete window prevents completed-prefix/lowest-pass certification; preserve all evidence and never infer omitted rejections.'}
j['strict_nonce_bounds']='First and exclusive global end checked within[1,2^48], every represented nonce strictly below2^48; checked arithmetic in Rust window_start and fixed partition cap.'
j['runtime_binding_fields'].append('required_runtime_artifacts_manifest_sha256')
j['full_pass_shots']='Operational transform asserts protected_shots==9024 immediately before record_pass; partial official result can never create pass evidence.'
js(p,j)
(r/'test-terminal-audit.py').write_bytes((old/'test-terminal-audit.py').read_bytes())
p=r/'audit-terminal.py';p.write_bytes(p.read_text().replace("2**63-1,'nonce'","2**48-1,'nonce'").encode())
binding=json.loads((r.parent/'repair67-conditional-filter-20261016/COMPOSITE_BINDING.json').read_text())
runtime=binding['artifacts']+[
 {'path':'/home/hclau/ecdsa_research/product-exact-20261015/repair-to67-rank-20261016/repair-67-retained-1024-proxy.bin','sha256':'0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b'},
 {'path':'/home/hclau/ecdsa_research/prefilter-20261015/evidence/mr-mask-tip-v3-fused.bin','sha256':'1ccbbfc4a45b8d359be9ce21eb4640c72bb9bfe9bffb35f5630c0d13da3f2f8a'},
 {'path':'/home/hclau/ecdsa_research/prefilter-20261015/libmask_fused.so','sha256':'dc8219ae84c21e244ec0e1b92a14e9d0705faf7ebced04a2663499a75a6af1a0'},
 {'path':'/home/hclau/ecdsa_research/zero-mr-slice-20261016/tip.compact16.bin','sha256':'812f706d2edd7e821ff6c5f72db5e7e65b3f9756f562d99c1d0e1fceb007daf0'},
 {'path':'/home/hclau/ecdsa_research/zero-mr-slice-20261016/libzero8_slice.so','sha256':'84b73bcdee01bb537d0320f9985a682758d1076860455ad382a2ae175690ea82'},
 {'path':'/home/hclau/ecdsa_research/mask-evaluator-20261016/libmask8.so','sha256':'641f8c1b6578c9878244650bd05cbbbd1fd452e9199c504bc76832cf72fd81e1'},
 {'path':'/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so','sha256':'3bb2304219fb336795ea88d4bf81174883cdd33702f5975819b812c3dffca30f'},
 {'path':'/home/hclau/ecdsa_research/rail-masks-20261016/librail8_masks.so','sha256':'046dd5f1d11386550ec5234b955f6bc1974431e79a6b80499bda97da0ade3e90'},
 {'path':'/home/hclau/ecdsa_research/shake8-20261015/libshake8.so','sha256':'41296c5587a62a131f89a84b242e15dd9200d5bd43d2c52a9ab86088b4b9fac6'}]
js(r/'REQUIRED_RUNTIME_ARTIFACTS.json',{'status':'REQUIRED_FUTURE_ACCEPTANCE_PINS_NOT_AUTHORITY','artifacts':runtime,'acceptance_must_pin_proposal_and_final_binary_separately':True})
for script in ['test-source-proposal.py','test-terminal-audit.py']:
 subprocess.run([sys.executable,str(r/script)],check=True)
baseline=['prepare.py','search.rs','coordinator.py','run-search.sh','audit-terminal.py']
diff=''.join(''.join(difflib.unified_diff((old/n).read_text().splitlines(True),(r/n).read_text().splitlines(True),fromfile='active25/'+n,tofile='repair67-proposal/'+n))for n in baseline)
(r/'SOURCE-DIFF.patch').write_bytes(diff.encode())
receipt={'status':'FROZEN_SOURCE_ONLY_PROPOSAL_NO_PREPARE_BUILD_LAUNCH_AUTHORITY','active25_reference_files':{n:sha(old/n)for n in baseline},'proposal_files':{p.name:sha(p)for p in sorted(r.iterdir())if p.is_file() and p.name!='PROPOSAL-SOURCE-RECEIPT.json'},'tool_prepared':False,'binary_built':False,'acceptance_created':False,'search_launched':False}
js(r/'PROPOSAL-SOURCE-RECEIPT.json',receipt)
archive=r.parent/'prefilter-20261015/evidence-repair67-operational-source-proposal-v2.tar.gz';assert not archive.exists()
files=[p for p in r.iterdir()if p.is_file()]
manifest={'status':receipt['status'],'files':[{'path':p.relative_to(r).as_posix(),'sha256':sha(p)}for p in sorted(files)]}
with tarfile.open(archive,'w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 data=(json.dumps(manifest,indent=2)+'\n').encode();info=tarfile.TarInfo('MANIFEST.json');info.size=len(data);t.addfile(info,io.BytesIO(data))
with tarfile.open(archive)as t:
 for row in manifest['files']:assert hashlib.sha256(t.extractfile(row['path']).read()).hexdigest()==row['sha256']
print(json.dumps({'receipt_sha256':sha(r/'PROPOSAL-SOURCE-RECEIPT.json'),'archive_sha256':sha(archive),'files':len(files)}))
