from pathlib import Path
a=Path(__file__).parent;old=a.parent/'breakthrough-global-quantum-pair-alias-20261021'
(old/'STATUS.md').write_text('# Native guarded-complement precision case failed\n\n17of18native controls passed. The pair fixture with outer guard and a complemented updated carrier was not recognized. No state mismatch or fullstream scan occurred. V2 adds exact pair equalities flip XOR captured_base, flip XOR effective_guard, and base_product XOR captured_base, with an explicit compensating X on the original target guard. All original source/logs retained; no point input/gate/nonce/benchmark.\n')
s=(a/'prepare-global-quantum-pair-alias.py').read_text().replace('breakthrough-global-quantum-pair-alias-20261021','breakthrough-global-quantum-pair-alias-v2-20261021')
needle="'search:for value in[product,flip,base_product]";assert s.count(needle)==1
s=s.replace(needle,"let cb=alg.xor(&flip,&base);let ce=alg.xor(&flip,&eff);let bp=alg.xor(&base_product,&base);'search:for(value,inverted)in[(product,false),(flip,false),(base_product,false),(cb,true),(ce,true),(bp,true)]")
needle='let wanted=other_value^u32::from(negative);';assert s.count(needle)==1;s=s.replace(needle,needle+'let emit_negative=negative^inverted;')
s=s.replace('if negative{out.push(make(K::X','if emit_negative{out.push(make(K::X').replace('if negative{"quantum_pair_complement"}','if emit_negative{"quantum_pair_complement"}')
exec(compile(s,str(a/'prepare-global-quantum-pair-alias.py'),'exec'))
