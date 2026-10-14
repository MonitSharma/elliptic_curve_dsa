from pathlib import Path
import hashlib,json,re,sys,collections
base=Path(sys.argv[1]);out=Path(sys.argv[2]);e=base/'product-evidence/producer-observation';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths={'raw_stream':e/'raw-ops.bin','generation_log':e/'run.log','native_log':e/'replay.log','metadata':e/'metadata.tsv','native_source':base/'product-producer-replay/src/main.rs','native_manifest':base/'product-producer-replay/Cargo.toml','native_binary':base/'product-producer-replay-target/release/product_producer_replay','builder_binary':base/'product-producer-observation-target/release/build_circuit','packet':base/'product-evidence/structured-detail/structured.tsv'}
evidence={k:dict(path=str(p),sha256=sha(p)) for k,p in paths.items()}
assert evidence['raw_stream']['sha256']=='c2c6987b7b97b3175cbd7947699c651c7b324f4c9412d439e7a9b4658a4ac272'
for record,key in [('native-builder.sha256','builder_binary'),('replay-native.sha256','native_binary')]:assert (e/record).read_text().split()[0]==evidence[key]['sha256']
for line,key in zip((e/'replay-source.sha256').read_text().splitlines(),['native_source','native_manifest','raw_stream','metadata']):assert line.split()[0]==evidence[key]['sha256']
assert 'path=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/producer-observation/raw-ops.bin' in paths['generation_log'].read_text()
source=base/'product-producer-observation'
for relative in ['src/point_add/square.rs','src/point_add/builder.rs','src/point_add/leapfrog.rs','src/bin/eval_circuit.rs','src/sim.rs','src/circuit.rs','src/weierstrass_elliptic_curve.rs','Cargo.toml','Cargo.lock','benchmark.sh']:
 evidence[relative]=dict(path=str(source/relative),sha256=sha(source/relative))
f=lambda s:dict(re.findall(r'(\w+)=(\S+)',s));rows={};groups=collections.Counter();zero_words={};examples=[]
log=paths['native_log'].read_text().splitlines()
for s in log:
 if s.startswith('PREFIX_SHOT phase=divide '):d=f(s);rows[int(d['index'])]=d
for s in log:
 if not s.startswith('PRODUCER_SHOT '):continue
 d=f(s);b=rows[int(d['index'])];rep='literal0' if int(b['y'],16)==0 else 'p' if b['family']=='zero_slope' else 'nonzero';key=(d['label'],d['family'],rep)
 groups[key,'shots']+=1;groups[key,'product_bad']+=int(d['product_correct']=='false');groups[key,'phase_changed']+=int(d['phase_delta']);groups[key,'input_changed']+=int(d['input_restored']=='false')
 if rep=='literal0' and d['label'].endswith('.producer'):
  prior=zero_words.setdefault(d['label'],dict(product=d['product'],expected=d['expected'],delta=d['delta'],shots=0));assert prior['product']==d['product'];prior['shots']+=1
  if int(d['index'])==1:examples.append(d)
observed=int(zero_words['SQ_C_POLICY.producer']['product'],16);model=int('30000000200000000fffffffd000000000000000300000003fffffffe',16)
assert model-observed==1<<118
j=dict(status='completed_production_producer_identity_diagnostic',baseline_revision='c5bb1ec876db859a3f9f8a9052c140a145df834e',qualified_score=None,evidence=evidence,
 generation_exit=int((e/'run.exit').read_text()),native_exit=int((e/'replay.exit').read_text()),runtime_path_verified=True,raw_byte_identical_to_full_width_v2=True,flags=dict(y42_unbound=True,y42_alloc=False,sq_asm_tail=18,full_cross=True),
 groups={str(k):v for k,v in groups.items()},literal_zero_producer_words=zero_words,examples=examples,c_word_unsigned_model_minus_observed_hex=hex(1<<118),weighted_residual_hex=hex(1<<246),
 limitations='One64shot structured packet; intermediate input mutation and C forward phase are expected. Phase defects assessed only after the actual folds and inverse. No repair or full benchmark qualification.')
out.write_text(json.dumps(j,indent=2)+'\n');print(json.dumps({k:j[k] for k in ['status','generation_exit','native_exit','raw_byte_identical_to_full_width_v2','qualified_score']}))
