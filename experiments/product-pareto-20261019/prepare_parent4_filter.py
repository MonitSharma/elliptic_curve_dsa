"""Bind the disabled, previously validated filter to the small frozen circuit.
No authoritative rejection, operational search, or submission is enabled.
"""
import hashlib, json, shutil
from pathlib import Path
root = Path(__file__).resolve().parent
ws = root.parent
out = root / 'parent4-filter'
proof = root / 'parent4-transfer-local/PUBLIC-PARENT-TRANSFER.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert json.loads(proof.read_text())['status'] == 'PUBLIC_PARENT_EXTENSION_UNIVERSAL_AUDIT_PASS'
assert (root / 'parent4-transfer-local.exit').read_text().strip() == '0'
assert '2 passed; 0 failed' in (root / 'parent4-transfer-local/tests.log').read_text()
gate = json.loads((root / 'parent4-qualification/RESULT.json').read_text())
assert gate['status'] == 'FAILURE_GATE_PASS' and all(gate['rules'].values())
candidate = root / 'candidate-parent4'
source = json.loads((root / 'parent4-qualification/point-add-source.json').read_text())
assert all(sha(candidate / p) == h for p, h in source.items())
assert sha(candidate / 'ops.bin') == gate['stream_sha256']['candidate']
assert json.loads((root / 'NATIVE-PILOT.json').read_text())['status'] == 'NATIVE_PILOT_BYTE_IDENTITY_PASS'
out.mkdir(exist_ok=False)
old = ws / 'product67-filter-20261016'
tool = out / 'tool'
shutil.copytree(old / 'tool/src', tool / 'src')
for name in ['Cargo.toml', 'Cargo.lock']:
    shutil.copyfile(old / 'tool' / name, tool / name)
p = tool / 'src/packed_body.rs'
text = p.read_text()
for before, after in [
    ('268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d', gate['stream_sha256']['candidate']),
    ('assert_eq!(n,17_891_821)', 'assert_eq!(n,17_889_606)')]:
    assert text.count(before) == 1
    text = text.replace(before, after)
assert 'const PROOF_ACCEPTED:bool=false;' in text
p.write_text(text)
# Retain every original67 proof binding and append the exact extension binding.
p = tool / 'src/transfer.rs'
text = p.read_text()
required = [proof, root / 'parent4-transfer-local/PROOF-SOURCE.json', root / 'parent4-transfer-local/target/release/verify_parent_extension',
    root / 'parent4-native.json', root / 'NATIVE-PILOT.json', root / 'parent-unwrapped.json',
    root / 'parent-unwrapped-retained.json', root / 'unwrap.rs', root / 'scan.rs',
    root / 'target/release/product_pareto_unwrap', root / 'target/release/product_pareto_exact_v3']
binding = ''.join(' sha_check(' + json.dumps(str(p)) + ',' + json.dumps(sha(p)) + ');\n' for p in required)
assert text.count('fn bind_transfer(){') == 1
p.write_text(text.replace('fn bind_transfer(){', 'fn bind_transfer(){\n' + binding))
run = (old / 'run.py').read_text()
run = run.replace("root.parent/'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin'", "root.parent/'candidate-parent4/ops.bin'")
run = run.replace("root.parent/'prefilter-20261015/model-source'", "Path('/home/hclau/ecdsa_research/prefilter-20261015/model-source')")
run = run.replace('268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d', gate['stream_sha256']['candidate'])
run = run.replace('DISABLED_PRODUCT67_PIPELINE_QUALIFICATION_PASS', 'DISABLED_PARENT4_PIPELINE_QUALIFICATION_PASS')
(out / 'validate.py').write_text(run)
manifest = {str(p.relative_to(out)): sha(p) for p in out.rglob('*') if p.is_file()}
(out / 'PREPARATION.json').write_text(json.dumps({'candidate_stream_sha256': gate['stream_sha256']['candidate'],
    'source_files': manifest, 'additional_proof_artifacts': {str(p): sha(p) for p in required},
    'original_filter': str(old), 'authoritative_rejection': False, 'model_attribution': 'GPT-6 Astra'}, indent=2) + '\n')
print('Candidate filter prepared with rejection disabled.', flush=True)
