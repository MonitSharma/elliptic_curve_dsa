from pathlib import Path
import subprocess,shutil,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-family-20261016');base=root.parent/'precision-repair-20261016/observer-tip';dest=root/'isolated-observer'
family=json.loads((root/'FAMILY-A.json').read_text());(root/'isolated').mkdir(exist_ok=True)
subprocess.run(['git','-C',str(base),'worktree','add','--detach',str(dest),family['source_revision']],check=True);shutil.copytree(base/'src/point_add',dest/'src/point_add',dirs_exist_ok=True)
p=dest/'src/point_add/fold_marks.rs';s=p.read_text();s=s.replace('precision-repair-20261016"','precision-family-20261016/isolated"');assert s.count('ops.len());}')==1;s=s.replace('ops.len());}','ops.len());eprintln!("ISOLATED_COMPONENT_ONLY; unchanged parent raw stream; no score");std::process::exit(0);}')
p.write_text(s)
p=dest/'src/point_add/record.rs';s=p.read_text();assert s.count('#[derive(Default)]')==3;s=s.replace('#[derive(Default)]','#[derive(Default, Clone)]')
for name in['Best','Row']:s=s.replace('struct '+name+' {','#[derive(Clone)]\nstruct '+name+' {')
p.write_text(s)
p=dest/'src/point_add/builder.rs';s=p.read_text();s=s.replace('pub struct Builder {','#[derive(Clone)]\npub struct Builder {');s=s.replace('#[derive(Default)]\npub struct PhaseReport','#[derive(Default, Clone)]\npub struct PhaseReport')
needle='    pub(crate) fn production_fold_ops(&self)->&[Op]{&self.ops}';assert s.count(needle)==1
s=s.replace(needle,needle+'''\n    pub(crate) fn precision_probe_active_ids(&self)->Vec<u64>{(0..self.next_qubit).filter(|q|!self.free_qubits.contains(q)).map(u64::from).collect()}
''');p.write_text(s)
p=dest/'src/point_add/y15_onefold.rs';s=p.read_text();s=s.replace('struct ESh {','#[derive(Clone,Debug)]\nstruct ESh {')
needle='''        fold_fwd_v2(c, &tg[..fold_window(t, false)], [x256, x257, x258], s, k1, k2, fin, esh.as_mut(), ttm, drop_n)''';assert s.count(needle)==1
ticks=','.join(map(str,family['eligible_structural_ticks']))
replacement='''        if ['''+ticks+'''].contains(&t) {
            let before=c.clone();
            let old_esh=esh.clone();
            let at=c.op_count();
            let active=before.precision_probe_active_ids();
            let old_plan=fold_fwd_v2(c, &tg[..fold_window(t,false)], [x256,x257,x258],s,k1,k2,fin,esh.as_mut(),ttm,drop_n);
            let end=c.op_count();
            let directory="/home/hclau/ecdsa_research/precision-family-20261016/isolated";
            let mut same=before.clone();let mut same_esh=old_esh.clone();
            let _=fold_fwd_v2(&mut same,&tg[..fold_window(t,false)],[x256,x257,x258],s,k1,k2,fin,same_esh.as_mut(),ttm,drop_n);
            assert_eq!(&c.production_fold_ops()[at..end],&same.production_fold_ops()[at..],"isolated original clone changes gates at tick{t}");
            crate::write_ops(&c.production_fold_ops()[at..end],std::path::Path::new(&format!("{directory}/tick-{t}.old.bin"))).unwrap();
            std::fs::write(format!("{directory}/tick-{t}.interface.json"),format!("{{\\"tick\\":{t},\\"raw_begin\\":{at},\\"raw_end\\":{end},\\"fin\\":{fin},\\"drop\\":{drop_n},\\"acc\\":{:?},\\"e\\":{:?},\\"nm\\":{:?},\\"shift\\":[{},{}],\\"active_entry\\":{:?}}}\\n",tg.iter().map(|q|q.0).collect::<Vec<_>>(),[x256.0,x257.0,x258.0],s.map(|q|q.0),k1.0,k2.0,active)).unwrap();
            let mut larger=before;let mut larger_esh=old_esh;
            let generated=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||fold_fwd_v2(&mut larger,&tg[..fold_window(t,false)+1],[x256,x257,x258],s,k1,k2,fin,larger_esh.as_mut(),ttm,drop_n)));
            LOAN_ACTIVE.with(|x|x.set(false));
            if generated.is_ok(){
                crate::write_ops(&larger.production_fold_ops()[at..],std::path::Path::new(&format!("{directory}/tick-{t}.new.bin"))).unwrap();
                std::fs::write(format!("{directory}/tick-{t}.esh.txt"),format!("OLD={esh:?}\\nNEW={larger_esh:?}\\n")).unwrap();
                eprintln!("ISOLATED_WIDTH_SUCCESS tick={t} old={} new={} old_clone_equal=true",end-at,larger.op_count()-at);
            }else{std::fs::write(format!("{directory}/tick-{t}.rejected"),"source allocator/capacity assertion; unchanged; no wider block emitted\\n").unwrap();eprintln!("ISOLATED_WIDTH_REJECT tick={t} old_clone_equal=true");}
            old_plan
        }else{fold_fwd_v2(c,&tg[..fold_window(t,false)],[x256,x257,x258],s,k1,k2,fin,esh.as_mut(),ttm,drop_n)}'''
s=s.replace(needle,replacement);p.write_text(s)
(root/'isolated-source.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'isolated-source.json').write_text(json.dumps(dict(base=family['source_revision'],component_only=True,parent_gates_expected_unchanged=True,private_builder_cloning=True,files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
