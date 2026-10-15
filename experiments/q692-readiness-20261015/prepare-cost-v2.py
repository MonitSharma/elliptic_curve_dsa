"""Exact size-clipped predicate folding; preserve thresholds and precision."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(sys.argv[1]);v1=root/'candidate-control-fold-v1';dest=root/'candidate-control-fold-v2'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-hardlinks',str(v1),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root/'candidate-control-fold-v1.patch')],check=True)
p=dest/'src/point_add/midg.rs';s=p.read_text(encoding='utf8')
start='        if small && szr.1 + j >= 257 {'
stop='\n    }\n    b.end()'
for function in ['stage1_v_compact_partitioned','stage1_v_compact_bank_partition']:
 a=s.index(start,s.index('pub(crate) fn '+function));z=s.index(stop,a)
 s=s[:a]+'''        // Preserve the exact runtime size cut. Disjoint SY and size cubes
        // compute the joint predicate in the already-clean SX0 flag.
        let cut=if small && szr.1+j>=257 {Some((sz,257-j))} else {None};
        let predicate=rec(b,|b|{
            let ranges:Vec<Vec<(QubitId,bool)>>=if let Some((v,limit))=cut {
                if limit>=(1usize<<v.len()) {vec![vec![]]} else {
                    (0..v.len()).rev().filter(|&i|limit>>i&1!=0).map(|i|{
                        let mut lits:Vec<_>=((i+1)..v.len()).rev()
                            .map(|h|(v[h],limit>>h&1==0)).collect();
                        lits.push((v[i],true));lits
                    }).collect()
                }
            } else {vec![vec![]]};
            for selector in &selectors {for range in &ranges {
                let mut controls=vec![(act,false),(r[0],false)];
                controls.extend(selector.iter().copied());
                controls.extend(range.iter().copied());
                mc_xor(b,&controls,g0,&[],&s.dirty);
            }}
        });
        b.play(&predicate,false);
        #[cfg(test)]
        if HF_FAULT_SELECTOR.with(|cell|cell.get()==Some(j)){b.x(g0);}
        inc_mixed(b,g0,&bits,&s.anc,&s.dirty);
        #[cfg(test)]
        if HF_FAULT_SELECTOR.with(|cell|cell.get()==Some(j)){b.x(g0);}
        b.play(&predicate,true);'''+s[z:]
p.write_text(s,encoding='utf8',newline='\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/'])
(root/'candidate-control-fold-v2.patch').write_bytes(patch)
manifest=dict(candidate=str(dest),base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),scope='exact joint enable and size-cut cubes; no precision/domain change',patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((dest/'src/point_add').rglob('*'))if p.is_file()})
(root/'candidate-control-fold-v2-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(json.dumps(manifest,indent=2))
