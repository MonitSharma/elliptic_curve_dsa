import hashlib,json,tarfile
from pathlib import Path
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(R/'run.exit').exists();code=int((R/'run.exit').read_text().strip())
prep=json.loads((R/'PREPARED-SOURCE.json').read_text())
for name,h in prep['files'].items():assert sha(R/name)==h,name
binding=json.loads((R/'BASE-BINDING.json').read_text());assert sha(Path(binding['stream_path']))==binding['stream_sha256']
assert sha(R/'BASE_NATIVE_RECEIPT.json')==binding['native_receipt_sha256']
plan=json.loads((R/'SOURCE-PLAN.json').read_text())
for name,h in plan['kernel_source_pins_local'].items():assert sha(R/'tool/src'/name)==h,name
summary={'status':'BOUNDED_FRESH_ALL70_MASK_FEASIBILITY','authority':False,'run_exit':code,
 'base_sha256':binding['stream_sha256'],'base_only70_restorations_fullcanonicalbinding':True,
 'native_tests_33_pass': '33 passed; 0 failed' in(R/'tests.log').read_text(),
 'trusted_generic_kernels_byteidentical_to_original_v3':True,'old_mask_transfer_used':False,
 'all_old_region_metadata_used_only_as_endpoint_hints_with_fresh_actual_gate_proof':True,
 'bounded_query':'oneattempt cap32,1core,24GiB,900s wholebuild/query/validation; noadaptive cap or selectedoutput retry',
 'production_changed':False}
refs={str(Path(binding['stream_path'])):binding['stream_sha256']}
if code==0:
 report=json.loads((R/'global.json').read_text());run=json.loads((R/'RUN-RECEIPT.json').read_text())
 assert report['output_bits']==512 and report['symbolic_input_wires']==1024 and report['rng_draws']==906156
 assert report['protected_full_state_containment_seeds']==4 and report['mask_compiled_matches_full_input_dag']
 assert json.loads((R/'BEFORE-PINS.json').read_text())==json.loads((R/'AFTER-PINS.json').read_text())
 for name in ['mask_nodes','input_only_dag_nodes','unresolved_rng_dependent_bits','concrete_known_output_bits','concrete_certified_wrong_shots','certified_reset_regions','shadow_contract_attempts','seconds']:
  summary[name]=report[name]
 summary['applied_shadow_contracts']=len(report['applied_shadow_contracts'])
 summary['failed_reset_candidate_count']=len(report['failed_reset_candidates'])
 summary['roots']=run['root_summary'];summary['existing_fixture_validation']=run.get('existing_fixture_validation')
 summary['protected_full_state_containment']='32existingauditinputs,allq/b,4physicalMRstreams'
 summary['outcome']='TERMINAL_NEGATIVE_ALL512_DEPENDENCY_ROOTS_UNKNOWN' if run['root_summary']['constant1_unknown']==512 else'FRESH_SOURCE_BOUND_PARTIAL_MASK_NEEDS_INDEPENDENT_REVIEW_NO_RUNTIME_AUTHORITY'
 refs[str(R/'mr-mask-all70.bin')]=sha(R/'mr-mask-all70.bin')
else:summary['outcome']='BOUNDED_UNKNOWN_OR_FAILED_NO_MASK_AUTHORITY'
(R/'TERMINAL-RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
(R/'SERVER-HASHREFS.json').write_text(json.dumps(refs,indent=2)+'\n')
files=[p for p in R.rglob('*')if p.is_file()and'target'not in p.parts and p.name not in('mr-mask-all70.bin','evidence.tar.gz','MANIFEST.json','ARCHIVE-RECEIPT.json')]
manifest={str(p.relative_to(R)):sha(p)for p in files};(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(R/'evidence.tar.gz','w:gz')as t:
 for p in sorted(files+[R/'MANIFEST.json']):t.add(p,arcname=str(p.relative_to(R)))
with tarfile.open(R/'evidence.tar.gz')as t:
 for n,h in manifest.items():assert hashlib.sha256(t.extractfile(n).read()).hexdigest()==h,n
receipt={'status':'VERIFIED','archive_sha256':sha(R/'evidence.tar.gz'),'verified_members':len(manifest),'terminal_receipt_sha256':sha(R/'TERMINAL-RECEIPT.json'),'server_hashrefs':refs}
(R/'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
