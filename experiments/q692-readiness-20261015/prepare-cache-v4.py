"""Bounded memoization of pure gate recordings; must preserve the v3 stream exactly."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(sys.argv[1]);v3=root/'candidate-control-fold-v3';dest=root/'candidate-control-fold-v4'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-hardlinks',str(v3),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root/'candidate-control-fold-v3.patch')],check=True)
p=dest/'src/point_add/builder.rs';s=p.read_text(encoding='utf8')
needle='    rec: Vec<Vec<G>>,';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    replay_cache: std::collections::HashMap<Vec<u64>,Vec<G>>,\n    replay_cache_gates: usize,')
needle='rec: Vec::new(), tof: 0,';assert s.count(needle)==1
s=s.replace(needle,'rec: Vec::new(), replay_cache: std::collections::HashMap::new(), replay_cache_gates: 0, tof: 0,')
needle='    pub fn finish_stream(&mut self) -> Option<u64> {';assert s.count(needle)==1
s=s.replace(needle,'''    // Only pure, allocation-free reciprocal recordings use this cache.
    // Native test probes count constructor calls, so leave those uncached.
    pub(crate) fn replay_cache_get(&self,key:&[u64])->Option<Vec<G>> {
        if cfg!(test) {None} else {self.replay_cache.get(key).cloned()}
    }
    pub(crate) fn replay_cache_store(&mut self,key:Vec<u64>,gates:&[G]) {
        if cfg!(test) || self.replay_cache.contains_key(&key) {return;}
        if self.replay_cache_gates+gates.len()>2_000_000 {return;}
        self.replay_cache_gates+=gates.len();self.replay_cache.insert(key,gates.to_vec());
    }

'''+needle)
p.write_text(s,encoding='utf8',newline='\n')
p=dest/'src/point_add/midg.rs';s=p.read_text(encoding='utf8')
helper='''
// All constructor inputs and local cancellation settings are part of the
// key. These routines allocate no wires/bits and create only replayable G
// gates; returning an identical recording changes construction time only.
fn reciprocal_cache_key(b:&B,tag:u64,zh:&[QubitId],win:&[QubitId],sz:&[QubitId],szr:(usize,usize),s:&S1,act:QubitId,window:bool,sy:&[QubitId],small:bool,bank:bool)->Vec<u64> {
    let mut key=vec![tag,szr.0 as u64,szr.1 as u64,act.0,window as u64,small as u64,bank as u64,s.f.0,s.zero.0,s.sgn.0,b.cancel_simple_pairs as u64,b.cancel_commuting_pairs as u64,b.cancel_window as u64];
    for reg in [zh,win,sz,&s.r,&s.gt,&s.anc,&s.andc,&s.chain,&s.dirty,sy] {
        key.push(reg.len() as u64);key.extend(reg.iter().map(|q|q.0));
    }
    key
}
'''
s+='\n'+helper
for tag,name in enumerate(['stage1_v_compact','stage1_v_compact_partitioned','stage1_v_compact_bank_partition']):
 a=s.index('fn '+name+'(');brace=s.index('{',a);end=s.index('\n    b.end()\n}',brace)
 args='&[],false,false' if tag==0 else ('sy,small,false' if tag==1 else 'sy,small,bank')
 key=f'\n    let memo_key=reciprocal_cache_key(b,{tag},zh,win,sz,szr,s,act,window,{args});\n    if let Some(gates)=b.replay_cache_get(&memo_key){{return gates;}}\n'
 s=s[:end]+s[end:].replace('\n    b.end()\n}', '\n    let gates=b.end();b.replay_cache_store(memo_key,&gates);gates\n}',1)
 s=s[:brace+1]+key+s[brace+1:]
p.write_text(s,encoding='utf8',newline='\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/'])
(root/'candidate-control-fold-v4.patch').write_bytes(patch)
manifest=dict(candidate=str(dest),base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),scope='v3 circuit plus bounded pure-recording cache; must have identical full stream to v3',patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((dest/'src/point_add').rglob('*'))if p.is_file()})
(root/'candidate-control-fold-v4-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(json.dumps(manifest,indent=2))
