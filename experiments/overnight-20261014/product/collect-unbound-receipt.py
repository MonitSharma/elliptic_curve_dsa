"""Matched raw consumer evidence with explicit rejection of the invalid cached run."""
from pathlib import Path
import hashlib,json,re,sys,collections
base=Path(sys.argv[1]);out=Path(sys.argv[2]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(status='negative_exact_full_width_repair_diagnostic',qualified_score=None,baseline_revision='c5bb1ec876db859a3f9f8a9052c140a145df834e',
 measurement_domain='product-paired-fixed-measurement-v1 + little-endian batch0',packet=str(base/'product-evidence/structured-detail/structured.tsv'),experiments={})
result['packet_sha256']=sha(Path(result['packet']))
for label,checkout,target in [('unbound-base','product-unbound-base','product-zero-target'),('unbound-full-cross-v2','product-unbound-full-cross','product-unbound-full-cross-v2-target')]:
 e=base/'product-evidence'/label;source=base/checkout
 paths={'generation_log':e/'run.log','native_log':e/'consumer-family.log','raw_stream':e/'raw-ops.bin','native_source':base/'product-consumer-prefix-replay/src/main.rs','native_manifest':base/'product-consumer-prefix-replay/Cargo.toml','native_binary':base/'product-consumer-prefix-v2-target/release/product_consumer_prefix_replay','builder_binary':base/target/'release/build_circuit'}
 evidence={k:dict(path=str(p),sha256=sha(p)) for k,p in paths.items()}
 for relative in ['src/point_add/builder.rs','src/point_add/leapfrog.rs','src/point_add/square.rs','src/bin/eval_circuit.rs','src/sim.rs','src/circuit.rs','src/weierstrass_elliptic_curve.rs','Cargo.toml','Cargo.lock','benchmark.sh']:
  evidence[relative]=dict(path=str(source/relative),sha256=sha(source/relative))
 for record,name in [('consumer-family-native.sha256','native_binary'),('native-builder.sha256','builder_binary')]:
  recorded=(e/record).read_text().split()[0];assert recorded==evidence[name]['sha256'],(label,name,'binary changed after run')
 # Check source and stream against the pre-run diagnostic manifest.
 manifest=(e/'consumer-family-source.sha256').read_text().splitlines()
 for line,key in zip(manifest,['native_source','native_manifest','raw_stream']):assert line.split()[0]==evidence[key]['sha256'],(label,key,'pre-run source mismatch')
 log=paths['native_log'].read_text();rows={};groups=collections.Counter();deltas=collections.Counter();masks={};prefix_phase=collections.Counter()
 f=lambda s:dict(re.findall(r'(\w+)=(\S+)',s))
 for s in log.splitlines():
  if s.startswith('PREFIX_SHOT phase=divide '):d=f(s);rows[int(d['index'])]=d
  if s.startswith('PREFIX_STATE '):d=f(s);masks[d['phase']]=int(d['phase_mask'],16)
 for s in log.splitlines():
  if s.startswith('FINAL_CONSUMER_SHOT '):
   d=f(s);v=rows[int(d['index'])];rep='literal0' if int(v['y'],16)==0 else 'p' if v['family']=='zero_slope' else 'nonzero';key=(d['family'],rep)
   groups[key,'shots']+=1
   for name in ['x_bad','y_bad','dirty','classical_input_changed']:groups[key,name]+=int(d[name]=='true')
   groups[key,'phase_bad']+=int(d['phase_bad'])
  if s.startswith('R0_SHOT '):d=f(s);deltas[d['family'],d['delta'],d['odd'],d['extension_uniform']]+=1
 for phase,mask in masks.items():
  for i,v in rows.items():rep='literal0' if int(v['y'],16)==0 else 'p' if v['family']=='zero_slope' else 'nonzero';prefix_phase[phase,v['family'],rep]+=(mask>>i)&1
 marker=f'path=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/{label}/raw-ops.bin'
 assert marker in paths['generation_log'].read_text(),(label,'runtime path mismatch')
 result['experiments'][label]=dict(evidence=evidence,generation_exit=int((e/'run.exit').read_text()),native_exit=int((e/'consumer-family.exit').read_text()),flags=dict(y42_unbound=True,y42_alloc=False,sq_asm_tail=18,full_cross=label.endswith('v2')),runtime_path_verified=True,family_counts={str(k):v for k,v in groups.items()},r0_delta_counts={str(k):v for k,v in deltas.items()},phase_at_prefix={str(k):v for k,v in prefix_phase.items()},qualified_score=None)
result['same_native_helper_binary']=len({x['evidence']['native_binary']['sha256'] for x in result['experiments'].values()})==1
result['distinct_builder_binaries']=len({x['evidence']['builder_binary']['sha256'] for x in result['experiments'].values()})==2
assert result['same_native_helper_binary'] and result['distinct_builder_binaries']
bad=base/'product-evidence/unbound-full-cross'
result['excluded_cached_run']=dict(status='invalid_cached_binary',generation_exit=int((bad/'run.exit').read_text()),native_exit=int((bad/'consumer-family.exit').read_text()),source_receipt_sha256=sha(bad/'receipt/receipt.json'),log_sha256=sha(bad/'run.log'),native_log_sha256=sha(bad/'consumer-family.log'),reason='Identical prior baseline binary and runtime raw snapshot path; no variant stream or simulation.',arithmetic_evidence_accepted=False)
result['limitations']='One64shot coupled raw packet; no independent repair follow-up because repair failed. Shared measurement domain but different MR locations. Later bound pipeline failed101; no final pipeline or qualified score.'
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','same_native_helper_binary','distinct_builder_binaries','qualified_score']}))
