from pathlib import Path
import ast
a=Path(__file__).parent;r=a.parent/'breakthrough-public-expanded-cap-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('observer/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
s='''import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';parent=ws/'breakthrough-public-acd0-reproduction-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();sf=json.loads((parent/'SOURCE-FREEZE.json').read_text());assert(parent/'run.exit').read_text().strip()=='0';assert all(sha(parent/'parent'/p)==h for p,h in {**sf['source_files'],**sf['protected_files']}.items());assert not t.exists();subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),sf['base']],check=True)
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'pub fn build() -> Vec<Op> {';assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'\\n    let mode=std::env::var("PUBLIC_EXPANDED_CAP").expect("Declared fixed public cap grid");let cap=match mode.as_str(){"public"=>None,"cap1235"=>Some(1235),"cap1236"=>Some(1236),"cap1237"=>Some(1237),"cap1238"=>Some(1238),"cap1240"=>Some(1240),"cap1244"=>Some(1244),"cap1248"=>Some(1248),_=>panic!("Undeclared cap")};');needle=b'    let mut ops = build_point_add();';assert raw.count(needle)==1;raw=raw.replace(needle,b'    if let Some(cap)=cap{for name in["HEO_PIN_PP_WALK_MAX_QUBITS","PEBBLE_HARD_CAP","LF_SQUARE_CAP"]{std::env::set_var(name,cap.to_string());}std::env::set_var("SQC_T","21");std::env::set_var("TAIL_NONCE","0");}\\n'+needle);p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in sf['protected_files'].items());assert all(sha(t/p)==h for p,h in sf['source_files'].items()if p!='src/point_add/mod.rs');subprocess.run(['cp','-a','--reflink=auto',str(parent/'parent/target'),str(t/'target')],check=True);subprocess.run(['git','-C',str(t),'add','--intent-to-add','src/point_add'],check=True);(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD','--','src/point_add']));freeze={'base':sf['base'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'protected_files':sf['protected_files'],'modes':['public','cap1235','cap1236','cap1237','cap1238','cap1240','cap1244','cap1248'],'public_exact_sha256':'3d7c94f1dea887dd2d4ff13326e350756350cc1044d396444c3f820f8bfad827','scope':'Fixed larger resource-cap grid on exact publicacd0 source. Only mod build-cap selection differs; all native arithmetic files byteidentical. Same21bit witness, public comparison recipe/windows/rounds, complete generic postpasses. Different global caps may derive different replay chunks, so full equivalence and failuregate not presumed. No point-input sampling/gate/nonce/score.'};(r/'SOURCE-FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\\n')
'''
ast.parse(s);(r/'prepare.py').write_text(s)
s=(a.parent/'breakthrough-public-acd0-exact-width-20261020/run.py').read_text();start=s.index(";assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test'");end=s.index(";assert run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build'",start);s=s[:start]+s[end:];s=s.replace('STACK_WIDTH_RESEARCH=mode','PUBLIC_EXPANDED_CAP=mode').replace('CURRENT_PUBLIC_ACD0_EXACT_COMPONENT_COMPLETE_WIDTH_GRID_NOT_SCORED','FIXED_PUBLIC_EXPANDED_CAP_GRID_COMPLETE_NOT_SCORED');ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Fixed larger-cap product tradeoff grid on the exact current public source

Publicacd0/7499, then cap1235/1236/1237/1238/1240/1244/1248. Only buildresource
selection in mod.rs changes; every native arithmetic source file remains byte
identical. Same parent21bit witness, window/round/comparison recipe and generic
passes. Resource caps can change derived replay chunks; no claim full point-add
equivalence without fresh development/finalgate. Public control must reproduce
every3d7c94f1 byte before fixed grid runs. Read actual protectedQ, not requested
cap; static counts are diagnostics only. No packet inputs, nonce or benchmark
selection here. A promising resource candidate needs frozen finished source,
fresh full-output development/sole finalgate against exact currentpublicparent,
qualifiedascendingnonce/unchanged9024benchmark/localreview beforeautoupload.
''');print(r)
