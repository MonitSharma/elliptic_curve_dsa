from pathlib import Path
import shutil,subprocess,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');tip=root.parent/'product-exact-20261015/tip';dest=root/'observer-tip';assert not dest.exists()
rev=subprocess.check_output(['git','-C',str(tip),'rev-parse','HEAD'],text=True).strip();assert rev=='4b2ec52fc55da796aa8f5ef851290297e8706424'
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(dest),rev],check=True)
base=dest/'src/point_add';shutil.copy2(root/'fold_marks.rs',base/'fold_marks.rs')
p=base/'mod.rs';s='mod fold_marks;\n'+p.read_text();needle='        circ.y33_clears();';assert s.count(needle)==1;s=s.replace(needle,'        fold_marks::dump(circ.production_fold_ops());\n'+needle);p.write_text(s)
p=base/'builder.rs';s=p.read_text();needle='    pub(crate) fn y33_clears(&mut self) {';assert s.count(needle)==1;s=s.replace(needle,'    pub(crate) fn production_fold_ops(&self)->&[Op]{&self.ops}\n'+needle);p.write_text(s)
p=base/'y15_onefold.rs';s=p.read_text()
for name,revflag in [('fold_fwd_v2','false'),('fold_rev_v2','true')]:
 start=s.index('fn '+name+'(');end=s.index('\n}',start)+2;part=s[start:end];needle='    let mw = acc.len();';assert part.count(needle)==1
 src='src'if revflag=='true'else'&[]'
 part=part.replace(needle,needle+f'\n    let observe_t=PAYLOAD_AT.with(|x|x.get().map_or(0,|(_,t)|t));\n    let observe_id=super::super::fold_marks::begin(c.op_count(),{revflag},observe_t,acc,e,nm,k1,k2,{src});')
 assert part.endswith('    plan\n}'),(name,part[-120:]);part=part[:-len('    plan\n}')]+ '    super::super::fold_marks::end(observe_id,c.op_count());\n    plan\n}';s=s[:start]+part+s[end:]
p.write_text(s)
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary']);(root/'observer.patch').write_bytes(patch)
manifest={'base_revision':rev,'expected_stream_sha256':'2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e','candidate_changes':False,'pointadd_source_files':{str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in base.rglob('*')if p.is_file()}}
(root/'observer-source.json').write_text(json.dumps(manifest,indent=2)+'\n');print('prepared gate-inert source fold observer')
