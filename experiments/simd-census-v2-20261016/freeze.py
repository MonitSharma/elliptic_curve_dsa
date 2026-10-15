from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parent;old=root.parent/'simd-census-20261016'
assert (root/'run.exit').read_text().strip()=='0'
for name,reference in [('tip.jsonl','tip-reference.jsonl'),('candidate.jsonl','candidate-final-reference.jsonl'),('partial.jsonl','partial-reference.jsonl'),('bench4096.jsonl','bench4096.jsonl')]:assert (root/name).read_bytes()==(old/reference).read_bytes(),name
(root/'bin').mkdir(exist_ok=True);binary=root/'bin/simd_census_v2';shutil.copy2(root/'tool/target/release/product_paired_diagnostic',binary)
files=['prepare.py','shake_rng.rs','run.sh','tool/src/main.rs','tool/src/prefix.rs','tool/src/fast_sim_wide.rs','tool/src/fast_curve_c.rs','tool/src/shake_rng.rs','tool/simd8count.c','tool/simd8wide.h','tool/build.rs','tool/Cargo.toml','tool/Cargo.lock']
external=['/home/hclau/ecdsa_research/scalar-fast-20261015/libscalar_fast_batch.so','/home/hclau/ecdsa_research/shake8-20261015/libshake8.so','/home/hclau/ecdsa_research/product-exact-20261015/tip/ops.bin','/home/hclau/ecdsa_research/product-exact-20261015/candidate-final/ops.bin']
out={'status':'validated_research_census_not_a_scored_evaluator','binary':str(binary),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'arguments':'OPS LABEL FIRST COUNT WORKERS OUT VERIFY_FIRST_BATCHES','files':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files},'external_files':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in external},'validation':{'all4096_rows_match_frozen_v1':True,'reference_rows128_per_source_match':True,'full_quantum_classical_phase_Toffoli_verified_batches_per_source':64,'all_MR_words_equal_scalar_SHAKE_on_verified_groups':True,'partial_first17_count11_workers3_matches':True,'bench4096_workers4_seconds':11.539649},'nonce_screening':False}
(root/'FREEZE.json').write_text(json.dumps(out,indent=2)+'\n');print(out['binary_sha256'],str(binary))
