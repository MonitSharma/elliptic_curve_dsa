"""Fresh v4 eliminates HR source/predicate aliases via plain carry-tail."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
source,dest,ev=map(lambda s:Path(s).resolve(),sys.argv[1:4])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():
    assert name.startswith('src/point_add/');shutil.copyfile(source/name,dest/name)
p=dest/'src/point_add/midg.rs';t=p.read_text();old='super::payload::trans_one(b,&t,&src[..sl],kk,false,vec![(ak,false)],None,sx[0],c0,&[],&pl.dirty);';assert old in t
t=t.replace(old,'super::payload::trans_one(b,&t,&q[..128.min(t.len())],kk,false,vec![(ak,false)],None,sx[0],c0,&[],&pl.dirty);')
for flag in ['false','true']:
    old=f'if let Some(norm) = &pad_sy7_zero {{ b.play(norm, {flag}); }}';assert old in t
    t=t.replace(old,f'if !precision25 {{ if let Some(norm) = &pad_sy7_zero {{ b.play(norm, {flag}); }} }}')
p.write_text(t)
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text();a=t.index('#[test]\nfn reserve9_columns_crossing_3713_positive_native');t=t[:a]+t[a:].replace('width=692','width=691').replace('Q21_SX6','Q21_Q118').replace('q21_owner=SX6','q21_owner=Q118')
a=t.index('#[test]\nfn n274_q21_counterexample1170_payload_native');z=t.index('#[test]',a+10);test=t[a:z]
test=test.replace('n274_q21_counterexample1170_payload_native','n274_hr_sy128_payload_full_predicate_native').replace('e1a14a46e6340fd02bde43002b9b85d32649195df078b8aa7efe88ce0964f802','223e2329d783f184c1814f967becd38aa587d6dd5f977fa511908c9f6a5e6950').replace('let j=36','let j=68').replace('N::from(2216631u64)','N::from(1u64)').replace('cols[35]','cols[67]')
old='assert!(cp.hr&&!cp.ht&&!cp.sw&&!cp.dn&&!cp.dl&&!cp.dq&&!cp.psw&&!cp.tt&&cp.sz.1<=255&&cp.sy.1+23>=128);';assert old in test
test=test.replace(old,'assert!(cp.hr&&t[j].bit_len()==128);').replace('assert!(max_digit>=N::from(1u64)<<21);','assert!(max_digit>=N::from(1u64));').replace('Q21_Q118','HR_SY128').replace('1170 exact','HR SY128 exact').replace('column=35 euclid_step=36 quotient=2216631','column=67 euclid_step=68 quotient=1').replace('q21_owner=Q118','full_SY8_predicate=true source_length=128').replace('117000','128000')
p.write_text(t+'\n'+test)
changed=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--name-only'],text=True).splitlines();assert len(changed)==6
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/']);(ev/'candidate-n274-v4.patch').write_bytes(patch)
manifest=dict(scope='N274-v4 Q118 q21; HR short/full128 sources exclude predicate/zero-pad aliases, originalHR SY128 fixture; components pending',base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),checkout=str(dest),candidate_changed_paths=changed,protected_files_modified=False,patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p:hashlib.sha256((dest/p).read_bytes()).hexdigest()for p in changed})
(ev/'candidate-n274-v4-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
