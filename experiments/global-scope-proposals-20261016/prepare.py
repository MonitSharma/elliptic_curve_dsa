from pathlib import Path
import hashlib,json,shutil
r=Path(__file__).resolve().parent;old=r.parent/'product-exact-20261015/scoped-cache-tool'
assert not (r/'tool').exists()
shutil.copytree(old,r/'tool',ignore=shutil.ignore_patterns('target','.git'))
p=r/'tool/src/lazy_cache_retained.rs';s=p.read_text()
assert hashlib.sha256(p.read_bytes()).hexdigest()=='cb0b0bb526d6f1e7f8b69d7303bcee01a87fc4f7b951bae767feea2b7c66c7f0'
a=s.index('    let first=uses[0];let last=*uses.last().unwrap();let a=&contexts[&first];let b=&contexts[&last];')
b=s.index('\n}',a)
s=s[:a]+'''    let first=uses[0];let last=*uses.last().unwrap();
    let _=(contexts,pops);let end=last+1;
    if fences[last]<end {None}else{Some((first,end))}'''+s[b:]
needle='    let mut proposals=vec![];let mut repeated=0;let mut repetitions=0;'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n    let first_use=first_use_tags(&ops,nb as usize);let mut excluded=0usize;\n    println!("GLOBAL_FIRST_USE_TAGGED sites={}",first_use.iter().filter(|x|x.is_some()).count());')
needle='                let us=uses[lo..hi].to_vec();'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n                if same_first_use_epoch(&us,&first_use){excluded+=1;continue;}')
needle='            if uses.len()<2 {continue;}\n            let (start,end)='
assert s.count(needle)==1
s=s.replace(needle,'            if uses.len()<2 {continue;}\n            if same_first_use_epoch(&uses,&first_use){excluded+=1;continue;}\n            let (start,end)=')
needle='    render(ops,chosen,nb,nq)';assert s.count(needle)==1
s=s.replace(needle,'    println!("GLOBAL_PROPOSAL_ONLY excluded_same_first_use_epoch={excluded} chosen={} no_renderer=true no_output_stream=true",chosen.len());\n    ops')
s+='\n'+(r/'tags.rs').read_text();p.write_text(s)
p=r/'tool/src/main.rs';s=p.read_text();needle='};write_ops(&revised,Path::new(&args[2])).unwrap();'
assert s.count(needle)==1
s=s.replace(needle,'};let _=revised;println!("GLOBAL_PROPOSAL_COMPLETE no_output_stream=true");')
p.write_text(s)
sources={str(p.relative_to(r/'tool')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/'tool').rglob('*') if p.is_file() and 'target' not in p.relative_to(r/'tool').parts}
(r/'PREPARED-SOURCE.json').write_text(json.dumps({'historical_source_sha256':'cb0b0bb526d6f1e7f8b69d7303bcee01a87fc4f7b951bae767feea2b7c66c7f0','private_files':sources,'no_renderer_or_stream_emission':True},indent=2)+'\n')
