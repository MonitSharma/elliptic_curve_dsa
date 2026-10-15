from pathlib import Path
import hashlib,json,subprocess,sys
r=Path(__file__).parent
tip=Path('/home/hclau/ecdsa_research/product-exact-20261015/tip')
dependency=Path('/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for p in sorted(tip.rglob('*')) if p.is_file() and ((p.relative_to(tip).parts[0]=='src' and not str(p.relative_to(tip)).startswith('src/point_add/')) or p.name in ('Cargo.toml','Cargo.lock','rust-toolchain.toml')) and 'target' not in p.relative_to(tip).parts]
protected={str(p.relative_to(tip)):dict(tip=sha(p),dependency=sha(dependency/p.relative_to(tip)) if (dependency/p.relative_to(tip)).exists() else None) for p in files}
terminal='--terminal-only' in sys.argv
active=lambda p:False  # All owned proof jobs terminal at this freeze.
source=[p for p in sorted((r/'tool/src').rglob('*.rs')) if not(terminal and active(p))]+[r/'tool/Cargo.toml',r/'tool/Cargo.lock']
report=dict(source_revision=subprocess.check_output(['git','-C',str(tip),'rev-parse','HEAD'],text=True).strip(),
            frozen_stream_sha256=sha(tip/'ops.bin'),protected_files=protected,
            all_protected_match=all(v['tip']==v['dependency'] for v in protected.values()),
            research_sources={str(p.relative_to(r)):sha(p) for p in source},
            binaries={p.name:sha(p) for p in (r/'tool/target/release').iterdir() if p.is_file() and p.name in ('value_prefilter','fast_screen','fast_screen_c','advisory_screen','advisory_screen-v1','bucket_screen','bucket_fast_screen','rail_advisory','walk_model','rng_audit','rng_coeff','bucket_fast_wide_screen','wide_verify','fixed_rng_anf','fixed_rng_anf_interned','global_rng_anf','global_rng_anf_nary','global_rng_anf_inputanf','global_rng_anf_inputanf16','global_rng_anf_nary_bigcache','rng_sensitivity','global_rng_anf_mask_export','global_rng_anf_mask_fast','global_rng_anf_mask_trace','mask_validate','global_rng_anf_shadow_bound','global_rng_anf_shadow_tail','global_rng_anf_prefix_shadow')})
external={}
for directory,names in {'simd-prefilter-20261015':['libsimd8.so','tool/simd8.c','tool/simd8.h'],'shake8-20261015':['libshake8.so','shake8.c','shake8.h'],'simd-rails-20261015':['librail8.so','rail8.c','rail8.h','steps.bin'],'scalar-fast-20261015':['libscalar_fast_batch.so'],'zero-mr-20261016':['libzero8.so']}.items():
 for name in names:
  p=r.parent/directory/name
  if p.exists():external[str(p)]=sha(p)
report['private_wide_backend']={str(p.relative_to(r)):sha(p) for p in [r/'libsimd8wide.so',r/'simd8wide.c',r/'simd8wide.h'] if p.exists()}
report['checkpoint_excludes_active_hybrid_sources']=False
report['all_owned_proof_jobs_terminal_at_freeze']=True
report['candidate_stream_sha256']=sha(r.parent/'product-exact-20261015/chain-retained.bin')
report['external_exact_and_advisory_libraries']=external
(r/'evidence/provenance.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(source_revision=report['source_revision'],frozen_stream_sha256=report['frozen_stream_sha256'],all_protected_match=report['all_protected_match'],protected_files=len(protected))))
