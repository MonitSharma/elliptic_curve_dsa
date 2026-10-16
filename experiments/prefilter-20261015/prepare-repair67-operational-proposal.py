"""Write an isolated, hard-disabled proposal. Does not prepare/build/run a tool."""
from pathlib import Path
import json,hashlib,difflib,math
r=Path(__file__).resolve().parent.parent
out=r/'repair67-operational-20261016'
assert not out.exists()
out.mkdir()
old=r/'product25-operational-20261016'
review=r/'prefilter-20261015/repair67-composite-review-v1'
def write(n,s): (out/n).write_bytes(s.encode())
def js(n,x):write(n,json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
candidate='0beec42b117e5f623736c4171e156d8ffdfaeeb585285636f91bab2838e7c10b'
theorem='b351ae4cbf4fab52a8248a83d517502c331a0a4291f73f0123370cad645a2c03'
guard='355f9951eda21a7204a96fd391b3208e8d6e000dce6a14feb40d8f19b637f2b3'
mask='560c12d5044dd895a4ef32adc905cdde48a780a196b3b28a75951c7f27b4fe9d'
declaration={
 'status':'SOURCE_PROPOSAL_ONLY_BUILD_LAUNCH_SEARCH_AND_AUTHORITY_DISABLED',
 'candidate_stream_sha256':candidate,'original_stream_sha256':'2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',
 'A29_stream_sha256':'1cd3457b44bd21d65921ce0d5b8352573a9c6f2bb2706430d367f68e5a7e5522',
 'conditional_theorem_sha256':theorem,'guard_sha256':guard,'mask_sha256':mask,
 'original_zeroMR_IR_sha256':'812f706d2edd7e821ff6c5f72db5e7e65b3f9756f562d99c1d0e1fceb007daf0',
 'A29_relative_cache67_certificate_sha256':'3cb037399462d45683c9790793ed1bfbff2df2934898f38f9ffe2cd857ff4d39',
 'dependency':'old_dependency OR G','guard_order':'Only after old known-wrong certificate; G=0 retains it, G=1 falls through to further witnesses/exact candidate fallback.',
 'workers':4,'threads_each':2,'total_screening_threads_max':8,'GiB_per_worker_max':6,'aggregate_worker_GiB_max':24,
 'first_nonce':1,'lookahead':4096,'count_cap_each':134217728,'wall_cap_hours':24,
 'selection':'Lowest full-protected passing nonce after complete lower-prefix JSONL audit; no Toffoli-based selection.',
 'submission_mode':'queue','active25_changes':False,'prepared_tool_created':False,
 'source_proposal_gate':False,'coordinator_proposal_disabled':True,
 'explicit_next_permissions':'Root independent fullsource/proof review, terminal disabled qualification, full8thread resource/cost gate and explicit launch decision are required. This declaration grants none.'}
js('DECLARATION.json',declaration)

# Preserve the exact active25 scheduling semantics, substituting only source and
# stronger acceptance bindings. Tool preparation remains a future action.
source=(old/'prepare.py').read_text()
source=source.replace("old=root.parent/'product-early-filter-20261016'","old=root.parent/'repair67-conditional-filter-20261016'")
source=source.replace("shutil.copytree(old/'tool/src',tool/'src',dirs_exist_ok=True)","assert not tool.exists(),'never overwrite a proposal/qualification tree'\nshutil.copytree(old/'tool/src',tool/'src')")
source=source.replace("source=source.replace('const PROOF_ACCEPTED:bool=false;','const PROOF_ACCEPTED:bool=true;')","assert 'const PROOF_ACCEPTED:bool=false;' in source # Deliberately disabled; root review must create a new source revision to enable.")
source=source.replace("'assert!(PROOF_ACCEPTED);bind_operational();'","'assert!(PROOF_ACCEPTED,\"isolated proposal is disabled; separate reviewed source revision required\");bind_operational();'")
source=source.replace(".replace('threads<=32','threads<=14')",".replace('threads<=32','threads<=2')")
source=source.replace("'PROOF_ACCEPTED=true NONCE_POLICY=ASCENDING_LOWEST_PASS screened={screened}'","'PROOF_ACCEPTED={PROOF_ACCEPTED} NONCE_POLICY=ASCENDING_LOWEST_PASS screened={screened}'")
source=source.replace("// Frozen original-source per-input masks plus complete universal candidate transfer accepted separately.","// Proposed original-mask OR discrepancy-guard transfer, hard-disabled pending separate acceptance.")
source=source.replace("// Full protected confirmation required for every possible pass; coordinator proves lower-prefix completeness.","// Candidate-own Fiat/full protected confirmation and complete lower-prefix audit required.")
# Do not label a hard-disabled mask component authoritative.
source=source.replace("mask=(tool/'src/masks.rs').read_text().replace('authoritative_gate=false','authoritative_gate=true');(tool/'src/masks.rs').write_text(mask)","assert 'authoritative_gate=false' in (tool/'src/masks.rs').read_text()")
# Bind the exact reviewed disabled precursor files before copying/transforming.
pins=json.loads((review/'PREPARED_SOURCE.json').read_text())
needle="shutil.copytree(old/'tool/src',tool/'src')"
source=source.replace(needle,"import hashlib,json\nexpected=json.loads((root/'PRECURSOR_SOURCE_PINS.json').read_text())\nfor name,digest in expected.items():\n    assert hashlib.sha256((old/name).read_bytes()).hexdigest()==digest,name\n"+needle)
source += "\nassert 'const PROOF_ACCEPTED:bool=false;' in (tool/'src/packed_body.rs').read_text()\nassert 'guard_safe(&proposed)' in (tool/'src/packed_body.rs').read_text()\nassert 'Some(original.as_ref().unwrap().as_slice())' in (tool/'src/packed_body.rs').read_text()\n(root/'PREPARED_SOURCE.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in tool.rglob('*') if p.is_file()},indent=2)+'\\n')\n"
write('prepare.py',source)
js('PRECURSOR_SOURCE_PINS.json',pins)

search=(old/'search.rs').read_text()
search=search.replace('180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64',candidate)
start=search.index('fn bind_operational(){');end=search.index('\n#[cfg(test)]',start)
search=search[:start]+'''fn bind_operational(){
 let path=std::env::var("ACCEPTANCE_PATH").unwrap();let expected=std::env::var("ACCEPTANCE_SHA256").unwrap();sha_check(&path,&expected);
 let row:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
 assert_eq!(row["status"],"REPAIRED67_CONDITIONAL_FULL_SOURCE_PROOF_RUNTIME_COST_ACCEPTED_FOR_ASCENDING_SEARCH");
 assert_eq!(row["candidate_stream_sha256"],"'''+candidate+'''");
 assert_eq!(row["mask_sha256"],"'''+mask+'''");
 assert_eq!(row["guard_sha256"],"'''+guard+'''");
 assert_eq!(row["conditional_theorem_sha256"],"'''+theorem+'''");
 assert_eq!(row["lowest_pass_from"],1);assert_eq!(row["submission_mode"],"queue");
 assert_eq!(row["workers"],4);assert_eq!(row["threads_each"],2);assert_eq!(row["aggregate_threads_max"],8);
 assert_eq!(row["aggregate_memory_GiB_max"],24);assert_eq!(row["wall_cap_hours"],24);
 for key in["cost_gate_pass","failure_gate_pass","disabled_qualification_pass","independent_operational_review_pass","fresh_public_record_comparison_pass"]{assert_eq!(row[key],true);}
 assert!(row["measured_expected_hours_8threads"].as_f64().unwrap()<=24.0);
 let exe=std::env::current_exe().unwrap();sha_check(exe.to_str().unwrap(),row["operational_executable_sha256"].as_str().unwrap());
 for item in row["runtime_artifacts"].as_array().unwrap(){sha_check(item["path"].as_str().unwrap(),item["sha256"].as_str().unwrap());}
 search_lane();
}'''+search[end:]
write('search.rs',search)

coord=(old/'coordinator.py').read_text()
coord=coord.replace("root=Path(__file__).resolve().parent;workers=4", "PROPOSAL_DISABLED=True\nassert not PROPOSAL_DISABLED,'source proposal only: no launch authority; separate reviewed revision required'\nroot=Path(__file__).resolve().parent;workers=4")
coord=coord.replace('SOURCE_BOUND_MASK_TRANSFER_AND_RUNTIME_ACCEPTED_FOR_ASCENDING_SEARCH','REPAIRED67_CONDITIONAL_FULL_SOURCE_PROOF_RUNTIME_COST_ACCEPTED_FOR_ASCENDING_SEARCH')
coord=coord.replace("threads=int(os.environ.get('SEARCH_THREADS_EACH','12'));assert 1<=threads<=14","threads=int(os.environ.get('SEARCH_THREADS_EACH','2'));assert threads==2 and workers*threads<=8")
coord=coord.replace("product-exact-20261015/candidate-product-final25/ops.bin","product-exact-20261015/repair-to67-rank-20261016/repair-67-retained-1024-proxy.bin")
coord=coord.replace("'preliminary_distinct_timing_nonces':262144","'preliminary_distinct_timing_nonces':receipt['preliminary_distinct_timing_nonces']")
coord=coord.replace("assert (root/'build.exit').read_text().strip()=='0'", "assert (root/'build.exit').read_text().strip()=='0'\nassert receipt['disabled_qualification_pass'] and receipt['independent_operational_review_pass']\nassert receipt['fresh_public_record_comparison_pass'] and receipt['measured_expected_hours_8threads']<=24\nassert receipt['workers']==4 and receipt['threads_each']==2 and receipt['aggregate_threads_max']==8\nassert receipt['aggregate_memory_GiB_max']==24 and receipt['wall_cap_hours']==24")
coord=coord.replace("assert hashlib.sha256(ops.read_bytes()).hexdigest()==receipt['candidate_stream_sha256']", "assert hashlib.sha256(ops.read_bytes()).hexdigest()==receipt['candidate_stream_sha256']\nassert hashlib.sha256(binary.read_bytes()).hexdigest()==receipt['operational_executable_sha256']\nfor item in receipt['runtime_artifacts']:\n assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']")
# Limit each child before exec, rather than relying on a coordinator-only limit.
coord=coord.replace("jobs=[];started=time.monotonic()", "import resource\ndef worker_limits():resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))\njobs=[];started=time.monotonic()")
coord=coord.replace("env=env,stdout=out,stderr=err)","env=env,stdout=out,stderr=err,preexec_fn=worker_limits)")
write('coordinator.py',coord)
write('run-search.sh', '''#!/bin/bash
set -euo pipefail
echo "DISABLED SOURCE PROPOSAL: no launch/build/search authority" >&2
exit 2
# After separate source review and acceptance, root must create a NEW reviewed
# revision that deliberately removes both this gate and coordinator's gate.
# Do not change or interrupt the existing product25 search.
''')
write('build.sh', '''#!/bin/bash
set -euo pipefail
echo "DISABLED SOURCE PROPOSAL: build requires separate root authorization" >&2
exit 2
''')

# Keep the existing complete-log audit implementation as a proposal, with
# explicit future acceptance/executable pins rather than old active25 hashes.
audit=(old/'audit-terminal.py').read_text()
audit=audit.replace("ACCEPTANCE='2c33d3e2b19cd77b8069e4c134f162e2ee0c9d8d7b97aa57ce4f56d388693682'","ACCEPTANCE='UNSET_REQUIRES_INDEPENDENT_FINAL_REVIEW'")
audit=audit.replace("BINARY='8333ec419e6ff3915021db1175e2e282989b67313a48fea6b751d3b36849b131'","BINARY='UNSET_REQUIRES_INDEPENDENT_FINAL_REVIEW'")
audit=audit.replace("run['threads_each']==12","run['threads_each']==2")
audit=audit.replace("artifacts={path:hash_file(Path(path)) for path in receipt['runtime_artifacts']}\n    require(artifacts==receipt['runtime_artifacts'],'changed runtime artifacts')","artifacts={item['path']:hash_file(Path(item['path'])) for item in receipt['runtime_artifacts']}\n    require(artifacts=={item['path']:item['sha256'] for item in receipt['runtime_artifacts']},'changed runtime artifacts')")
write('audit-terminal.py',audit)

js('FINAL-CENSUS-PLAN.json',{
 'status':'PREDECLARED_SOURCE_PROPOSAL_BEFORE_ANY_REPAIRED67_OPERATIONAL_SEARCH',
 'candidate_frozen_stream':candidate,'candidate_final_stream':'Identical audited17898304-op prefix plus selected lowest-passing48XX identity tail; final generated hash must be recorded.',
 'parent_stream':declaration['original_stream_sha256'],'label':'repair67-conditional-finalnonce-20261016-v1',
 'first_batch':0,'batches_per_source':32768,'shots_per_source':2097152,
 'workers_per_source':4,'paired_sources':'Sequential, never more than8total workers; inspect resources first.',
 'runner':'/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2',
 'runner_sha256':'790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66',
 'pass':'Every predeclared row included, candidate failed batches<=paired record parent and failures per141batches<=18, candidate dirty0. Refresh public record before launch and final comparison.',
 'failure_action':'Retain every result, no resampling/relabeling/circuit tuning/submission of failed final candidate.',
 'timing':'Only after lowest-pass log audit, selected final source generation, prefix identity audit and unchanged full official native benchmark.',
 'separate_from_search_eligibility':True,'submission_mode':'queue'})
f=4134/32768;expected=(1-f)**-141
js('ACCEPTANCE-REQUIREMENTS.json',{
 'status':'REQUIREMENTS_ONLY_NO_ACCEPTANCE_CREATED',
 'hard_gates':['PROOF_ACCEPTED false in proposed tool; coordinator PROPOSAL_DISABLED true; launch/build wrappers exit2.',
  'No runtime/search activation from theorem, census, this source proposal or old25 acceptance.',
  'Only a NEW source revision independently reviewed by root may remove these gates.'],
 'required_before_build':['Root authorizes bounded build/test resources; preserve existing25 unchanged.','Exact reviewed precursor sources match PRECURSOR_SOURCE_PINS and full proposal diff reviewed.'],
 'required_before_launch':['Terminal disabled repaired67 qualification has all forced scheduler controls, full9024 q/bit/phase/MR equality, original2a zeroIR shadows, fixed445 containment, high-ID and partial packing tests PASS.',
  'Independent complete generated-source, local contracts, conditional induction, compiler/ABI and cache67 proof review PASS; exact acceptance/theorem/source/binary/runtime hashes frozen.',
  'Operational false-to-true gate changes get a separate review; every root/classical ID mapping and own candidate Fiat prefix/tail pinned; scalar library resolved path SHA pinned.',
  'New bounded FOUR-process2-thread cost test demonstrates aggregate8-thread expected search<=24h with startup cost and resource contention included; no projection from48threads or singleprocess qualifies.',
  'Remaining authorized run time can accommodate the chosen cap and official native/final fresh census work; root explicitly decides whether another long search is justified.',
  'Refresh official public records; frozen fresh source census must still beat record failure rate and cap18. No old4b mask transfer absent conditionalG.',
  'All lower nonce rows/unique partitions and deadline/pass race audit tested; exact candidate fallback for all uncertified inputs, phase/garbage checks and all physical MR draws remain.'],
 'runtime_binding_fields':['operational_executable_sha256','runtime_artifacts[] path/sha256','candidate_stream_sha256','mask_sha256','guard_sha256','conditional_theorem_sha256','disabled_qualification_pass','independent_operational_review_pass','cost_gate_pass','failure_gate_pass','fresh_public_record_comparison_pass','measured_expected_hours_8threads','preliminary_distinct_timing_nonces'],
 'cost_bound':{'assumption':'Independent fresh-batch estimate only; not a guarantee or new eligibility census.','candidate_failed_batches':4134,'fresh_batches':32768,'packet_batches':141,'expected_nonces':expected,'minimum_aggregate_nonces_per_second_for24h':expected/86400,'maximum_aggregate_thread_seconds_per_nonce_8threads':8*86400/expected,'single2thread_4096_trial_seconds_for_ideal_linear8thread24h':4096*4*86400/expected,'probability_at_count_N':'1-(1-(1-4134/32768)^141)^N','decision':'If measured bound exceeds24h or remaining run time, do not start; retain proposal as cost-negative. No automatic extra run.'},
 'after_pass':['Complete immutable JSONL unique/lower-prefix audit','Final actual source/pre-tail identity validation','Unchanged full official native benchmark','Separately predeclared final32768 paired census with retained runner790e and noresampling','Queue candidate/evidence only; no external submission']})
baseline_names=['prepare.py','search.rs','coordinator.py','run-search.sh','audit-terminal.py']
diff=''
for n in baseline_names:
 diff+=''.join(difflib.unified_diff((old/n).read_text().splitlines(True),(out/n).read_text().splitlines(True),fromfile='active25/'+n,tofile='repair67-proposal/'+n))
write('SOURCE-DIFF.patch',diff)
js('PROPOSAL-SOURCE-RECEIPT.json',{'status':'SOURCE_ONLY_NO_PREPARE_BUILD_OR_LAUNCH',
 'active25_reference_files':{n:sha(old/n)for n in baseline_names},
 'copied_precursor_review_sha256':sha(review/'REVIEW-v2.json'),
 'proposal_files':{p.name:sha(p)for p in out.iterdir()if p.is_file()},
 'disabled_acceptance_created':False})
print(json.dumps({'folder':str(out),'files':len(list(out.iterdir())),'expected_nonces':expected,'proposal_receipt_sha256':sha(out/'PROPOSAL-SOURCE-RECEIPT.json')}))
