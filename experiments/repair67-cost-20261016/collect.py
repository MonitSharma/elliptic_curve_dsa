from pathlib import Path
import hashlib,io,json,tarfile
root=Path(__file__).resolve().parent
assert (root/'run.exit').read_text().strip()=='0'
result=json.loads((root/'RESULT.json').read_text())
assert result['status']=='DISABLED_FOUR_PROCESS_TIMING_AND_COMPLETE_ROWS_PASS'
assert len(result['trials'])==4 and result['total_rows_with_repetitions']==65536
assert not result['additional_search_authority']
archive=root/'evidence.tar.gz';assert not archive.exists()
files=[p for p in sorted(root.iterdir()) if p.is_file() and p.name not in ['ARCHIVE-RECEIPT.json','evidence.tar.gz']]
manifest={'files':{p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in files},'external_pins':json.loads((root/'LAUNCH_BINDINGS.json').read_text()),'scope':'Complete timing evidence; disabled filter and no nonce selection.'}
with tarfile.open(archive,'w:gz') as t:
 for p in files:t.add(p,arcname=p.name,recursive=False)
 raw=(json.dumps(manifest,indent=2)+'\n').encode();info=tarfile.TarInfo('manifest.json');info.size=len(raw);t.addfile(info,io.BytesIO(raw))
with tarfile.open(archive) as t:
 for n,v in manifest['files'].items():assert hashlib.sha256(t.extractfile(n).read()).hexdigest()==v['sha256']
receipt=dict(status='TERMINAL_COMPLETE_TIMING_ARCHIVE',archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size,files=len(files),runtime_external_artifacts=len(manifest['external_pins']['artifacts']))
(root/'ARCHIVE-RECEIPT.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
