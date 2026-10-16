from pathlib import Path
import json,hashlib,tarfile,io
r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(r/'run.exit').read_text().strip()=='0'
assert(r/'binary-before.sha256').read_bytes()==(r/'binary-after.sha256').read_bytes()
for n,h in json.loads((r/'PREPARED_SOURCE.json').read_text()).items():assert sha(r/n)==h,n
result=json.loads((r/'RESULT.json').read_text());on=next(x for x in result['records']if x['mode']=='on');off=next(x for x in result['records']if x['mode']=='off')
m={x['name']:x for x in on['profile']['metrics']}
curve=m['prep_curve_C_paircall'];rail=m['prep_rail_C_walk'];keys=m['prep_SHAKE_key_read']
assert curve['units']*64==keys['units'] and curve['calls']==keys['calls']
point_count=curve['units'];assert point_count>0
nonoverlap_names=['prep_key_buffer_alloc','prep_SHAKE_key_read','prep_scalar_decode_alloc','prep_curve_input_BE_pack_alloc','prep_curve_output_buffer_alloc','prep_curve_C_paircall','prep_curve_output_decode_alloc','prep_curve_valid_point_filter','prep_point_vector_alloc','prep_rail_init_once','prep_rail_denominator_pack_alloc','prep_rail_flags_alloc','prep_rail_C_walk','prep_rail_shadow_reference','prep_flag_candidate_collect','prep_nonce_hash_packet_create_inclusive','prep_packet_container_push']
total=sum(m[n]['seconds']for n in nonoverlap_names)
analysis={'status':'SAME4096_SOURCE_AND_ROW_IDENTICAL_FINE_PROFILE_DESCRIPTIVE_ONLY',
 'off_process_wall_seconds':off['process_wall_seconds'],'off_window_wall_seconds':off['window_wall_seconds'],
 'on_process_wall_seconds':on['process_wall_seconds'],'on_window_wall_seconds':on['window_wall_seconds'],
 'startup_main_to_window_seconds':m['startup_main_to_window']['seconds'],
 'candidate_seed_diagnostic_seconds':m['startup_candidate_seed_diagnostics']['seconds'],
 'unused_C_SHAKE8_update_seconds':m['startup_C_SHAKE8_updates_unused_base']['seconds'],
 'actual_Rust_SHAKE_prefix_update_seconds':m['startup_Rust_SHAKE256_updates']['seconds'],
 'fixed_scalar_table_init_seconds':m['startup_scalar_fixed_table_init']['seconds'],
 'prepared_scalar_pairs':point_count,'rail_checked_points':rail['units'],
 'key_read_bytes':keys['units'],'key_pairs_equal_curve_calls_units':True,
 'curve_C_worker_seconds':curve['seconds'],'curve_C_us_per_pair':curve['seconds']*1e6/point_count,
 'rail_C_worker_seconds':rail['seconds'],'rail_C_us_per_point':rail['seconds']*1e6/rail['units'],
 'selected_nonoverlap_worker_seconds':total,
 'selected_worker_seconds':{n:m[n]['seconds']for n in nonoverlap_names},
 'selected_worker_fraction':{n:m[n]['seconds']/total for n in nonoverlap_names},
 'all_metrics':on['profile']['metrics'],
 'source_observation':'The C SHAKE8 base is updated for every prefix byte but passed only to an unused _base parameter; actual Fiat reader uses Rust hash. Measurement does not remove it or establish operational acceptance for removal.',
 'limits':['Startup includes repeated diagnostic candidate-seed checks; persistent-worker perwindow time is separate.','Worker times sum across two threads and include descheduling; inclusive parent spans overlap children and must not be added to wall.','One off/on fixed trial pair does not establish stable instrumentation overhead, throughput, eight-thread forecast or a new search budget.','No circuit, source model, libraries, sampler, guard selection or active search changed.']}
(r/'ANALYSIS.json').write_bytes((json.dumps(analysis,indent=2)+'\n').encode())
archive=r/'evidence.tar.gz';assert not archive.exists()
files=[p for p in r.rglob('*')if p.is_file()and'target'not in p.relative_to(r).parts and'__pycache__'not in p.relative_to(r).parts]
manifest={'status':'DISABLED_INSTRUMENTATION_FULL_SOURCE_AND_EXACT_ROWS','files':[{'path':p.relative_to(r).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(files)],'hashrefs':[{'path':'../repair67-fused-filter-20261016/evidence.tar.gz','sha256':'7af8c67adb7698f01a43af981b8f1a6c78930d1178dc65ac5fbc69bbcf2de85b'},{'path':'tool/target/release/value_prefilter','sha256':(r/'binary-before.sha256').read_text().split()[0]}]}
with tarfile.open(archive,'w:gz')as t:
 for p in files:t.add(p,arcname=p.relative_to(r).as_posix(),recursive=False)
 b=(json.dumps(manifest,indent=2)+'\n').encode();i=tarfile.TarInfo('MANIFEST.json');i.size=len(b);t.addfile(i,io.BytesIO(b))
with tarfile.open(archive)as t:
 for x in manifest['files']:assert hashlib.sha256(t.extractfile(x['path']).read()).hexdigest()==x['sha256']
receipt={'status':'ALL_ARCHIVED_MANIFEST_ENTRIES_VERIFY','archive_sha256':sha(archive),'files':len(files),'analysis_sha256':sha(r/'ANALYSIS.json'),'binary_path':str(r/'tool/target/release/value_prefilter'),'binary_sha256':(r/'binary-before.sha256').read_text().split()[0]}
(r/'ARCHIVE-RECEIPT.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt));print(json.dumps({k:v for k,v in analysis.items()if k not in['all_metrics','selected_worker_seconds','selected_worker_fraction']}))
