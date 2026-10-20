from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-public-drop-tradeoffs-20261020';r=a.parent/'breakthrough-public-drop-tradeoffs-v2-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore','additional-tests.rs','phase-compare-compact.rs']:shutil.copyfile(old/n,r/n)
s=(old/'prepare.py').read_text();needle='"cap1233-r9"=>Some((1233,21))';assert s.count(needle)==1;s=s.replace(needle,needle+',"cap1233-r000"=>Some((1233,21)),"cap1233-r001"=>Some((1233,21)),"cap1233-r002"=>Some((1233,21)),"cap1233-r011"=>Some((1233,21)),"cap1233-r012"=>Some((1233,21))')
needle="['public','cap1233-t21','cap1233-rmin','cap1233-r1','cap1233-r2','cap1233-r9']";assert s.count(needle)==1;s=s.replace(needle,"['cap1233-r1','cap1233-r000','cap1233-r001','cap1233-r002','cap1233-r011','cap1233-r012']");ast.parse(s);(r/'prepare.py').write_text(s)
s=(old/'drop-policy-tests.rs').read_text();s=s.replace('"r9"=>[1,2,2],','"r9"=>[1,2,2],"r000"=>[0,0,0],"r001"=>[0,0,1],"r002"=>[0,0,2],"r011"=>[0,1,1],"r012"=>[0,1,2],');s=s.replace('("r9",Some([1,2,2]))','("r9",Some([1,2,2])),("r000",Some([0,0,0])),("r001",Some([0,0,1])),("r002",Some([0,0,2])),("r011",Some([0,1,1])),("r012",Some([0,1,2]))');(r/'drop-policy-tests.rs').write_text(s)
s=(old/'run.py').read_text();needle="   if mode=='public':assert row['stream_sha256']==f['public_exact_sha256'],'Every current publicacd0 output byte must reproduce'";assert s.count(needle)==1;s=s.replace(needle,needle+"\n   if mode=='cap1233-r1':assert row['stream_sha256']=='dd4d7a4ef46e7f3be35e0d6428415d8308dc859a4e196caddedc69a5de22ee8c','Exact priorr1 control must reproduce'")
needle="   assert mode!='public','Exact public control failed; stop rather than bypass binding'";assert s.count(needle)==1;s=s.replace(needle,"   assert mode not in ['public','cap1233-r1'],'Exact control failed; stop rather than bypass binding'");ast.parse(s);(r/'run.py').write_text(s)
(r/'PLAN.md').write_text('''# Extend exact carry-cost grid toward the original reverse policy

V1 public3d7c and originalwidth52a0 controls exact, native9PASS. Complete rmin
1/2/3 reduces17.75proxyT; r1 0/1/3 reduces25.75 at sameQ1233. No new point inputs,
finalgate or nonce. Test exact reverse profiles0/0/0,0/0/1(originalparent policy),
0/0/2,0/1/1,0/1/2 with unchanged forwarddrop3/compactcomparator/parent21bit witness.
All primitive/budget/cap guards remain, failed cases retained. Extend only
already-tested profile selection; every native arithmetic source is unchanged.
Repeat9native controls plus full priorr1/dd4d7a4e bytecontrol before five variants.
Publicflagfalse and prior profiles remain identical by independent truth-table;
no input/nonce/window/round/onefold-range tuning. Select cheapest successful
complete resource profile from the fixed grids before fresh point development,
regenerate exact caches and freeze full bindings. No old cache rows transported.
Any officialsubmission requires ownfinalgate/qualifiedascendingnonce/full9024
benchmark/localreview; static weights are diagnostics, not scored results.
''');print(r)
