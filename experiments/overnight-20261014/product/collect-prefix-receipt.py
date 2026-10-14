"""Freeze observational native-prefix provenance; never emit a qualified score."""
from pathlib import Path
import hashlib,json,re,sys,collections
base=Path(sys.argv[1]);out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths={
 'baseline_final':base/'product-evidence/raw-handoff/ops.bin',
 'baseline_raw':base/'product-evidence/raw-handoff/raw-ops.bin',
 'raw_generation_log':base/'product-evidence/raw-handoff/run.log',
 'raw_replay_log':base/'product-evidence/raw-handoff/prefix.log',
 'final_prefix40_log':base/'product-evidence/phase-anchors/prefix40.log',
 'anchor_certificate':base/'product-evidence/phase-anchors/anchors40.json',
 'raw_native_source':base/'product-raw-prefix-replay/src/main.rs',
 'raw_native_manifest':base/'product-raw-prefix-replay/Cargo.toml',
 'raw_native_binary':base/'product-anf-analysis/target/release/product_raw_prefix_replay',
 'final_native_source':base/'product-prefix-replay/src/main.rs',
 'final_native_manifest':base/'product-prefix-replay/Cargo.toml',
 'final_native_binary':base/'product-anf-analysis/target/release/product_prefix_replay',
 'structured_packet':base/'product-evidence/structured-detail/structured.tsv',
 'protected_eval':base/'product/src/bin/eval_circuit.rs',
 'protected_sim':base/'product/src/sim.rs',
 'protected_circuit':base/'product/src/circuit.rs',
 'protected_curve':base/'product/src/weierstrass_elliptic_curve.rs',
}
rows={};groups=collections.Counter();deltas=collections.Counter();counterexamples=[]
log=paths['raw_replay_log'].read_text()
for line in log.splitlines():
 if line.startswith('PREFIX_SHOT phase=divide '):
  d=dict(re.findall(r'(\w+)=(\S+)',line));rows[int(d['index'])]=d
for line in log.splitlines():
 if not line.startswith('R0_SHOT '):continue
 d=dict(re.findall(r'(\w+)=(\S+)',line));b=rows[int(d['index'])]
 rep='literal0' if int(b['y'],16)==0 else 'p' if b['family']=='zero_slope' else 'nonzero'
 groups[str((d['family'],rep,d['residue_correct'],d['odd'],d['extension_uniform']))]+=1
 deltas[d['delta']]+=1
 if len(counterexamples)<6 and d['residue_correct']=='false':counterexamples.append(dict(divide=b,square_r0=d))
j=dict(status='completed_research_diagnostic',qualified_score=None,baseline_revision='c5bb1ec876db859a3f9f8a9052c140a145df834e',
 evidence={k:dict(path=str(p),sha256=sha(p)) for k,p in paths.items()},
 exit_statuses={x:int((base/x).read_text()) for x in ['product-evidence/raw-handoff/run.exit','product-evidence/raw-handoff/prefix.exit','product-evidence/phase-anchors/prefix40.exit']},
 final_stream_byte_identical=sha(paths['baseline_final'])=='49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4',
 raw_square_boundary=5986173,final_multiply_boundary=11452887,actual_settings=dict(native_sfuse_b=1,t6_seedfuse=True,seam_fs=53,erase_compare=20),
 signed_r0_wires=list(range(256))+[857,861,860,859],
 r0_groups=dict(groups),r0_expected_minus_actual_delta_counts=dict(deltas),counterexamples=counterexamples,
 limitations='One native 64-shot structured packet. Raw and final streams use distinct MR positions; each complete consumer was replayed. No full benchmark qualification or universal repair proof.')
out.write_text(json.dumps(j,indent=2)+'\n')
print(json.dumps({k:j[k] for k in ['status','qualified_score','final_stream_byte_identical','r0_groups']}))
