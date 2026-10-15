from pathlib import Path
import subprocess,shutil,json,hashlib
root=Path('/home/hclau/ecdsa_research/precision-repair-20261016');dest=root/'candidate-posttable-top1';tip=root.parent/'product-exact-20261015/tip'
proof=json.loads((root/'component-comparison.json').read_text());assert proof['prefix_byte_identical']and proof['suffix_byte_identical']
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(dest),'4b2ec52fc55da796aa8f5ef851290297e8706424'],check=True)
for a,b in [('precision_region.rs','precision_region.rs'),('old-fold-records.bin','precision_fold_old.bin'),('new-fold-records.bin','precision_fold_new.bin')]:shutil.copy2(root/a,dest/'src/point_add'/b)
p=dest/'src/point_add/mod.rs';s='mod precision_region;\n'+p.read_text();needle='    ops = apply_tail_nonce(ops, nonce);';assert s.count(needle)==1;s=s.replace(needle,needle+'\n    ops = precision_region::run(ops);');p.write_text(s)
assert (dest/'src/point_add/square_finish.rs').read_bytes()==(tip/'src/point_add/square_finish.rs').read_bytes()
assert (dest/'src/point_add/y15_onefold.rs').read_bytes()==(tip/'src/point_add/y15_onefold.rs').read_bytes()
(root/'candidate-posttable-top1.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'candidate-posttable-top1-source.json').write_text(json.dumps(dict(base='4b2ec52fc55da796aa8f5ef851290297e8706424',source_changes_only_point_add=True,all_inherited_assertions_and_tables_retained=True,component_comparison_sha256=hashlib.sha256((root/'component-comparison.json').read_bytes()).hexdigest(),files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
