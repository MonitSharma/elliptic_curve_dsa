"""Freeze a candidate-bound copy of the qualified filter; rejection stays off."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;parent=ws/'product-pareto-20261019'
out=r/'parent4-filter';proof=r/'PUBLIC-PARENT-TRANSFER.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert (r/'extension.exit').read_text().strip()=='0'
assert json.loads(proof.read_text())['status']=='PUBLIC_PARENT_EXTENSION_UNIVERSAL_AUDIT_PASS'
assert json.loads((r/'VERIFIED-EXTENSION-PROOFS.json').read_text())['status']=='SOURCE_BOUND_EXTENSION_PROOFS_VERIFIED'
gate=json.loads((parent/'parent4-qualification/RESULT.json').read_text())
assert gate['status']=='FAILURE_GATE_PASS' and all(gate['rules'].values())
candidate=parent/'candidate-parent4'
source=json.loads((parent/'parent4-qualification/point-add-source.json').read_text())
protected=json.loads((parent/'parent4-qualification/protected-files.json').read_text())
assert all(sha(candidate/p)==h for p,h in source.items())
assert all(sha(candidate/p)==h for p,h in protected.items())
assert sha(candidate/'ops.bin')==gate['stream_sha256']['candidate']=='9f50f06098026882a57f5f6c436abaaf68be79be2fc7c6e33b8e884065195a3a'
assert sha(parent/'parent/ops.bin')=='99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683'
assert json.loads((parent/'NATIVE-PILOT.json').read_text())['status']=='NATIVE_PILOT_BYTE_IDENTITY_PASS'
old=ws/'product67-filter-20261016'
assert json.loads((old/'RESULT.json').read_text())['status']=='DISABLED_PRODUCT67_PIPELINE_QUALIFICATION_PASS'
out.mkdir(exist_ok=False);tool=out/'tool';shutil.copytree(old/'tool/src',tool/'src')
for name in ('Cargo.toml','Cargo.lock'):shutil.copyfile(old/'tool'/name,tool/name)
p=tool/'src/packed_body.rs';text=p.read_text()
for before,after in [('268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d',gate['stream_sha256']['candidate']),('assert_eq!(n,17_891_821)','assert_eq!(n,17_889_606)')]:
    assert text.count(before)==1;text=text.replace(before,after)
assert 'const PROOF_ACCEPTED:bool=false;' in text;p.write_text(text)
required=[proof,r/'VERIFIED-EXTENSION-PROOFS.json',r/'verify_extension.rs',r/'target/release/verify_extension',r/'export.rs',r/'prove.py',r/'prove_wide.py',r/'prove_zero.py',r/'replay_one.py',
          r/'validate_zero.py',r/'ZERO-MUTATION-CONTROLS.json',r/'zero-8192-result.json',r/'zero-8192-replay.json',
          parent/'parent4-native.json',parent/'NATIVE-PILOT.json',parent/'parent-unwrapped.json',parent/'parent-unwrapped-retained.json',
          parent/'unwrap.rs',parent/'scan.rs',parent/'target/release/product_pareto_unwrap',parent/'target/release/product_pareto_exact_v3',
          parent/'parent4-qualification/RESULT.json',parent/'parent4-qualification/point-add-source.json',parent/'parent4-qualification/protected-files.json']
for j in range(1,28):required.extend([r/f'boundary-{j:02}.json',r/('wide-02-1024-result.json' if j==2 else f'seeded-lease-{j:02}-result.json')])
p=tool/'src/transfer.rs';text=p.read_text();needle='fn bind_transfer(){';assert text.count(needle)==1
binding=''.join(' sha_check('+json.dumps(str(p))+','+json.dumps(sha(p))+');\n' for p in required)
p.write_text(text.replace(needle,needle+'\n'+binding))
run=(old/'run.py').read_text()
before="root.parent/'product-exact-20261015/product-to67-rank-20261016/product-67-retained-1024-proxy.bin'"
assert run.count(before)==1;run=run.replace(before,'Path('+repr(str(candidate/'ops.bin'))+')')
run=run.replace("root.parent/'prefilter-20261015/model-source'","Path('/home/hclau/ecdsa_research/prefilter-20261015/model-source')")
run=run.replace('268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d',gate['stream_sha256']['candidate'])
run=run.replace('DISABLED_PRODUCT67_PIPELINE_QUALIFICATION_PASS','DISABLED_PARENT4_PIPELINE_QUALIFICATION_PASS')
(out/'validate.py').write_text(run)
(out/'PREPARATION.json').write_text(json.dumps({'candidate_stream_sha256':gate['stream_sha256']['candidate'],'source_files':{str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()},
    'additional_proof_artifacts':{str(p):sha(p) for p in required},'original_filter':str(old),'authoritative_rejection':False,
    'circuit_changed':False,'gate_rerun':False,'model_attribution':'GPT-6 Astra'},indent=2)+'\n')
print('Frozen candidate-bound filter prepared with rejection disabled',flush=True)
