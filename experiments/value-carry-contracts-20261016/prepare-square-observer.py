from pathlib import Path
import shutil,subprocess,hashlib,json
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016');tip=r.parent/'product-exact-20261015/tip';d=r/'square-observer';e=r/'square-component';e.mkdir(exist_ok=True)
assert not d.exists();rev=subprocess.check_output(['git','-C',str(tip),'rev-parse','HEAD'],text=True).strip();assert rev=='4b2ec52fc55da796aa8f5ef851290297e8706424'
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(d),rev],check=True)
b=d/'src/point_add';shutil.copytree(r/'observer/src/point_add',b,dirs_exist_ok=True)
p=b/'fold_marks.rs';s=p.read_text().replace('value-carry-contracts-20261016"','value-carry-contracts-20261016/square-component"');p.write_text(s)
p=b/'mod.rs';s=p.read_text();needle='        fold_marks::dump(circ.production_fold_ops());';assert s.count(needle)==1
s=s.replace(needle,needle+'\n        eprintln!("RESEARCH_COMPONENT_ONLY_RAW; unchanged source emission, no table bypass candidate, no scoring");\n        std::process::exit(0);');p.write_text(s)
p=b/'square.rs';s=p.read_text();start=s.index('fn wcin_windows(');end=s.index('\n}',start)+2;part=s[start:end]
needle='        let win = &out[shift..top];';assert part.count(needle)==1
part=part.replace(needle,needle+'\n        let observe_begin=circ.op_count();')
needle='        if inv { circ.x_all(win); }';assert part.count(needle)==2
at=part.rindex(needle)+len(needle)
part=part[:at]+'''
        let ids=|v:&[QubitId]|v.iter().map(|q|q.0).collect::<Vec<_>>();
        eprintln!("VALUE_SQUARE_WINDOW {{\\"begin\\":{observe_begin},\\"end\\":{},\\"high_width\\":{},\\"shift\\":{shift},\\"top\\":{top},\\"inv\\":{inv},\\"carry_in\\":{},\\"out\\":{:?},\\"high\\":{:?}}}",circ.op_count(),high.len(),c.0,ids(out),ids(high));
'''+part[at:]
s=s[:start]+part+s[end:];p.write_text(s)
(r/'square-observer.patch').write_bytes(subprocess.check_output(['git','-C',str(d),'diff','--binary']))
(r/'square-observer-source.json').write_text(json.dumps(dict(base_revision=rev,component_only=True,expected_raw_sha256='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69',files={str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in b.rglob('*')if p.is_file()}),indent=2)+'\n')
