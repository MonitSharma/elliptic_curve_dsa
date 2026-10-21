from pathlib import Path
import shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-global-quantum-alias-20261021'
(old/'STATUS.md').write_text('# Pre-test guarded-complement refinement\n\nNo native/full-stream scan ran. Review of the guarded-complement fixture showed that a wire equal to g*(1 XOR product) need not be the global complement of g*product outside g. V2 adds the exact expression flip XOR effective_guard to the complement lookup. This is an additional exact equality case, never an assumed implication. Original source/freeze preserved.\n')
s=(a/'prepare-global-quantum-alias.py').read_text().replace('breakthrough-global-quantum-alias-20261021','breakthrough-global-quantum-alias-v2-20261021');needle='for(value,negative)in[(product,false),(product^1,true),(flip,false),(flip^1,true)]';assert s.count(needle)==1;s=s.replace(needle,'let guarded_complement=alg.xor(&flip,&eff);for(value,negative)in[(product,false),(product^1,true),(flip,false),(flip^1,true),(guarded_complement,true)]')
exec(compile(s,str(a/'prepare-global-quantum-alias.py'),'exec'))
shutil.copyfile(a.parent/'breakthrough-global-quantum-alias-20261021/official-ffe20.ops.bin',a.parent/'breakthrough-global-quantum-alias-v2-20261021/official-ffe20.ops.bin')
