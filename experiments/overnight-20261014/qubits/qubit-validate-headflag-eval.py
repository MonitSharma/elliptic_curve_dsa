"""Fail-closed allocation/source guards outside the protected evaluator."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
root=Path('/home/hclau/ecdsa_research/overnight-20261014/qubits')
stream=root/'evidence/headflag-v1-ops.bin'
stream_sha='6b0046e2470cabf150fa6d2892e0b8206a683d3975b5d268cd7b80ed2cfdc902'
patch_sha='1792f88c69567b403aaf84e1bd9122f179d06c4e6db29de0c17440bef226b243'
N=3500369588
mode=sys.argv[1]
assert mode in ('reserve','evaluate','launch')
limit=268435456*1024
previous=root/'evidence/n275-v2-official-eval-native.exit'
assert previous.exists(),'prior native exit marker is required before any vector allocation'
previous_status=int(previous.read_text().strip())
ps=subprocess.check_output(['ps','-eo','pid=,rss=,comm=,args='],text=True)
large=[]
for line in ps.splitlines():
    words=line.strip().split(None,3)
    if len(words)<4:continue
    pid,rss,comm,args=words
    if comm=='eval_circuit' or ('/home/hclau/ecdsa_research' in args and int(rss)>16*1024**2):
        large.append(dict(pid=int(pid),rss_kib=int(rss),comm=comm,args=args))
assert not large,('another ECDSA evaluator/large process exists',large)
for name in ['headflag-v1-full-build.exit','headflag-v1-harness-build.exit']:
    assert (root/'evidence'/name).read_text().strip()=='0',name
m=json.loads((root/'evidence/headflag-v1-stream-metadata.json').read_text())
assert (m['ops'],m['referenced_qubits'],m['sizeof_op'],m['op_vec_bytes'])==(N,692,56,N*56)
need=N*56+16*2**30
pre=subprocess.check_output(['python3','/home/hclau/ecdsa_research/server-preflight.py'],text=True)
(root/f'evidence/headflag-v1-{mode}-preflight.json').write_text(pre)
pre=json.loads(pre)
assert need<limit and need<pre['memory']['MemAvailable_bytes'],(need,limit,pre['memory']['MemAvailable_bytes'])
with stream.open('rb')as file:
    header=file.read(16)
assert header[:8]==b'QECCOPSZ'and int.from_bytes(header[8:],'little')==N
def digest(path):
    h=hashlib.sha256()
    with path.open('rb')as file:
        while chunk:=file.read(4*1024**2):h.update(chunk)
    return h.hexdigest()
assert digest(stream)==stream_sha
candidate=json.loads((root/'evidence/candidate-headflag-v1-manifest.json').read_text())
assert candidate['patch_sha256']==patch_sha and digest(root/'evidence/candidate-headflag-v1.patch')==patch_sha
source=Path(candidate['checkout'])
assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==candidate['base_revision']
changed=subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines()
assert sorted(changed)==sorted(candidate['candidate_changed_paths'])and all(p.startswith('src/point_add/')for p in changed)
for relative,expected in candidate['source_sha256'].items():assert digest(source/relative)==expected,relative
trusted=json.loads((root/'evidence/headflag-v1-protected-harness-manifest.json').read_text())
harness=Path(trusted['checkout'])
assert harness==root/'harness-headflag-v1'
assert subprocess.check_output(['git','-C',str(harness),'rev-parse','HEAD'],text=True).strip()==trusted['base_revision']
for relative,expected in trusted['protected_source_sha256'].items():assert digest(harness/relative)==expected,relative
assert not subprocess.check_output(['git','-C',str(harness),'status','--porcelain'],text=True).strip()
assert digest(harness/'target/release/eval_circuit')==trusted['protected_binary_sha256']=='8333555d82603e07c735e56db12cf8ce9c6355c92f2afa2ce7670ec3b8578a18'
assert not(harness/'results.tsv').exists()and not(harness/'score.json').exists()
if mode=='launch':
    assert (harness/'ops.bin').is_symlink()and(harness/'ops.bin').resolve()==stream.resolve()
else:
    assert not os.path.lexists(harness/'ops.bin')
assert digest(root/'stream-resource-meta/target/release/qubit_stream_resource_meta')=='e0a15f3bf58d0e7731321fded824962cf3a4ff6c07dc4556553960ce6efe042e'
if mode in ('evaluate','launch'):
    reserved=json.loads((root/'evidence/headflag-v1-stream-reserved-metadata.json').read_text())
    assert reserved['measured_loader_vec_capacity']==N and reserved['sizeof_op']==56 and reserved['ops']==N
    if mode=='evaluate':(harness/'ops.bin').symlink_to(stream)
    assert(harness/'ops.bin').resolve()==stream.resolve()
receipt=dict(scope='External allocation/source guards only; unchanged protected evaluator',mode=mode,prior_native_status=previous_status,stream_sha256=stream_sha,patch_sha256=patch_sha,N=N,sizeof_op=56,op_vec_bytes=N*56,need_plus_margin_bytes=need,virtual_cap_bytes=limit,available_bytes=pre['memory']['MemAvailable_bytes'],other_large_ECDSA_processes=large,protected_binary_sha256=trusted['protected_binary_sha256'],input_path=str(harness/'ops.bin'),resolved_stream=str(stream),placeholder_used=False,historical_outputs_absent_before=True)
(root/f'evidence/headflag-v1-{mode}-attestation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,sort_keys=True))
