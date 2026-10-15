"""Reconstruct the repeated-root wrapper and every compiled node on this machine."""
from pathlib import Path,PurePosixPath
import hashlib,json,struct,tarfile
experiments=Path(__file__).resolve().parents[2]/'experiments'
root=experiments/'guard-fused-20261016';data=root/'root-data'
sha=lambda b:hashlib.sha256(b).hexdigest()
archive_path=experiments/'prefilter-20261015/evidence-guard-fused-component.tar.gz'
assert sha(archive_path.read_bytes())=='5bfa6909f40b996b46a10be82657c728511149d0240a75f0e960c224456e0a53'
with tarfile.open(archive_path) as archive:
    names=archive.getnames();assert len(names)==len(set(names))
    assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
    manifest=json.load(archive.extractfile('MANIFEST.json'))
    for item in manifest['files']:
        payload=archive.extractfile(item['path']).read();assert sha(payload)==item['sha256'],item['path']
        if item.get('size') is not None:assert len(payload)==item['size']
    assert len(manifest['files'])==25
raw=(experiments/'prefilter-20261015/a29-conditional-prefix-v1/public-discrepancy-guard.bin').read_bytes()
assert sha(raw)=='355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3'
assert raw[:8]==b'MRMASK01' and struct.unpack_from('<QQQ',raw,8)==(1831784,1024,1)
wrapper=raw[:24]+struct.pack('<Q',512)+raw[32:-4]+raw[-4:]*512
assert sha(wrapper)=='5477d190d11716b0769d0d1c681b49368549345e095a71c85fae871e48e14375'
assert sha(raw[32:-4])=='aaa3f81c453595867a4d69875001ee1bccc07a61b273ad96ce52713b02bc514c'
(data/'guard512.bin').write_bytes(wrapper)
assert sha((data/'guard-fused.bin').read_bytes())=='e889e0a6f123a7ae34a9d81339a209ba93aad5246b224057107de3360a9c578a'
assert sha((data/'guard-fused.nodeids-u32le.bin').read_bytes())=='60f66061b25cc6b1a4ef7fb4873e0bc77eb84c1017ce53bdb0068fed79d1a91b'
checker=(root/'verify-mask-fused.py').read_bytes()
assert sha(checker)=='4c26cccb620c0787ee57d2422a91891c8eb9a2b1468990b29a6f422bee233801'
original=(experiments/'prefilter-20261015/verify-mask-fused.py').read_bytes()
assert sha(original)=='a04f42de78d3306256bf968278496295e2c27430937a8ceb1dd916c0c0e046b0'
reconstructed=checker.replace(b"prefix=r/'guard-fused'",b"prefix=r/'evidence/mr-mask-tip-v3-fused'").replace(b"r/'guard512.bin'",b"r/'evidence/mr-mask-tip-v3.bin'").replace(b"r/'whole-plan-verification.json'",b"r/'evidence/mask-fused-verification.json'")
assert reconstructed.replace(b'\r\n',b'\n')==original.replace(b'\r\n',b'\n')
# The complete independently authored structural checker runs unchanged in a
# private data directory; its output cannot replace the frozen server receipt.
namespace={'__file__':str(data/'verify-mask-fused.py'),'__name__':'__main__'}
exec(compile(checker,str(data/'verify-mask-fused.py'),'exec'),namespace)
receipt=json.loads((data/'whole-plan-verification.json').read_text())
assert receipt['instructions']==1130985 and receipt['slots']==1656 and receipt['negative_controls']==5
assert receipt['source_sha256']==sha(wrapper) and receipt['plan_sha256']==sha((data/'guard-fused.bin').read_bytes())
out=dict(status='ROOT_FULL_LOCAL_COMPILED_GUARD_NODE_RECONSTRUCTION_AND_WRAPPER_EQUIVALENCE_PASS',component_archive_sha256=sha(archive_path.read_bytes()),archived_files=25,raw_guard_sha256=sha(raw),wrapper_sha256=sha(wrapper),plan_sha256=receipt['plan_sha256'],nodeids_sha256=receipt['nodeids_sha256'],instructions=1130985,slots=1656,all_original_node_identities_reconstructed=True,private_checker_identical_except_three_paths_and_line_ending_normalization=True,negative_controls=5,source_function_for_all1024bit_inputs_identical=True,no_runtime_or_search_authority=True)
(root/'ROOT_FUNCTION_RECONSTRUCTION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
