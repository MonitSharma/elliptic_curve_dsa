"""Materialize a raw observer aligned by full random-read ordinal, both directions."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'joint-carry-20261015/prepare.py').read_text().replace("dynamic-pool-20261015/wide-b3","y15-unseeded-20261015/wide-b3")
s=s.replace("p=base/'y15_onefold.rs';s=p.read_text()","p=base/'y15_onefold.rs';full=p.read_text();a=full.index('fn body(');z=full.index('fn body_capped(',a);s=full[a:z]")
s=s.replace("s=s[:start]+part+s[end:];p.write_text(s)","s=s[:start]+part+s[end:];p.write_text(full[:a]+s+full[z:])")
s=s.replace('if !rev && top1 {','if top1 {').replace('if !rev {','{').replace('mark(c.op_count(),t,','mark(c.op_count(),t+usize::from(rev)*1000,')
(root/'prepare-state.py').write_text(s)
s=(root.parent/'joint-carry-20261015/joint_trace.rs').read_text()
a=s.index('let selected:Vec<_>');b=s.index('assert_eq!(selected.len(),1)',a)
s=s[:a]+'''let target_at=ops.iter().enumerate().filter(|(_,op)|matches!(op.kind,OperationType::Hmr|OperationType::R)).nth(780824).unwrap().0;
 let selected:Vec<_>=all.iter().filter(|m|m.label=="hmr"&&m.at==target_at&&m.flags[0].0==135&&m.bit==1555).collect();'''+s[b:]
(root/'joint_trace.rs').write_text(s)
s=(root.parent/'joint-carry-20261015/run.sh').read_text().replace('/joint-carry-20261015','/y15-carry-source-20261015').replace('"$root/prepare.py"','"$root/prepare-state.py"')
(root/'run-state.sh').write_text(s,newline='\n')
