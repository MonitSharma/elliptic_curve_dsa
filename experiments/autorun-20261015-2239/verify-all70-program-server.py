"""Read-only binary structure/source-sidecar check, not a new semantic proof."""
from pathlib import Path
from collections import Counter
import hashlib,json,resource,struct
resource.setrlimit(resource.RLIMIT_AS,(4*2**30,4*2**30))
root=Path('/home/hclau/ecdsa_research/all70-mask-feasibility-20261016')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
side=json.loads((root/'EXPORT-METADATA-CLARIFICATION.json').read_bytes())
assert sha((root/'EXPORT-METADATA-CLARIFICATION.json').read_bytes())=='bfd68eae7215bfadaa0222b62203ec5cf6dc12c987af30ba6084c4282b07d485'
program=(root/'mr-mask-all70.bin').read_bytes();assert sha(program)==side['program_sha256']
raw=(root/'mr-mask-all70.json').read_bytes();assert sha(raw)==side['raw_export_manifest_sha256']
manifest=json.loads(raw)
assert program[:8]==b'MRMASK01';nodes,inputs,outputs=struct.unpack_from('<3Q',program,8)
assert (nodes,inputs,outputs)==(7918169,1024,512)
assert len(program)==32+nodes*16+outputs*4
assert struct.unpack_from('<I',program,32)[0]==0 and struct.unpack_from('<I',program,48)[0]==1
kinds=Counter()
for i,(kind,a,b,aux) in enumerate(struct.iter_unpack('<4I',memoryview(program)[32:32+nodes*16])):
    assert kind in range(6);kinds[kind]+=1
    if kind==2:assert a<inputs
    elif kind>=3:assert a<i and b<i
roots=struct.unpack_from('<512I',program,32+nodes*16)
assert list(roots)==manifest['dependency_roots'] and all(r<nodes for r in roots)
counts=Counter('constant0' if r==0 else 'constant1' if r==1 else 'nonconstant' for r in roots)
assert counts=={'constant1':332,'nonconstant':180}
for name,digest in side['authoritative_fresh_binding'].items():assert sha((root/name).read_bytes())==digest
source=Path('/home/hclau/ecdsa_research/product-exact-20261015/candidate-all70-base/ops.bin')
assert sha(source.read_bytes())==side['evaluated_source_stream_sha256']=='06cdc5de3dadbe23a2ff306466ec2ef27514bed53be1145ec83bdf490cb99a7a'
assert manifest['original_stream_sha256'].startswith('2a522394') # invalid legacy label, never authoritative here
out=dict(status='ROOT_ALL_BINARY_NODES_ROOTS_AND_FRESH_SOURCE_SIDECAR_STRUCTURE_PASS',
         source_sha256=side['evaluated_source_stream_sha256'],program_sha256=sha(program),sidecar_sha256=sha((root/'EXPORT-METADATA-CLARIFICATION.json').read_bytes()),
         nodes=nodes,inputs=inputs,outputs=outputs,node_kinds=dict(kinds),root_kinds=dict(counts),
         children_strictly_earlier=True,all_roots_match_raw_export=True,
         invalid_legacy_2a_label_not_used_for_binding=True,no_new_semantic_proof_or_runtime_authority=True)
(root/'ROOT_PROGRAM_STRUCTURE_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
