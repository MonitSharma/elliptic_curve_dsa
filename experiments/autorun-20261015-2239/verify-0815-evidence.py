"""Independent archive integrity and result arithmetic, no active-job mutation."""
from pathlib import Path,PurePosixPath
from collections import Counter
from fractions import Fraction
import hashlib,json,statistics,tarfile

BASE=Path(__file__).resolve().parents[2]/'experiments'
CASES=[
 ('census-control-family','evidence.tar.gz','manifest.json','23b6a65c55d1c5c191c892ee37e2b03d2d57c700c6bbd607a1b1851d155976a6'),
 ('census-control-review','review-v1.tar.gz','MANIFEST.json','675b67df79d197ee1d9b02d45b1279e02d6d6e930405dce8726cf9f114d6d6f9'),
 ('scalar-window-audit','evidence.tar.gz','MANIFEST.json','7411dc6d4dc489055e2998f7f061ba058964610171d6ffe2b6341b23dbef7565'),
 ('all70-value-transfer','evidence.tar.gz','MANIFEST.json','41c13293342222dbd8470d6bc8f03085961eb8982c466e37716477e117d33df0'),
 ('wide-cache-cleanup-audit','evidence.tar.gz','manifest.json','a9135be87a649820c2ee1fbb2288a342f82e2fd3a2551127ca0dbc5fe6966ee1'),
 ('n2-readonly-normalizers','source-only-readonly-v1.tar.gz','source-only-readonly-v1/MANIFEST.json','5517f914dbc8070753a5bfbb410f05c3efc96274de1ca752838ecb2e9575aa92'),
]
def digest(b):return hashlib.sha256(b).hexdigest()
for case,archive,manifest_name,expected in CASES:
    folder=BASE/(case+'-20261016');p=folder/archive
    assert digest(p.read_bytes())==expected,(case,'archive')
    with tarfile.open(p) as t:
        names=t.getnames();assert len(names)==len(set(names))
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names)
        assert all(m.isfile() or m.isdir() for m in t.getmembers())
        read=lambda n:t.extractfile(n).read()
        load=lambda n:json.loads(read(n))
        manifest=load(manifest_name);files=manifest.get('files',manifest)
        prefix=manifest_name[:-len(PurePosixPath(manifest_name).name)]
        for name,info in files.items():
            raw=read(prefix+name)
            if isinstance(info,str):assert digest(raw)==info,(case,name)
            else:assert len(raw)==info['bytes'] and digest(raw)==info['sha256'],(case,name)
        detail={}
        if case=='census-control-family':
            all144=load('ALL144.json');all70=load('ALL70.json');summary=load('SUMMARY.json')
            assert len(all144)==144 and len(all70)==70
            assert Counter(r['action']=='del' for r in all144)=={True:74,False:70}
            assert all(r['old'][0]==13 for r in all144)
            assert all(r['new'][0]==8 and r['action'].startswith('cx:') for r in all70)
            assert len({r['row'] for r in all70})==70
            assert [r for r in all144 if r['action']!='del']==all70
            assert summary['scope_depths']=={'0':56,'1':14}
            assert Fraction(56)+Fraction(14,2)==Fraction(summary['restoration_depth_weight_exact'])==63
            assert summary['universal_added_executed_T_bounds']==[56,70]
            assert not summary['static_depth_weight_is_fresh_expected_T']
            detail=dict(all144=144,all70=70,restoration_T_bounds=[56,70],proxy_not_fresh_T=True)
        elif case=='census-control-review':
            report=load('REVIEW.json');source=load('NATIVE-SOURCE-REVIEW.json')
            assert report['entire_before144_application_equals_final_actual_bytes']
            assert report['all70_uniform_CCX_to_CX'] and report['all74_deletions_retained_as_separate_family']
            assert report['executed_added_T_per_shot_bounds']==[56,70]
            assert len(report['helper_lifecycles'])==70
            assert Counter(str(r['next_value_write']['kind']) for r in report['helper_lifecycles'])=={'8':61,'12':5,'13':4}
            assert source['strict_family_count_assertion']==[144,74,70,0]
            assert source['only_tracked_source_change'] and source['all_original_anchor_row_assertions_retained']
            assert source['complete_helper_cleanup_not_proved'] is True
            detail=dict(independent_agent_source_binding_report_consistent=True,native_byte_verification_at_archive_time='PENDING',not_global_correctness=True)
        elif case=='scalar-window-audit':
            result=load('RESULT.json');analysis=load('ANALYSIS.json');rows=result['results']
            assert result['status']=='PASS' and result['all_outputs_equal_old20_and_preserved_protected_Rust']
            assert len(rows)==12 and {(r['window'],r['trial']) for r in rows}=={(w,i) for w in [13,16,18,20] for i in range(3)}
            assert len({r['output_sha256'] for r in rows})==1
            for r in rows:
                assert r['pairs']==131072 and r['passes']==32 and r['batch']==64 and len(r['pass_ns'])==32
                assert abs(r['us_per_pair']-r['call_loop_ns']/131072/1000)<1e-12
                assert digest(read(f"output-{r['trial']}-{r['window']}.bin"))==r['output_sha256']
                assert r['invalid_count_controls']==[65,4294967295] and not r['authority']
            for s in analysis['summary']:
                vals=[r['us_per_pair'] for r in rows if r['window']==s['window']]
                assert statistics.median(vals)==s['median_us_per_pair']
            detail=dict(all12_full_output_hashes_identical=True,all_timing_arithmetic_recomputed=True,stable_compute_gain=False,production_adopted=False)
        elif case=='all70-value-transfer':
            receipt=load('TERMINAL-RECEIPT.json');cl=load('CLASSIFICATION.json');sw=load('SWAP-REFINEMENT.json')
            assert digest(read('CLASSIFICATION.json'))==receipt['classification_sha256']
            assert digest(read('SWAP-REFINEMENT.json'))==receipt['swap_refinement_sha256']
            assert len(cl['sites'])==70 and len(sw['reports'])==7
            assert all(s['scan_both_old_and_restored_operand_sets'] for s in cl['sites'])
            assert all(len(r['swaps'])==3 and r['status']=='UNKNOWN_VALUE_CONTROL_FANOUT_AFTER_SWAP' for r in sw['reports'])
            assert receipt['direct_value_control_before_unconditional_reset']==63 and receipt['admitted_phase_only_reset_frames']==0
            primitive=load('PRIMITIVE-CHECKS.json');assert primitive['exhaustive_cases']==128 and not primitive['authority']
            detail=dict(all70_structural_fanout=True,no_phase_only_transfer=True,Boolean_fixture_only=True,not_proof_of_final_value_change=True)
        elif case=='wide-cache-cleanup-audit':
            result=load('RESULT.json');assert len(result['stage_order'])==15 and len(result['renderers'])==8
            assert result['uncompensated_cache_cleanup_CCX_families']==0
            assert len({r['render_sha256'] for r in result['renderers']})==1
            for r in result['renderers']:
                raw=read('frozen-source/'+Path(r['source']).name)
                assert digest(raw)==r['sha256']
                text=raw.decode();render=text[text.index('fn render('):text.index('\npub fn audit(')]
                cleanup=render[render.index('if let Some(js)=ends.get'):render.index('if let Some(js)=starts.get')]
                assert digest(render.encode())==r['render_sha256'] and digest(cleanup.encode())==r['cleanup_sha256']
                assert 'CCX' not in cleanup and 'Hmr' in cleanup and 'CZ' in cleanup
                assert r['cleanup_CCX']==0 and r['all_renderer_CCX_count']==1
            detail=dict(all15_stages_eight_identical_renderers=True,cleanup_CCX=0,new_candidate=False)
        elif case=='n2-readonly-normalizers':
            result=load(prefix+'RESULT.json');assert result['no_candidate'] and result['no_sample'] and result['no_rewrites']
            assert result['before_after_source_pins_identical'] and len(result['phases'])==2
            dirty=zero=0
            for phase in result['phases']:
                assert not phase['candidate_limit_truncated']
                for q in phase['queries']:
                    if q['dirty_atom_count']:
                        dirty+=1;assert q['affine_q'] is None and q['affine_q_stable_classical'] is None
                        assert q['existing_physical_product_rhs'] is None and not q['affine_factor_rhs']['expressible']
                    else:zero+=1
            assert (dirty,zero)==(12,4)
            detail=dict(all16_targets_12_nonconstant_negative=True,external_refs_not_locally_reexecuted=len(manifest['external']),not_a_candidate=True)
    receipt=dict(status='ROOT_ARCHIVE_AND_RESULT_CONSISTENCY_PASS',archive_sha256=expected,stored_files_verified=len(files),detail=detail)
    (folder/'ROOT_REVIEW.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(case=case,**receipt)))
