"""Generate the PRODUCT179 search phase (filter qualification, operational search, finalization)
from the verified PRODUCT95 scripts by explicit binding substitutions. Runs on the server only
after phase A wrote a PASS gate. Every substitution must apply at least once where listed."""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path

ws = Path('/home/hclau/ecdsa_research'); px = ws / 'product-exact-20261015'; nd = ws / 'product179-native-20261017'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
gate = json.loads((nd / 'GATE.json').read_text()); assert gate['status'] == 'FAILURE_GATE_PASS' and all(gate['rules'].values())
ident = json.loads((nd / 'NATIVE_IDENTITY.json').read_text()); assert ident['status'] == 'NATIVE_BYTE_IDENTITY_PASS'
freeze = json.loads((px / 'PRODUCT179_FREEZE.json').read_text())
S = freeze['external_stream_sha256']; assert S == ident['generated'] == gate['candidate_stream_sha256']
N = freeze['resources']['ops']; assert freeze['resources']['qubits'] == 1234
STREAM = freeze['external_stream']; assert STREAM.startswith('product-to179-rank-20261017/')
cert = px / 'cache-certificate179-20261017'
c = json.loads((cert / 'CACHE_EQUIVALENCE_CERTIFICATE.json').read_text()); assert c['stage_count'] == 179 and c['candidate_stream_sha256'] == S
# frozen native source archive for finalization
tree = nd / 'candidate'; arc = nd / 'point-add-source.tar.gz'
if not arc.exists():
    subprocess.run(['tar', 'czf', str(arc), 'src/point_add'], cwd=tree, check=True)
nfiles = int(subprocess.check_output(f"tar tzf {arc} | grep -vc '/$'", shell=True, text=True).strip())
ndirs = int(subprocess.check_output(f"tar tzf {arc} | grep -c '/$'", shell=True, text=True).strip())
frozen_bin = sha(tree / 'src/point_add/frozen_cache_product179.bin')

S95 = 'ba87b9ceb0691ccfe8c509539cfc38e774ee02134363c19e3541c6e942723e84'
common = [
    (S95, S), ('20_275_836', f'{N:_}'),
    ('product-to95-rank-20261016/product-95-retained-1024-proxy.bin', STREAM),
    ('cache-certificate95-20261017', 'cache-certificate179-20261017'),
    ('product95-filter-20261017', 'product179-filter-20261017'),
    ('plain95-operational-20261017', 'plain179-operational-20261017'),
    ('plain95-final-20261017', 'plain179-final-20261017'),
    ('product95-native-20261017', 'product179-native-20261017'),
    ('frozen_cache_product95', 'frozen_cache_product179'),
    ('candidateba87b9ce universal95stage', f'candidate{S[:8]} universal179stage'),
    ('product95-gate-20261017-v1', 'product179-gate-20261017-v1'),
    ('universal95', 'universal179'), ('PRODUCT95', 'PRODUCT179'), ('95-stage', '179-stage'),
]

def conv(src, dst, extra=(), required=()):
    s = Path(src).read_text()
    for a, b in list(extra):
        assert a in s, (src, a); s = s.replace(a, b)
    for a, b in common:
        s = s.replace(a, b)
    for a in required:
        assert a in s, (dst, a)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(s)

# 1. filter qualification
f95, f179 = ws / 'product95-filter-20261017', ws / 'product179-filter-20261017'
for n in ['prepare.py', 'run.py', 'run.sh']:
    conv(f95 / n, f179 / n)
# 2. operational search (4 workers x up to 24 threads)
o95, o179 = ws / 'plain95-operational-20261017', ws / 'plain179-operational-20261017'
conv(o95 / 'prepare.py', o179 / 'prepare.py', extra=[("replace('threads<=32','threads<=14')", "replace('threads<=32','threads<=24')")])
conv(o95 / 'search.rs', o179 / 'search.rs', required=[S])
conv(o95 / 'build.sh', o179 / 'build.sh')
conv(o95 / 'prepare-all.sh', o179 / 'prepare-all.sh')
conv(o95 / 'control.py', o179 / 'control.py')
conv(o95 / 'coordinator.py', o179 / 'coordinator.py', extra=[
    ("threads=int(os.environ.get('SEARCH_THREADS_EACH','14'));assert 1<=threads<=14", "threads=int(os.environ['SEARCH_THREADS_EACH']);assert 14<=threads<=24")])
conv(o95 / 'run-search.sh', o179 / 'run-search.sh', extra=[('SEARCH_THREADS_EACH=14', 'SEARCH_THREADS_EACH=$(cat threads-each.txt)')])
conv(o95 / 'audit_tool_diff.py', o179 / 'audit_tool_diff.py', extra=[
    ('    ("candidate268aefe2 universal67stage", "candidateba87b9ce universal95stage"),\n]',
     '    ("candidate268aefe2 universal67stage", "candidateba87b9ce universal95stage"),\n    ("threads<=14", "threads<=24"),\n]')])
acc = (o95 / 'accept.py').read_text()
old_gate = acc[acc.index('gate = read(native_dir / "GATE.json")'):acc.index('qual = read(')]
acc = acc.replace(old_gate, 'gate = read(native_dir / "GATE.json")\nassert gate["candidate_stream_sha256"] == S95 and gate["label"] == "product95-gate-20261017-v1" and gate["batches"] == 32768\nassert gate["status"] == "FAILURE_GATE_PASS" and all(gate["rules"].values())\n')
acc = acc.replace('lam = gate["verdicts"]["plain67_final"]["failed_batches_per_packet"]["candidate"]', 'lam = gate["failed_batches_per_packet"]["candidate"]')
acc = acc.replace('threads = 56', 'threads = int((root / "threads-each.txt").read_text()) * 4')
acc = acc.replace('c["stage_count"] == 95', 'c["stage_count"] == 179')
(o179 / 'accept.tmpl.py').write_text(acc)
conv(o179 / 'accept.tmpl.py', o179 / 'accept.py', required=['c["stage_count"] == 179', S]); (o179 / 'accept.tmpl.py').unlink()
# 3. finalization
fz95, fz179 = ws / 'plain95-final-20261017', ws / 'plain179-final-20261017'
conv(fz95 / 'finalize.py', fz179 / 'finalize.py', extra=[
    ("archive_hash = 'd0927ba5ffd51c3ba0e75403dff6fd6ab5463b35653483188c5a8c91e655a7d2'", f"archive_hash = '{sha(arc)}'"),
    ("frozen_bin_hash = '13e7881703be5a698361950cab5edd9a1a8e4d21909806ec30f0bd4469a3533f'", f"frozen_bin_hash = '{frozen_bin}'"),
    ("assert sum(m.isfile() for m in members) == 168", f"assert sum(m.isfile() for m in members) == {nfiles}"),
    ("(native / 'point-add-source.tar.gz')", "(native / 'point-add-source.tar.gz')")], required=[f'{N:_}', S])
conv(fz95 / 'audit-terminal.py', fz179 / 'audit-terminal.py', extra=[
    ("require(run['threads_each']==14 and", "require(14<=run['threads_each']<=24 and")])
conv(fz95 / 'run-final.sh', fz179 / 'run-final.sh')
conv(fz95 / 'watch.sh', fz179 / 'watch.sh')
for p in list(o179.glob('*.sh')) + list(fz179.glob('*.sh')) + list(f179.glob('*.sh')):
    p.chmod(0o755)
leftover = subprocess.run(f"grep -l 'ba87b9ce\\|product95\\|plain95\\|cache-certificate95\\|20_275_836' {f179}/*.py {f179}/*.sh {o179}/*.py {o179}/*.sh {o179}/*.rs {fz179}/*.py {fz179}/*.sh", shell=True, capture_output=True, text=True).stdout.split()
# accept.py and audit_tool_diff.py legitimately mention the 95 stream (as the PLAIN67->95 reference binding)
leftover = [x for x in leftover if not x.endswith(('accept.py', 'audit_tool_diff.py'))]
assert not leftover, leftover
record = {'status': 'PHASE_B_GENERATED', 'candidate_stream_sha256': S, 'ops': N, 'archive_sha256': sha(arc), 'archive_files': nfiles,
          'archive_dirs': ndirs, 'frozen_bin_sha256': frozen_bin, 'certificate_sha256': sha(cert / 'CACHE_EQUIVALENCE_CERTIFICATE.json')}
(nd / 'PHASE_B.json').write_text(json.dumps(record, indent=2) + '\n'); print(json.dumps(record, indent=2))
