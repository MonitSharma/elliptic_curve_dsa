from pathlib import Path
import shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-value-cone-audit-20261020';r=a.parent/'breakthrough-value-cone-audit-v2-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','run.py','PLAN.md']:shutil.copyfile(old/n,r/n)
s=(old/'audit.rs').read_text();needle='let mut current:Vec<_>=(0..nb).collect();';assert s.count(needle)==1;s=s.replace(needle,'let mut current:Vec<_>=(0..nb).map(|v|u32::try_from(v).unwrap()).collect();');(r/'audit.rs').write_text(s)
(r/'V2-SCOPE.md').write_text('V1 did not compile: protected analyze_ops returns a u64 classical-bit count, while this tool uses bounded u32 SSA IDs. No native test, full audit, circuit mutation or nonce screen ran. Preserve original compile errors/SOURCE-FREEZE/run.exit1. V2 explicitly checks each initial SSA index converts to u32; all later SSA IDs already use checked conversion. Same four native controls and two frozen input streams, no semantic algorithm change. New tool source freeze before tests.\n');print(r)
