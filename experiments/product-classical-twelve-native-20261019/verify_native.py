import hashlib,json,struct,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE_FREEZE.json').read_text());t=Path(f['candidate'])
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
assert all(sha(t/p)==h for p,h in f['source_files'].items());assert all(sha(t/p)==h for p,h in f['protected_files'].items())
actual={p.relative_to(t).as_posix() for p in (t/'src/point_add').rglob('*') if p.is_file()};assert actual==set(f['source_files'])
p=t/'ops.bin';header=p.open('rb').read(16);assert header[:8]==b'QECCOPSZ';assert struct.unpack_from('<Q',header,8)[0]==f['expected_ops']
binary=r.parent/'product-order-20261019/target/release/hash_classical_ops'
raw=subprocess.check_output([str(binary),str(p)],text=True).strip();assert raw==f['expected_raw_sha3_256']
result={'status':'NATIVE_COMPLETE_STREAM_IDENTICAL_TO_CONTROLLED_RESEARCH_CANDIDATE','ops':f['expected_ops'],'raw_sha3_256':raw,'compressed_sha256':sha(p),
        'source_archive_sha256':f['source_archive_sha256'],'source_files_checked':len(actual),'protected_files_checked':len(f['protected_files']),
        'scope':'Native source reproduction; no statistical gate, official benchmark or scored record yet.'}
(r/'NATIVE-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
