from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-prefix27-width-20261020';r=a.parent/'breakthrough-public-prefix27-width-v2-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','additional-tests.rs','phase-compare-compact.rs','prefix-policy-tests.rs','run.py']:shutil.copyfile(old/n,r/n)
s=(old/'prepare.py').read_text();needle='(rev&&(124..127).contains(&t))';assert s.count(needle)==1;s=s.replace(needle,'(rev&&((if std::env::var("STACK_DROP_EARLY_RESEARCH").is_ok_and(|v|v=="1"){122}else{124})..127).contains(&t))')
s=s.replace("'scope':'Exact entire currentpublicacd0 control unchanged; fixed complete postprocessed width1234/1233/1232 with SAMEparent21bit witness, plus stronger28bit control. No witness/window/round cut lowered. New exactphasecomparator plus independently nativeplan7/originalloan128. Originalallpublicgeneric passes remain and rederivefromnewstream; no frozen_stack inpublicacd0. Own finalgate/nonce/benchmark stillrequired.'","'scope':'V2 exact prefix27/fullfold port with preflight flag bound to runtime; original public3d7c/cap1233 positive52a0 unchanged. Cap<=1232 uses independently tested exactdrop3/plan7 forward127..136 and reverse122..126, preserves original policy elsewhere. Fixed complete grid and strengthened+1/+2 controls, sameparent21bit witness. Fourteen native controls before construction. No pointcensus/finalgate/nonce/score.'")
ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'early-policy-tests.rs').read_text();assert s.count(needle)==1;s=s.replace(needle,'(rev&&((if early{122}else{124})..127).contains(&t))');(r/'early-policy-tests.rs').write_text(s)
(r/'PLAN.md').write_text('''# Exact reverse schedule admission after forward prefix clears

V1 comparator4/plan4/policy1/prefix2/cleanup1/fullfold1/policy1 controls PASS14;
public3d7c and cap1233/52a0 controls exact. Smaller caps clear forward with the
prefix route, then cap1232 stops unchanged reverse123 fold guard: short21,
room17/need38, pool16+tops2+fin2=20. V1 failure final/preserved, no point sampling.
V2 admits ONLY the same independently verified exactdrop3/50bit/7-helper ladder
earlier on reverse122..126 when cap<=1232. Cap1233 keeps prior124..126; forward
and all arithmetic windows/onefold tick ranges/precision remain unchanged.
Update independent policy truth-table for the new bounded selector, preserve
all original primitive and fullfold peak assertions. Repeat14 controls before
same fixed full public/smaller-cap/strengthening grid. No finalgate/nonce/score.
''');print(r)
