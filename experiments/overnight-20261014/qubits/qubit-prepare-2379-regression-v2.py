"""Fixed independent full-benchmark counterexample, external diagnostic only."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
source,dest,ev=map(lambda s:Path(s).resolve(),sys.argv[1:4])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():
    assert name.startswith('src/point_add/');shutil.copyfile(source/name,dest/name)
script=(source.parent/'qubit-add-k32-column-tests.py').read_text();prefix=script[script.index('def states(dx):'):script.index('\n\nselected={}')];ns={'P':2**256-2**32-977};exec(prefix,ns)
dx=int('b99d62d1aa557c0a85f9ea89739eded4eb025ed76459a15b2551efaae60665bd',16)
state=ns['states'](dx)[86];assert state['kind']=='HT' and state['j']==86 and state['quotient']==22815568,state
a,z=state['before'],state['after'];case='("shot2379_div2_HT_q25",86,['+','.join('"'+format(v,'x')+'"'for v in a[:3])+'],'+','.join(str(v)for v in a[3:])+',['+','.join('"'+format(v,'x')+'"'for v in z[:3])+'],'+','.join(str(v)for v in z[3:])+')'
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text();match=re.search(r'#\[test\]\nfn n27[45]_v2_full_column_new_boundaries_native',t);assert match
start=match.start();end=t.find('#[test]',start+10);end=len(t)if end<0 else end;test=t[start:end];test=re.sub(r'fn n27[45]_v2_full_column_new_boundaries_native','fn qubit_diag2379_full_column_negative_control',test)
begin=test.index('let cases=&[')+len('let cases=&[');end=test.index('];let (cols',begin);test=test[:begin]+case+test[end:]
old='assert_eq!(got.q,expected,"case {label} col{ci} exact Euclid shadow plus all scratch/passengers");assert_eq!(got.phase,0,"case {label}");';assert old in test
test=test.replace(old,'let bad:Vec<_>=got.q.iter().zip(&expected).enumerate().filter_map(|(i,(x,y))|if x!=y{Some(i)}else{None}).collect();eprintln!("FIXED2379_NEGATIVE forward_bad={bad:?} phase={:x} q={:x} sy={:x} sx={:x}",got.phase,get(&got.q,&q,0),get(&got.q,&sy,0),get(&got.q,&sx,0));assert!(!bad.is_empty(),"Known quotient overflow must be reproduced by this unchanged source");')
test=re.sub(r'assert_eq!\(back.q,input,"case \{label\} inverse"\);assert_eq!\(back.phase,0\);', 'eprintln!("FIXED2379_NEGATIVE inverse_all_wires_restore={} inverse_phase={:x}",back.q==input,back.phase);',test)
test=test.replace('N275_NEW_BOUNDARY_CASE_PASS','FIXED2379_NEGATIVE_CONTROL_COMPLETE').replace('N275_NEW_BOUNDARY_SUITE_PASS','FIXED2379_DIAGNOSTIC_COMPLETE')
p.write_text(t+'\n'+test)
manifest=dict(scope='Known expected-negative external native diagnosis; exit0 means reproduced failure, not candidate pass',source_variant=source.name,source_patch_sha256=hashlib.sha256(subprocess.check_output(['git','-C',str(source),'diff','HEAD','--','src/point_add/'])).hexdigest(),input_dx=hex(dx),shot=2379,division=2,column=86,state=state,source_constructor_width=int(re.search(r'pub const N:\s*usize\s*=\s*(\d+)\s*;', (dest/'src/point_add/pointadd_frogdrop.rs').read_text())[1])+417,diagnostic_source_sha256={name:hashlib.sha256((dest/name).read_bytes()).hexdigest()for name in subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--name-only'],text=True).splitlines()})
(ev/f'{dest.name}-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
