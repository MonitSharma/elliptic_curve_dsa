from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parent
assert (root/'run.exit').read_text().strip()=='0'
assert (root/'bench.exit').read_text().strip()=='0'
(root/'bin').mkdir(exist_ok=True)
binary=root/'bin/simd_census_v1';shutil.copy2(root/'tool/target/release/product_paired_diagnostic',binary)
files=['main.rs','prepare.py','build.rs','run.sh','bench.sh','tool/src/main.rs','tool/src/prefix.rs','tool/src/fast_sim_wide.rs','tool/src/fast_curve_c.rs','tool/simd8count.c','tool/simd8wide.h','tool/Cargo.toml','tool/Cargo.lock']
hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}
external=['/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so','/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin','/home/hclau/ecdsa_research/product-exact-20261015/candidate-final/ops.bin']
out={'status':'validated_research_census_not_a_scored_evaluator','binary':str(binary),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'arguments':'OPS LABEL FIRST COUNT WORKERS OUT VERIFY_FIRST_BATCHES','files':hashes,'external_files':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in external},'validation':json.loads((root/'validation-summary.json').read_text()),'nonce_screening':False}
(root/'FREEZE.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['binary_sha256'],str(binary))
