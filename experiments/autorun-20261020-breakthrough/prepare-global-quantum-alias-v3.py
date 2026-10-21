from pathlib import Path
import shutil
a=Path(__file__).parent;v2=a.parent/'breakthrough-global-quantum-alias-v2-20261021'
(v2/'STATUS.md').write_text('# Native precision control failed; no complete-circuit scan\n\n14 of15native tests passed. The retained-product fixture under an outer captured guard plus another per-operation guard was not recognized by lookup of raw or fully guarded products. This is a missed proof, not a concrete state mismatch. V3 also queries base*product and its complement inside the captured base guard, which are exact equality cases. Original frozen source and failed native logs retained. No point inputs, gate, nonce or benchmark ran.\n')
s=(a/'prepare-global-quantum-alias.py').read_text().replace('breakthrough-global-quantum-alias-20261021','breakthrough-global-quantum-alias-v3-20261021')
needle='for(value,negative)in[(product,false),(product^1,true),(flip,false),(flip^1,true)]';assert s.count(needle)==1
s=s.replace(needle,'let guarded_complement=alg.xor(&flip,&eff);let base_product=alg.and(&base,&product);let base_complement=alg.xor(&base_product,&base);for(value,negative)in[(product,false),(product^1,true),(flip,false),(flip^1,true),(guarded_complement,true),(base_product,false),(base_complement,true)]')
exec(compile(s,str(a/'prepare-global-quantum-alias.py'),'exec'))
shutil.copyfile(a.parent/'breakthrough-global-quantum-alias-20261021/official-ffe20.ops.bin',a.parent/'breakthrough-global-quantum-alias-v3-20261021/official-ffe20.ops.bin')
