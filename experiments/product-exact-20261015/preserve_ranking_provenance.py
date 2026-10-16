"""Preserve the actual structural ranking code, independent of proof packets."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'rank-source';d.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['lazy_cache.rs','lazy_cache_anf.rs','lazy_cache_retained.rs','main.rs'];files={}
for name in names:
    source=r/'flags-tool/src'/name;destination=d/name
    if destination.exists():assert sha(source)==sha(destination)
    else:shutil.copy2(source,destination)
    files[name]=sha(source)
for name in names[:3]:
    s=(r/'flags-tool/src'/name).read_text()
    for snippet in ['0.5f64.powi(depth as i32+if o.c_condition==NO_BIT{0}else{1})','let union_proxy=1.0-','proxy:weight_sum-union_proxy','(a.start,a.end,&a.uses).cmp(&(b.start,b.end,&b.uses))','b.proxy.total_cmp(&a.proxy)']:
        assert snippet in s,(name,snippet)
    assert 'rng' not in s.lower() and 'nonce' not in s.lower()
row={'status':'SOURCE_ONLY_ANALYTICAL_RANKING','generator_executable':'target-flags/release/product_paired_diagnostic','generator_executable_sha256':sha(r/'target-flags/release/product_paired_diagnostic'),'source_snapshot':'rank-source','source_files_sha256':files,'weights':'For a source CCX at PushCondition depth d, w=2^-(d+g), where g=1 iff c_condition is present, otherwise0. Uses only operation nesting and guard presence.','proxy':'For a repeated-product proposal U, sum(w_i) - (1-product(1-w_i)). This assumes independent fair guard events only as an allocation heuristic, without sampling actual guard values.','start':'Sort lexicographically by(start,end,use_indices).','proxy_rank':'Sort descending proxy, ties lexicographically by(start,end,use_indices).','density_rank':'Sort descending proxy/(end-start), same lexicographic ties.','eligibility':'Immutable symbolic repeated-product identities, universal-zero donor proof, raw source touch/control fences, lexical condition boundaries. Greedy allocator rejects overlapping source uses and donor lifetimes.','not_inputs':['anchored-packet values','packet Toffoli counts','failure flags or failure counts','curve-input samples','identity-tail nonce','census rows or benchmark outcomes'],'exactness':'Ranking selects among universally exact rewrites; it does not establish equalities or replace proof. Conservative Boolean identities and the HMR/CZ gadget plus full source-bound verifier supply the equivalence obligations.','schedules':'Final67 and both95 schedules are fixed and separately frozen before their own measurements. Checkpoint metrics are reported only; no packet-selected stopping or in-run rank/cap changes.','relevant_artifacts':['PRODUCT67_FREEZE.json','product-to67-rank-20261016/DECLARATION.txt','product-to95-rank-20261016/DECLARATION.json','wide-to95-rank-20261016/DECLARATION.json'],'score':None}
for path in [r/'CACHE_RANKING_PROVENANCE.json',r/'CACHE_RANKING_PROVENANCE.md']:assert not path.exists()
(r/'CACHE_RANKING_PROVENANCE.json').write_text(json.dumps(row,indent=2)+'\n')
(r/'CACHE_RANKING_PROVENANCE.md').write_text('''# Cache ranking provenance

The start/proxy ranks used for product67 and the fixed95 continuations use
source structure and an analytical probability approximation only. For each
CCX at condition-stack depth d, assign w=2^-(d+g), where g records whether an
explicit classical guard exists. For a proposal, the proxy is
sum(w_i) - (1-product(1-w_i)). It assumes independent fair guard events;
actual guard values are never sampled for ranking.

Start sorts by source start, end and use indices. Proxy sorts by descending
proxy with the same lexical ties. Density sorts by proxy divided by source
interval length. Symbolic identities, zero donors, source touch/control fences
and nonoverlapping intervals determine eligibility. These heuristic scores do
not prove equivalence; the independent symbolic/gadget audits do that.

The optimizer does not read packet values, measured T, failure flags, sampled
curve inputs, nonce outcomes or census rows. The separate67/95 schedules and
endpoints were frozen before their measurements. Reported checkpoint counts
do not feed back into an in-progress recipe or choose an earlier endpoint.
The JSON binds the actual executable and archived allocator source snapshots;
the full flags-tool source is also retained in the evidence archive.
''')
print(json.dumps({'report_sha256':sha(r/'CACHE_RANKING_PROVENANCE.json'),'source_files_sha256':files}),flush=True)
