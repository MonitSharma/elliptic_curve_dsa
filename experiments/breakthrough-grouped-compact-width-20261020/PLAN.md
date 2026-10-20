# Exact terminal phase expansion at the one-helper width cliff

Before inputs, freeze the same three stronger full259-tail/28-bit witness/exact
split square cases: full control, cap1234 and cap1233, inverseleaf depth8. Only
new behavior in lowcap cases: when the old phase comparison exceeds the cap,
replace penultimate carry by exact GF(2) identity
MAJ(x,y,MAJ(a,b,c))=xy+(x+y)ab+(x+y)(a+b)c. One CZ,two CCZs; one fewer clean
carry, one extra native Toffoli locally. No precision/window/witness/cut changes.
All operands restored and HMR phase repairs retained; dummy HMR on knownzero
carry preserves total random-draw count. y16 admission need_m uses new exact
helper count (minusone for n>=3), not a relaxed old guard. Other guards untouched.

Four new native controls precede27 inherited andgroupplan/square units: full
basis n3..6, arbitrary wider n7/22/56/128/256, independent/aliased source seed,
classicalguards, each measurement basis outcome, all value/phase/helper lanes,
strict one-qubit peak reduction/equaldrawcount; omitted cubicphase fault must
be detected; invalidaccumulator alias rejected. Control disables newroute and
must reproduce fulla871 stream byte-for-byte. Preserve all constructionfails.
Complete source/protected bindings/patch/native logs/raw+generic stream hashes
retained. No new finalgate, nonce or scoredresult. Finite tests are not proof
of complete universal point-addition correctness. Prior six square-domain edge
exclusions retained/disclosed. Nominal caps are not measured widths.
