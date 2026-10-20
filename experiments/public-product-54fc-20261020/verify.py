import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'parent';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((r/'SOURCE_FREEZE.json').read_text())
assert all(sha(t/p)==h for p,h in f['tracked_files'].items());assert not subprocess.check_output(['git','-C',str(t),'diff','--name-only']).strip()
h=sha(t/'ops.bin');result={'status':'EXACT_PUBLIC_NATIVE_STREAM_REPRODUCED'if h==f['expected_native_stream_sha256']else'PUBLIC_STREAM_HASH_MISMATCH','stream_sha256':h,'stream_bytes':(t/'ops.bin').stat().st_size,'source_archive_sha256':sha(r/'public-source.tar.gz'),'protected_files_checked':len(f['protected_files']),'no_new_score_or_statistical_gate':True}
(r/'REPRODUCTION.json').write_text(json.dumps(result,indent=2)+'\n');assert h==f['expected_native_stream_sha256'];print(json.dumps(result))
