"""Reuse a conditionally-one quotient decision to fold the exact size cut."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(sys.argv[1]);v3=root/'candidate-control-fold-v3';dest=root/'candidate-control-fold-v5'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-hardlinks',str(v3),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root/'candidate-control-fold-v3.patch')],check=True)
p=dest/'src/point_add/midg.rs';s=p.read_text(encoding='utf8')
for name in ['stage1_v_compact_partitioned','stage1_v_compact_bank_partition']:
 a=s.index('        if small && szr.1 + j >= 257 {',s.index('fn '+name+'('));z=s.index('\n    }\n    b.end()',a)
 replacement='''        // The retained predicate implies r0=1. Temporarily XORing the
        // exact size comparison into r0 therefore makes r0=!too_large on
        // selected shots. Off the predicate it remains an arbitrary control
        // whose value is ignored and restored. No extra clean wire is used.
        let predicate=rec(b,|b|for selector in &selectors{
            let mut controls=vec![(act,false),(r[0],false)];
            controls.extend(selector.iter().copied());
            mc_xor(b,&controls,g0,&[],&s.dirty);
        });
        b.play(&predicate,false);
        #[cfg(test)]
        if HF_FAULT_SELECTOR.with(|cell|cell.get()==Some(j)){b.x(g0);}
        if small && szr.1+j>=257 {
            let size_test=rec(b,|b|super::frogdrop_col::ge_const_compact(
                b,sz,257-j as isize,r[0],&s.chain,&s.dirty));
            b.play(&size_test,false);
            inc_with_controls(b,&bits,&[(g0,false),(r[0],false)],&s.dirty);
            b.play(&size_test,true);
        } else {
            inc_mixed(b,g0,&bits,&s.anc,&s.dirty);
        }
        #[cfg(test)]
        if HF_FAULT_SELECTOR.with(|cell|cell.get()==Some(j)){b.x(g0);}
        b.play(&predicate,true);'''
 s=s[:a]+replacement+s[z:]
p.write_text(s,encoding='utf8',newline='\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/'])
(root/'candidate-control-fold-v5.patch').write_bytes(patch)
manifest=dict(candidate=str(dest),base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),scope='joint selector predicate, exact conditional-one size borrow and linear controlled increment; no precision/domain change',patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((dest/'src/point_add').rglob('*'))if p.is_file()})
(root/'candidate-control-fold-v5-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(json.dumps(manifest,indent=2))
