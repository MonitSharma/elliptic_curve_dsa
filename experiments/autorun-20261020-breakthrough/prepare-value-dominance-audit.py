from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-value-abstract-audit-20261020';r=ex/'breakthrough-value-dominance-audit-20261020';r.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
s=(old/'audit.rs').read_text().replace('struct Program{nodes:','struct Program{inputs:Vec<usize>,nodes:').replace('Program{nodes,guards,nq,nb,versions,rng,certified_zero_resets:certified}','Program{inputs:unknown_quantum.to_vec(),nodes,guards,nq,nb,versions,rng,certified_zero_resets:certified}')
start=s.index('fn optimize(');end=s.index('fn eval(',start)
s=s[:start]+'''// Recompute reset dominance on the CURRENT value-equivalent IR after dead-write/cancellation removal.
fn normalize_resets(p:&mut Program)->usize{let mut zero=vec![true;p.nq];for &q in &p.inputs{zero[q]=false;}let mut meet=vec![Vec::<u32>::new();p.nq];let mut changed=0;
 for n in &mut p.nodes{if n.k>=CINV{continue;}let t=n.t as usize;if n.k==QZERO{if n.g==0||zero[t]||subset(&p.guards[n.g as usize],&meet[t]){if n.g!=0{n.g=0;changed+=1;}zero[t]=true;meet[t].clear();}}else{for q in if n.k==QSWAP{vec![t,n.a as usize]}else{vec![t]}{if zero[q]{zero[q]=false;meet[q]=p.guards[n.g as usize].clone();}else{meet[q]=intersect(&meet[q],&p.guards[n.g as usize]);}}}}
 p.certified_zero_resets+=changed;changed}
fn optimize(p:&mut Program,outputs:&[usize])->Vec<(usize,usize,usize)>{let mut rounds=vec![];for round in 0..2048{let d=normalize_resets(p);let l=live(p,outputs);let c=cancel(p);rounds.push((l,c,p.nodes.len()));if round%8==0{eprintln!("VALUE_IR_PROGRESS round={} nodes={} removed={} cancelled={} reset_normalizations={}",round,p.nodes.len(),l,c,d);}if d+l+c==0{break;}}rounds}
''' +s[end:]
pos=s.rfind('\n}')
s=s[:pos]+'''
 #[test]fn matched_writes_expose_a_new_global_zero_reset_without_assuming_nonoutput_inputs_clean(){let n=u64::MAX;let ops=vec![op(K::CCX,0,1,3,n,n),op(K::CCX,0,1,3,n,n),op(K::Hmr,n,n,3,1,0),op(K::CX,n,3,2,n,n)];let p=checked(&ops,&[0,1,2],&[0,1,2]);assert!(p.nodes.iter().any(|n|n.k==QZERO&&n.g==0));let p=checked(&ops,&[0,1,2,3],&[0,1,2]);assert!(p.nodes.iter().any(|n|n.k==QZERO&&n.g!=0));}
''' +s[pos:]
s=s.replace('value-abstract-source-audit-20261020-v1','value-dominance-source-audit-20261020-v1')
(r/'audit.rs').write_text(s)
s=(old/'run.py').read_text().replace('14 passed; 0 failed;','15 passed; 0 failed;').replace("'native_controls':14","'native_controls':15").replace('Fourteen protected native','Fifteen protected native').replace('fixedpoint or128round bound','fixedpoint or2048round bound; normalize resets after every current-IR deadwrite/cancellation round, with original arbitrary quantuminput set retained')
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Verification-only current-IR reset dominance audit

No candidate/nonce/gate edits orscreens. Frozen oldproduct61927788 source and
protecteddependencies unchanged. Build the same exactvalueIR, then after each
deadwrite/involution elimination recompute conditionalreset globalzero proofs
on the CURRENT value-equivalent IR. This may expose zerohelpers after matched
writes disappear. Preserve the ORIGINAL arbitraryquantuminput set, including
nonoutput inputs; never assume only outputregisters are arbitrary. Same safe
necessaryguard intersections; conditionalreset becomesglobal only ifalready
zero or its guard implied byALLpossible remainingwrites. ClassicalHMR random
definitions andoriginal RNGpositions stay separate. Phase deliberately omitted.

15nativecontrols add matchedwrites->globalzero and adversarial arbitrary
nonoutputinput regression. Fixedpoint/2048rounds, progress8rounds. Thenonefixed
verification-only label value-dominance-source-audit-20261020-v1 and8arbitrary
registeredinput fixtures,24protected fullsource comparisons. This isNOTa curve
failure census, nonce screen orquantumresource result. Prior3valuednegative
kept. Anyfuturewrongpointfilter must separately qualifyoriginalFS/tail/curve/
source anduseonlyexact certifiedwrongoutputs; fullphase/dirty/9024benchmark
acceptance remainsmandatory. No IRshortcut is used in production.
''');print(r)
