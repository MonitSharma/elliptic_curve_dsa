"""Source-only feasibility planner; the renderer is never called."""
import hashlib,json,shutil
from pathlib import Path
r=Path(__file__).resolve().parent;tool=r/'endpoint-proposals-tool';d=r/'endpoint-proposals-20261016'
assert (r/'endpoint-classification.exit').read_text().strip()=='0'
assert not tool.exists() and not d.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((r/'PRODUCT95_FREEZE.json').read_text());stream=r/freeze['external_stream'];assert sha(stream)==freeze['external_stream_sha256']
origin=Path('/home/hclau/ecdsa_research/global-scope-proposals-20261016/tags.rs');tags=origin.read_text()
shutil.copytree(r/'flags-tool',tool,ignore=shutil.ignore_patterns('target'))
p=tool/'src/lazy_cache_retained.rs';s=p.read_text()
start=s.index('    if std::env::var("CACHE_SEMANTIC_END")');end=s.index('    let mut proposals=',start)
s=s[:start]+'''    let raw_end_ok=end_ok.clone();
    let mut checks:std::collections::BTreeMap<usize,Vec<usize>>=std::collections::BTreeMap::new();
    let mut wanted=HashSet::new();
    for (key,uses) in &groups {if !key.1.is_empty() && uses.len()>1 {for &at in uses.iter().skip(1) {if !raw_end_ok[at] {checks.entry(ends[at]).or_default().push(at);wanted.insert(at);}}}}
    for ats in checks.values_mut(){ats.sort_unstable();}
    let mut proof=super::interned_anf_retained::Support::new(&ops);
    let mut expected:HashMap<usize,(bool,Vec<u64>)>=HashMap::new();let mut recovered=0usize;
    for i in 0..=ops.len(){
        if let Some(ats)=checks.get(&i){for &at in ats {let old=expected.remove(&at).unwrap();if proof.cache_product(&ops[at])==old{end_ok[at]=true;recovered+=1;}}}
        if i<ops.len(){if ops[i].kind==K::CCX{let key=proof.cache_product(&ops[i]);if wanted.contains(&i){assert!(expected.insert(i,key).is_none());}}proof.step(&ops[i]);}
    }
    assert!(expected.is_empty());println!("ENDPOINT_WITHIN_PASS recovered_nonconstant={recovered} candidates={} no_cross_pass_ID_comparison=true",wanted.len());
''' + s[end:]
needle='let mut proposals=vec![];let mut repeated=0;let mut repetitions=0;'
assert s.count(needle)==1;s=s.replace(needle,needle+'let first_use=first_use_tags(&ops,nb as usize);let mut excluded=0usize;')
needle='for (_,mut uses) in groups {';assert s.count(needle)==1;s=s.replace(needle,'for (key,mut uses) in groups {if key.1.is_empty(){continue;}')
needle='if !end_ok[*us.last().unwrap()] {continue;}'
assert s.count(needle)==1;s=s.replace(needle,'if !end_ok[*us.last().unwrap()] || raw_end_ok[*us.last().unwrap()] {continue;}if same_first_use_epoch(&us,&first_use){excluded+=1;continue;}')
# Only split64 is admitted. The unused whole-group branch is disabled.
needle='let split=std::env::var("CACHE_SPLIT").ok().map_or(false,|v|v=="1");';assert s.count(needle)==1;s=s.replace(needle,needle+'assert!(split);')
needle='for w in proposals {';assert s.count(needle)==1;s=s.replace(needle,needle+'if w.proxy<=1e-12{continue;}')
needle='    render(ops,chosen,nb,nq)';assert s.count(needle)==1;s=s.replace(needle,'    println!("ENDPOINT_PROPOSAL_ONLY selected={} excluded_same_first_use_epoch={excluded} structural_proxy_only=true emits_stream=false sampled_inputs=0 no_renderer=true",chosen.len());\n    ops')
s+='\n'+tags;p.write_text(s)
main=tool/'src/main.rs';s=main.read_text();start=s.index('fn main(){');s=s[:start]+'''fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);let ops=load_ops(&args[1]).unwrap();let _unchanged=lazy_cache_retained::optimize(ops);}
''';main.write_text(s)
d.mkdir();shutil.copy2(origin,d/'tags-origin.rs')
plan=dict(status='PREDECLARED_SOURCE_ONLY_RESTORED_ENDPOINT_DONOR_FEASIBILITY',stream=freeze['external_stream'],stream_sha256=freeze['external_stream_sha256'],input_freeze_sha256=sha(r/'PRODUCT95_FREEZE.json'),classifier_result_sha256=sha(r/'endpoint-classification-20261016/RESULTS.json'),atom_cap=1024,pair_cap=64,product_cap=1000000,rank='density',split_max_uses=64,positive_proxy_threshold=1e-12,workers=1,address_limit_GiB=24,time_limit_seconds=7200,tag_helper_source=str(origin),tag_helper_sha256=sha(origin),emits_stream=False,sampled_inputs=0,scope='Nonconstant repeated products only; each selected endpoint must fail the old physical-write fence but pass a same-instance endpoint product check. Existing zero-donor/touch/nonoverlap allocator retained. Same monotone first-use proposals excluded. Proxy assumes fair independent guards and is not an executed T mean. No renderer, candidate, universal cache proof, native port, failure gate or nonce is authorized by these counts.',source_files_sha256={str(p.relative_to(tool)):sha(p) for p in tool.rglob('*') if p.is_file()})
(d/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan))
