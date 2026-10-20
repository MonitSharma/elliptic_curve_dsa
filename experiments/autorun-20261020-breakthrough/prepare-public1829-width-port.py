"""A new source-bound resource grid; old gates and cache rows are not reused."""
from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-public-drop-tradeoffs-v2-20261020';r=ex/'breakthrough-public1829-width-port-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','additional-tests.rs','phase-compare-compact.rs','drop-policy-tests.rs']:shutil.copyfile(old/n,r/n)
s=(old/'prepare.py').read_text().replace('7499c902d7989e5a995ccd2331104a532197851b','3eefcf216ca37cba0ae3f56212d6b1302844a249').replace('breakthrough-public-acd0-reproduction-20261020','breakthrough-public1829-reproduction-20261020').replace("parent_result['T']==756265","parent_result['T']==755314").replace("prior=ws/'public-product-54fc-20261020/parent/target'","prior=parent/'parent/target'")
s=s.replace("'modes':['cap1233-r1','cap1233-r000','cap1233-r001','cap1233-r002','cap1233-r011','cap1233-r012']","'modes':['public','cap1234-t21','cap1233-r012']")
needle="assert all(sha(t/p)==h for p,h in protected.items());prior="
assert s.count(needle)==1
overlay='''# Public static tables bind the old complete stream. Never apply or weaken those
# bindings on a changed constructor: preserve them verbatim in public control,
# explicitly omit all three source-bound tables in uncached research variants.
p=t/'src/point_add/stream_edits.rs';raw=p.read_bytes();needle=b'pub(super) fn run(mut v:Vec<Op>)->Vec<Op>{';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\\nif std::env::var("STACK_WIDTH_RESEARCH").is_ok_and(|s|s!="public"){std::env::set_var("SL_COND","ur");v=super::cond_pass::run(v);v=super::zero_force::run(v);v=super::classical_factors_xor::simplify_classical(v);return super::classical_wide::simplify_classical(v);}')
p.write_bytes(raw)
'''
s=s.replace(needle,overlay+needle)
s=s.replace('Exact entire currentpublicacd0 control unchanged;','Exact entire public1829 control unchanged; changed constructors OMIT old source-bound row/cache/product/value tables and retain generic passes. New cache proofs required before final source;').replace('no frozen_stack inpublicacd0','no frozen_stack inpublic1829')
ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'run.py').read_text();s=s.replace("   if mode=='cap1233-r1':assert row['stream_sha256']=='dd4d7a4ef46e7f3be35e0d6428415d8308dc859a4e196caddedc69a5de22ee8c','Exact priorr1 control must reproduce'",'')
s=s.replace("mode not in ['public','cap1233-r1']","mode!='public'").replace('CURRENT_PUBLIC_ACD0_EXACT_COMPONENT_COMPLETE_WIDTH_GRID_NOT_SCORED','PUBLIC1829_EXACT_WORKSPACE_PORT_RESOURCE_GRID_NOT_SCORED').replace('Every current publicacd0 output byte must reproduce','Every public1829 output byte must reproduce')
ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Exact workspace port on the new public product parent

Parent public1829986e/source3eefcf21, unchanged benchmark already reproduced.
Three fixed complete resource cases before fresh point inputs: exact public
byte control; cap1234 with compact comparator/loan128 and unchanged witness21;
cap1233 with the native tested exact forward drop3/reverse profile[0,1,2] and
seven-wire carry plan. All arithmetic range/capacity checks remain. No new
square/walk cutoff imported or lowered: public parent's approximations remain.
Same nine native comparator/plan/policy controls before whole-stream generation.

PUBLIC mode must reproduce every published stream byte. Variant constructors
cannot use parent's source-bound rewrite tables: OMIT row/AND-cache/product-copy/
value edits completely in explicit uncached research branches; keep all generic
condition/zero/classical simplifiers. No hash checks disabled or repointed.
Only src/point_add changes, 17 protected files checked, all original table bytes
preserved. This may lose old resource savings; that is measured and disclosed.
Any later cache needs fresh proofs and full prefix/source bindings. The finished
candidate needs fresh development, its OWN final statistical gate against exact
public1829, source-qualified ascending nonce selection, unchanged9024 benchmark
and automatic official verification. Old Q1233/acd0 verdict stays final and is
never reused. Static stream counts are diagnostics only, not scored results.
''')
print(r.name)
