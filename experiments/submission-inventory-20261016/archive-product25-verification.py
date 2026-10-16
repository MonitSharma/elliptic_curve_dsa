"""Preserve terminal verification evidence; never execute or change a circuit."""
import hashlib
import io
import json
from pathlib import Path
import tarfile

root = Path('/home/hclau/ecdsa_research/product25-final-20261016')
assert (root / 'final.exit').read_text().strip() == '0'
assert (root / 'final-census.exit').read_text().strip() == '1'
assert json.loads((root / 'FINAL_CENSUS_RESULT.json').read_text())['status'] == 'FINAL_FRESH_CENSUS_FAIL'
freeze = json.loads((root / 'SOURCE_FREEZE.json').read_text())
files = {}
names = ['BENCHMARK_RESULT.json', 'NATIVE_RECEIPT.json', 'SOURCE_FREEZE.json', 'SEARCH_AUDIT.json',
         'FINAL-CENSUS-PLAN.json', 'FINAL_CENSUS_BINDING.json', 'FINAL_CENSUS_RESULT.json',
         'FINAL_CENSUS_INDEPENDENT_RECOUNT.json', 'finalize.py', 'final-census.py', 'run-final.sh',
         'run-final-census.sh', 'benchmark.log', 'benchmark-verification.log', 'native-tests.log',
         'native-verification.log', 'final-census.log', 'final.exit', 'final-census.exit',
         'point-add-source.tar.gz', 'candidate-source.patch', 'score.json', 'results.tsv',
         'benchmark-appended-row.tsv', 'VERIFY-RESUME-20261016.json']
for name in names:
    files[name] = root / name
for path in (root / 'final-fresh').iterdir():
    if path.is_file():
        files[str(path.relative_to(root))] = path
for name, expected in freeze['protected_files'].items():
    path = root / 'candidate' / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
    files['protected/' + name] = path
for name, expected in freeze['source_files'].items():
    assert hashlib.sha256((root / 'candidate' / name).read_bytes()).hexdigest() == expected
for name in ['build_circuit', 'eval_circuit']:
    files['native-binaries/' + name] = root / 'candidate/target/release' / name
runner_root = Path('/home/hclau/ecdsa_research/simd-census-v2-20261016')
files['census-runner/FREEZE.json'] = runner_root / 'FREEZE.json'
files['census-runner/simd_census_v2'] = runner_root / 'bin/simd_census_v2'
manifest = {name: dict(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            for name, path in files.items()}
manifest_raw = (json.dumps(manifest, indent=2) + '\n').encode()
archive = root / 'verification-terminal-evidence.tar.gz'
assert not archive.exists()
with tarfile.open(archive, 'w:gz', compresslevel=3) as dest:
    for name, path in files.items():
        dest.add(path, arcname=name, recursive=False)
    member = tarfile.TarInfo('MANIFEST.json')
    member.size = len(manifest_raw)
    dest.addfile(member, io.BytesIO(manifest_raw))
receipt = dict(status='FINAL_FAILURE_GATE_FAILED_EVIDENCE_PRESERVED', archive=archive.name,
               archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
               archive_bytes=archive.stat().st_size, files=len(files),
               external_stream_path=str(root / 'candidate/ops.bin'),
               external_stream_sha256=hashlib.sha256((root / 'candidate/ops.bin').read_bytes()).hexdigest(),
               benchmark_pass=True, final_failure_gate_pass=False, submission_performed=False)
(root / 'VERIFICATION_ARCHIVE_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
