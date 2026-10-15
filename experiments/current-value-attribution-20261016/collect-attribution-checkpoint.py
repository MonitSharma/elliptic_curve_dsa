from pathlib import Path
import json,hashlib,tarfile,shutil,datetime,subprocess,re,ast,collections
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');v='attribution-checkpoint-v1';stage=r/v;assert not stage.exists();stage.mkdir()
for name in ['actual-replay','add-replay','dirty-add-replay','source-markers','add-markers','loan-markers','dirty-low-protected']:
 assert(r/(name+'.exit')).read_text().strip()=='0',name
actual=r.parent/'product-exact-20261015/tip/ops.bin';raw=r/'raw-builder.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(actual)=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e';assert sha(raw)=='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69'
a=json.loads((r/'attribution.json').read_text());assert a['target_witnesses']==431 and a['full_original_batches_replayed']==413
events=[s for s in(r/'add-replay.log').read_text().splitlines()if s.startswith('ADD_EVENT ')];assert len(events)==14 and all('tick=131 rev=false at=4055807 id=780 width=256 'in s for s in events)
entries={int(m[1]):set(ast.literal_eval(m[2]))for m in re.finditer(r'ADD_ENTRY shot=(\d+) .*?nonzero=(\[[^\n]*\])',(r/'dirty-add-replay.log').read_text())};assert len(entries)==14
f=json.loads((r/'n2-loan-family.json').read_text());divide=f['families'][0];rails=divide['source_rails_bit1through5'];cases=[]
def parse(line):return dict(re.findall(r'(\w+)=([^ ]+)',line))
for line in events:
 e=parse(line);shot=int(e['shot']);bits=entries[shot];values=[]
 for rail in rails:
  sg=int(rail[4]in bits);d=sum(int(q in bits)<<(i+1)for i,q in enumerate(rail[:4]));values.append((1-2*sg)*(1+d))
 dirt=[q for q in [553,554,555,556]if q in bits];assert len(dirt)==1 and dirt[0]in[555,556]
 carry_bit={555:2,556:3}[dirt[0]];x,y=int(e['a'],16),int(e['b'],16);carry=((x%(1<<carry_bit))+(y%(1<<carry_bit)))>>carry_bit;delta=(1-2*carry)*(1<<carry_bit)
 assert int(e['delta'],16)==delta%(1<<256)
 cases.append(dict(shot=shot,batch=shot//64,lane=shot%64,parked_signed6bit_rails=values,dirty_q=dirt[0],injected_carry_bit=carry_bit,exact_sum_error=delta))
counts=collections.Counter(z['injected_carry_bit']for z in cases);assert counts=={2:8,3:6}
diag=dict(status='TERMINAL ACTUAL FINAL SOURCE DIAGNOSIS; NO CANDIDATE /REPAIR',target_current_value_witnesses=431,original_batch_contexts=413,original_context_shots=26432,original_source_sha256=sha(actual),
 source_raw_component_sha256=sha(raw),raw_observer_provenance='rawff5163 source dump supplies marker IDs only; every attributed state is replayed through ACTUAL final2a gates, with actual original per-batch MR stream and unchanged protected differential. Raw ff5163 states are NOT final2a states.',
 advisory_unexplained_original_category=dict(witnesses=55,batches=54,lambda_per9024_on_fixed4096_cohort=54/4096*141,universal_floor=False,historical_unsmoothed_B3_roughly1_1_not_current_source=True),
 exact_fold_boundary_losses=dict(total=26,forward_negative_carry=13,reverse_positive_carry=13),exact_square_window_losses=3,
 fixed14_first_failure='first low_keep_add at actual[4052107,4055807), before fold[4064306,4075337); source unchanged, high carry correct, low sum error±4/±8',
 source_cause='n2_loan_out assumes each parked odd signed6bit rail is±1; clears bits1..4 against bit5/sign then release_clean. All14 have rail1±3/±5; one dirty bit enters the first add.',
 all_source_adds=dict(calls=786,markers=1572,all_literal_unique_bindings=True,all_other_calls_on_fixed14_pass=True),all_N2_sites=f,
 exact_carry_contract='dirty[i] XOR MAJ(a[i],b[i],carry[i]) injects carry. Internal scratch is measured/reset, and phase retains Σ HMR_i*dirty_i. Unconditional reset/discard is not justified.',
 protected_primitive=json.loads((r/'dirty-low-protected.json').read_text()),cases=cases,
 limits=['First-add/N2 diagnosis is exact for preserved14 cases; no universal point-add correctness or repair claimed.','Six centered fold markers remain UNKNOWN (three paired regions), preserved in attribution.json.','The original approximate endpoint, finite-fold and table contracts remain unchanged.','A protected-harness classical-slot reuse mistake and PATH setup failure are preserved separately; terminal corrected proof passes.','Source-defined donor feasibility is a separate checkpoint; Square4 census remains frozen outside this archive.'])
(r/'N2-DIAGNOSIS.json').write_text(json.dumps(diag,indent=2)+'\n')
report='''# Actual current-source value attribution checkpoint

Status: terminal diagnostic evidence, no candidate change or demonstrated repair.

The actual final public4b stream is SHA256 `2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e`. All431 value-failure witnesses from the preserved4096-batch census were replayed in their413 original64-lane contexts (26432shots). Exact input keys, original MR continuation, every final quantum/classical bit, phase, executed Toffolis, and original failure masks match the unchanged protected simulator. This is existing-input attribution, not a new failure census.

The source metadata dump is raw builder `ff516396...`, before inherited tables. Its states are not final-circuit authority. Unique literal source neighborhoods bind observation positions into the actual final2a stream; all observed states in the terminal replay come from that actual final stream. Three paired internal fold boundaries remain UNKNOWN and are retained explicitly.

The advisory classifier misses55 witnesses in54 batches: lambda1.85888671875 on this fixed4096 cohort. This category is not a universal rate floor. The older roughly1.1 estimate belongs to the unsmoothedB3 source. Among these55,26 have exact fold boundary loss (13 forward negative carries,13 reverse positive carries),3 have exact C130 square-window loss, and14 share the now localized N2 clean-loan failure. Twelve still need further causal attribution.

All14 N2 cases first violate the first256-bit low_keep_add, before the fold. The source and outgoing high carry stay correct; the sum error is exactly plus/minus4 or8. The parked second rail is plus/minus5 on8 cases or plus/minus3 on6. n2_loan_out clears bits1..4 against the sign and releases them as clean; this is valid exactly when the signed odd6bit rail is plus/minus1. The differing rail bit enters the first add as a dirty carry. Exact ANF and1048576 protected cases prove the arbitrary-dirty low-chunk value and phase contract. The residual phase is the XOR of each internal dirty bit times its HMR word; simply resetting the borrowed bits is not an exact repair.

All2 source n2_loan_out calls (4 rail loans,16 release_clean calls) and their return boundaries are bound to actual final Ops. Loaned wires are reused thousands of times and measured/reset hundreds of times, so repairing only the first carry does not preserve their original data. No low-cost reversible repair is admitted here. Donor feasibility is separately recorded; the frozen Square4 candidate/census is outside this checkpoint.

The archive includes complete source-observer point_add code, the two supplemental gate-inert metadata overlays, tool code, exact input/context packets, protected reference code and hashes, logs, source manifests, and all terminal reports. Large frozen streams are explicitly server-only external entries in MANIFEST.json, not falsely listed as archived members.
'''
(r/'ATTRIBUTION-CHECKPOINT.md').write_text(report)
# Preserve terminal root files, excluding the independent donor experiment.
for p in r.iterdir():
 if p.is_file()and p.suffix in['.py','.sh','.json','.jsonl','.rs','.log','.exit','.pid','.sha256','.patch','.md']and not p.name.startswith(('affine-','prepare-affine','run-affine','donor-')):
  shutil.copy2(p,stage/p.name)
shutil.copytree(r/'packets',stage/'packets')
shutil.copytree(r/'source-observer/src/point_add',stage/'source-observer/src/point_add')
for name,files in [('source-add-observer',['payload_trace.rs','y15_onefold.rs']),('source-loan-observer',['payload_trace.rs','leapfrog.rs'])]:
 for file in files:
  out=stage/name/'src/point_add'/file;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/name/'src/point_add'/file,out)
for name in ['Cargo.toml','Cargo.lock']:shutil.copy2(r/'tool'/name,stage/('tool-'+name))
for name in ['payload_runtime.rs','add_runtime.rs','dirty_add_runtime.rs','observed_sim.rs']:
 p=stage/'tool/src'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/'tool/src'/name,p)
for name in ['current_payload.rs','current_adds.rs','current_dirty_add.rs','protected_dirty_low.rs']:
 p=stage/'tool/src/bin'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/'tool/src/bin'/name,p)
ref=r.parent/'overnight-20261014/product-b3-baseline';protected=[]
for p in(ref/'src').rglob('*'):
 if p.is_file()and'point_add'not in p.relative_to(ref).parts:
  out=stage/'protected-reference'/p.relative_to(ref);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);protected.append(str(p.relative_to(ref)))
for name in ['Cargo.toml','Cargo.lock','rust-toolchain.toml']:
 if(ref/name).is_file():shutil.copy2(ref/name,stage/'protected-reference'/name)
assert sha(ref/'src/sim.rs')==sha(r/'source-observer/src/sim.rs')
pins=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),protected_reference_path=str(ref),protected_git_head=subprocess.check_output(['git','-C',str(ref),'rev-parse','HEAD'],text=True).strip(),protected_sim_matches_frozen4b_source=True,source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',source_snapshot_full_point_add=True,supplemental_snapshots='only two modified files each; every other point_add file must match archived base observer per supplied complete hash manifest')
(stage/'SOURCE-PROVENANCE.json').write_text(json.dumps(pins,indent=2)+'\n')
files={str(p.relative_to(stage)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in stage.rglob('*')if p.is_file()}
external={str(p):dict(bytes=p.stat().st_size,sha256=sha(p),preserved_server_only=True,not_an_archive_member=True)for p in[actual,raw,r/'raw-add-builder.bin',r/'raw-loan-builder.bin']}
(stage/'MANIFEST.json').write_text(json.dumps(dict(status='TERMINAL ATTRIBUTION CHECKPOINT',files=files,external=external,active_work_excluded=['frozen Square4 candidate/census','separate affine donor feasibility']),indent=2)+'\n')
archive=r/(v+'.tar.gz')
with tarfile.open(archive,'w:gz',compresslevel=5)as tf:tf.add(stage,arcname=v)
with tarfile.open(archive)as tf:
 for name,info in files.items():assert hashlib.sha256(tf.extractfile(v+'/'+name).read()).hexdigest()==info['sha256'],name
receipt=dict(status='PASS',archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),verified_archive_members=len(files),external_server_only_streams=len(external),manifest_all_files_present=True)
(r/(v+'-receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
