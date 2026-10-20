from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-exact-witness-ripple-20261020';r=ex/'breakthrough-exact-witness-ripple-v2-20261020';r.mkdir(exist_ok=False)
for n in['.gitattributes','.gitignore','witness-tests.rs','sum-tests.rs','run.py','PLAN.md']:shutil.copyfile(old/n,r/n)
s=(old/'prepare.py').read_text();start=s.index("p=t/'src/point_add/square.rs';s=p.read_text();");end=s.index("p=t/'src/point_add/mod.rs';",start);part=s[start:end];part=part.replace("s=p.read_text();","whole=p.read_text();begin=whole.index('fn sub_square_g1m(');finish=whole.index('\\nfn sub_square_body(',begin);s=whole[begin:finish];",1);part=part.replace("s+='\\n'+(r/'sum-tests.rs').read_text();p.write_text(s)","s=whole[:begin]+s+whole[finish:]+'\\n'+(r/'sum-tests.rs').read_text();p.write_text(s)");s=s[:start]+part+s[end:];ast.parse(s);(r/'prepare.py').write_text(s)
with(r/'PLAN.md').open('a')as out:out.write('\nV1 stopped before sourcefreeze/native controls: a textual sharedsum needle also\noccurs in another square path. Preserve original setup/logs/partialsource. V2\nscopes replacement ONLY inside sub_square_g1m; same declared mechanisms/cases,\nno statistical gate/census/nonce rerun and no numericalcut orinput change.\n')
print(r)
