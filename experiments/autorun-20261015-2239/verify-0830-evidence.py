"""Frozen archive, source binding and conservative result consistency review."""
from pathlib import Path,PurePosixPath
from collections import Counter,defaultdict
import hashlib,json,tarfile
ROOT=Path(__file__).resolve().parents[2]/'experiments'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
cases=[
('all70-mask-feasibility-20261016','evidence.tar.gz','MANIFEST.json','814a8e74aa0c4990e29cddf120a6739c117c45df773544bc6f83d5594ac58b87'),
('all70-mask-feasibility-20261016','metadata-supplement.tar.gz','METADATA-SUPPLEMENT-MANIFEST.json','6255ca9f9350ce3751866b7ba0da2256295335c80ab62e11656b6faf509079ef'),
('n2-temporal-storage-20261016','source-only-temporal-v1.tar.gz','source-only-temporal-v1/MANIFEST.json','ea135a9a0546176e0c36c2e1c774374ba000ad534b5c7b22eba8bffc49d09be3'),
('census-deletion-family-20261016','source-only-v1.tar.gz','source-only-v1/MANIFEST.json','93e34a44b9ab8e93e162838471a10b19ccbeb38758ebbf484f9ff46958d745e6'),
('census-deletion-n2-join-20261016','source-only-v1.tar.gz','source-only-v1/MANIFEST.json','352a56d8d6af597f6849864cf37c781bdf5144eacb0a8af74cfc021d273d348e'),
('census-control-review-20261016','native-review-v2.tar.gz','native-review-v2/MANIFEST.json','fbfad34af65010778211d1dd37c73e3ededcaf0a6ec3db509dc30b144c5a3324'),
]
for folder,archive,m,expected in cases:
    p=ROOT/folder/archive;assert sha(p.read_bytes())==expected
    with tarfile.open(p) as t:
        names=t.getnames();assert len(names)==len(set(names))
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
        assert all(r.isfile() or r.isdir() for r in t.getmembers())
        read=lambda n:t.extractfile(n).read()
        load=lambda n:json.loads(read(n))
        manifest=load(m);files=manifest.get('files',manifest);prefix=m[:-len(PurePosixPath(m).name)]
        for n,r in files.items():
            raw=read(prefix+n)
            if isinstance(r,str):assert sha(raw)==r,n
            else:assert len(raw)==r['bytes'] and sha(raw)==r['sha256'],n
        if folder=='all70-mask-feasibility-20261016' and archive=='evidence.tar.gz':
            report=load('TERMINAL-RECEIPT.json');query=load('global.json');plan=load('SOURCE-PLAN.json')
            assert query['source_stream_sha256']==report['base_sha256']=='06cdc5de3dadbe23a2ff306466ec2ef27514bed53be1145ec83bdf490cb99a7a'
            assert not report['authority'] and not report['old_mask_transfer_used']
            assert report['roots']=={'constant0_known':0,'constant1_unknown':332,'nonconstant':180}
            assert report['mask_nodes']==query['mask_nodes']==7918169
            assert query['mask_compiled_matches_full_input_dag'] and query['protected_full_state_containment_seeds']==4
            assert len(plan['kernel_source_pins_local'])==7
            for n,d in plan['kernel_source_pins_local'].items():assert sha(read('tool/src/'+n))==d,n
            assert read('run.exit').strip()==b'0'
            raw=load('mr-mask-all70.json');roots=raw['dependency_roots']
            assert len(roots)==512 and Counter(0 if r==0 else 1 if r==1 else 2 for r in roots)=={1:332,2:180}
            # These two exporter labels are explicitly INVALID for this fresh artifact.
            assert raw['original_stream_sha256'].startswith('2a522394') and raw['source_commit'].startswith('4b2ec52f')
            detail=dict(fresh_source_bound_06=True,all7_generic_kernels_unchanged=True,partial_roots180_unknown332=True,
                        invalid_legacy_exporter_labels_require_sidecar=True,not_a_runtime_or_failure_rate_claim=True)
            output='ROOT_MASK_ARCHIVE_REVIEW.json'
        elif folder=='all70-mask-feasibility-20261016':
            side=load('EXPORT-METADATA-CLARIFICATION.json')
            assert side['evaluated_source_stream_sha256']=='06cdc5de3dadbe23a2ff306466ec2ef27514bed53be1145ec83bdf490cb99a7a'
            assert sha(read('mr-mask-all70.json'))==side['raw_export_manifest_sha256']
            for n,d in side['authoritative_fresh_binding'].items():assert sha(read(n))==d,n
            assert read('BEFORE-PINS.json')==read('AFTER-PINS.json')
            assert side['preserved_original_archive_sha256']==cases[0][3]
            assert not side['authority'] and not side['program_or_proof_rerun']
            assert len(side['invalid_legacy_exporter_fields'])==2
            detail=dict(sidecar_binds_actual06_and_all_fresh_receipts=True,raw_program_external_hash_pinned=True,
                        consumers_must_reject_2a_only_binding=True)
            output='ROOT_METADATA_REVIEW.json'
        elif folder=='n2-temporal-storage-20261016':
            result=load(prefix+'RESULT.json');summary=load(prefix+'SUMMARY.json')
            assert sha(read(prefix+'RESULT.json'))==summary['result_sha256']
            assert result['no_candidate_or_sample'] and result['six_slots_not_an_information_theoretic_lower_bound']
            assert len(result['phases'])==2
            for phase,s in zip(result['phases'],summary['phases']):
                core=phase['optimistic_core_capacity'];start,end=core['start'],core['end'];events=defaultdict(int)
                for hole in phase['holes']:
                    a,b=max(start,hole['start']),min(end,hole['end'])
                    if a<b:events[a]+=1;events[b]-=1
                current=0;observed=[]
                for at in sorted(set(events)|{start,end}):
                    current+=events[at]
                    if at<end:observed.append(current)
                assert min(observed)==core['minimum']==s['minimum_core_capacity']==0
                assert max(observed)==core['maximum']==s['maximum_core_capacity']
                assert s['first_gradual_start_violation']['shortfall']==1
                assert s['first_gradual_start_violation']['capacity']==5 and s['first_gradual_start_violation']['separate_slot_demand']==6
            detail=dict(core_capacity_recomputed_from_all_holes=True,narrow_separate_slot_route_negative=True,
                        not_an_information_or_general_repair_impossibility=True)
            output='ROOT_REVIEW.json'
        elif folder=='census-deletion-family-20261016':
            s=load(prefix+'SUMMARY.json');rows=load(prefix+'ALL74.json')
            assert len(rows)==74 and s['rows']==74 and s['kinds']=={'13':74}
            assert s['scope_depths']=={'0':59,'1':15} and s['rigorous_added_executed_T_per_shot_bounds']==[59,74]
            assert s['syntactic_half_per_scope_proxy_exact']=='133/2' and s['proxy_not_measured_mean']
            assert s['all74_original_CCX_retained_in_virtual_view'] and s['all70_control_reductions_still_present_in_virtual_view']
            assert s['no_serialized_candidate'] and s['no_sampling'] and s['no_mask_transfer']
            detail=dict(all74_uniform_CCX_restore_inventory=True,T_bounds=[59,74],proxy66_5_not_measured_mean=True,no_candidate_or_sample=True)
            output='ROOT_REVIEW.json'
        elif folder=='census-deletion-n2-join-20261016':
            s=load(prefix+'SUMMARY.json');assert s['rows']==74 and s['all_source_rows_preserved']
            assert (s['all_add_instances'],s['add_boundary_queries'],s['loan_boundary_queries'])==(786,1572,8)
            seven=[2,5,6,7,8,9,10]
            assert s['divide_out_before_all_rail_potential_sources']==seven
            assert s['divide_out_before_q555_q556_potential_sources']=={'555':seven,'556':seven}
            assert len(s['multiply_out_before_all_rail_potential_sources'])==35
            detail=dict(complete74_rows_and_all_source_boundaries=True,seven_possible_divide_sources=seven,
                        structural_overapproximation_only=True,no_repair_or_causality_claim=True)
            output='ROOT_REVIEW.json'
        else:
            r=load(prefix+'NATIVE-BYTE-REVIEW.json');assert r['exactly70_current_CX_replaced_by_exact_source_CCX']
            assert r['every_other_original_Op_byte_identical'] and r['all_original_MR_classical_ABI_positions_tail_identical']
            assert r['all74_deletions_preserved'] and r['ops']==11630716
            assert r['candidate_canonical_sha256']=='9e964d38ba3c5f0ecadf21ad126cd6ab6f232a0be8e9d1ec3b551763ebf3bc3f'
            detail=dict(independent_complete_native_byte_review_consistent=True,no_whole_correctness_claim=True)
            output='ROOT_NATIVE_V2_REVIEW.json'
    out=dict(status='ROOT_FROZEN_ARCHIVE_AND_RESULT_CONSISTENCY_PASS',archive_sha256=expected,stored_files=len(files),detail=detail)
    (ROOT/folder/output).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(folder=folder,**out)))
