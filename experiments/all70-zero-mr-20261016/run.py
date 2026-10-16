from pathlib import Path
import hashlib,json,os,subprocess,time
R=Path(__file__).resolve().parent;os.chdir(R)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=json.loads((R/'DECLARATION.json').read_text());B=R.parent
source=B/d['source_path'];assert sha(source)==d['source_sha256']
assert(B/'repair67-persistent-cost-20261016/run.exit').read_text().strip()=='0', 'cost workers must be released first'
sidecar=B/'all70-mask-feasibility-20261016/EXPORT-METADATA-CLARIFICATION.json'
assert sha(sidecar)==d['required_mask_source_sidecar_sha256'];s=json.loads(sidecar.read_text())
assert s['evaluated_source_stream_sha256']==d['source_sha256'] and s['program_sha256']==d['fresh_mask_program_sha256']
assert sha(B/'all70-mask-feasibility-20261016/mr-mask-all70.bin')==d['fresh_mask_program_sha256']
for name,h in d['compiler_source_lineage'].items():assert sha(R/name)==h,name
available=int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))
assert available>=116*1024**2,'16GiB query plus100GiB reserve required'
corpus=B/'prefilter-20261015/evidence/census-coordinates4096.tsv';audit=B/'prefilter-20261015/packets/audit.tsv'
assert sha(audit)=='56bd53b84fa65d28779f7cbb28b1b969453ca1da695e46392a90b00abba23ba3'
library=B/'overnight-20261014/product-b3-baseline'
assert sha(library/'src/sim.rs')=='f0c72f2a280cd68acee1dbf8282098f72d6b3bf4311e0abf96d122fe002256d7'
files=[p for p in(R/'tool').rglob('*')if p.is_file()and'target'not in p.parts]+[R/'run.py',R/'run.sh',R/'DECLARATION.json',source,sidecar,corpus,audit]+[library/p for p in ['src/sim.rs','src/circuit.rs','src/weierstrass_elliptic_curve.rs','Cargo.toml','Cargo.lock']]
before={str(p):sha(p)for p in files};(R/'SOURCE-PINS-BEFORE.json').write_text(json.dumps(before,indent=2)+'\n')
env=os.environ.copy();env.update(CARGO_BUILD_JOBS='1',RAYON_NUM_THREADS='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
with(R/'build.log').open('w')as log:
 subprocess.run(['/home/hclau/.cargo/bin/cargo','build','--manifest-path','tool/Cargo.toml','--release','--locked','--offline','--bins'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
compiler=R/'tool/target/release/product_paired_diagnostic';verifier=R/'tool/target/release/zero_ir_verify'
binpins={str(p):sha(p)for p in [compiler,verifier]};(R/'BINARY-PINS.json').write_text(json.dumps(binpins,indent=2)+'\n')
with(R/'validation.log').open('w')as log:
 subprocess.run([str(compiler),str(source),str(corpus),str(R/'all70.compact16.bin')],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
with(R/'extra-validation.log').open('w')as log:
 subprocess.run([str(verifier),str(source),str(R/'all70.compact16.bin'),str(audit),str(corpus)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
after={str(p):sha(p)for p in files};assert before==after
assert all(sha(Path(p))==h for p,h in binpins.items());(R/'SOURCE-PINS-AFTER.json').write_text(json.dumps(after,indent=2)+'\n')
generic=(R/'validation.log').read_text();extra=(R/'extra-validation.log').read_text()
assert 'SLICE_FIXTURES assignments=512' in generic and 'ZERO_VALUE_VERIFIED shots=512' in generic and 'SLICE_VERIFIED shots=512' in generic
assert 'FRESH_ALL70_ZERO_IR_ALL_CONTROLS_PASS' in extra and extra.count('FRESH_ALL70_ZERO_IR_CONTROL_PASS')==16 and 'FRESH_ALL70_ZERO_IR_NEGATIVES_PASS'in extra
metadata=(R/'all70.compact16.bin.tsv').read_text().splitlines();assert metadata.count('qubits\t1234')==1 and metadata.count('classical_bits\t45701')==1
outputs=[x for x in metadata if x.startswith('output\t')];assert len(outputs)==512
binding={'status':'FRESH_ALL70_FIXED_ZERO_MR_VALUE_IR_PROTECTED_VALIDATED_NO_RUNTIME_AUTHORITY','source_stream_sha256':d['source_sha256'],
 'program_path':str(R/'all70.compact16.bin'),'program_sha256':sha(R/'all70.compact16.bin'),'program_bytes':(R/'all70.compact16.bin').stat().st_size,
 'program_metadata_sha256':sha(R/'all70.compact16.bin.tsv'),'compiler_source_sha256':sha(R/'tool/src/main.rs'),'C_kernel_source_sha256':sha(R/'tool/zero8.c'),
 'canonical_1024_input_ports':True,'scored_output_bits':512,'Q':1234,'B':45701,'source_physical_MR_count':906156,'IR_randomness':'fixed all-zero; phase not queried',
 'required_mask_program_sha256':d['fresh_mask_program_sha256'],'required_mask_source_sidecar_sha256':d['required_mask_source_sidecar_sha256'],
 'source_before_after_equal':True,'generic512_actual_and512_scope_controls':True,'extra_native_states':4,'audit_inputs':32,'partial_cases':11,'negative_kernel_cases':4,
 'old_2a_IR_transferred_or_loaded':False,'runtime_or_search_authority':False,'phase_or_pass_authority':False,'production_changed':False}
(R/'IR-BINDING.json').write_text(json.dumps(binding,indent=2)+'\n');print(json.dumps(binding),flush=True)
