import hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;a=ws/'wide95-703-review-20261018-085419/candidate/src/point_add';b=ws/'breakthrough-wide-loan-policy-20261020/observer/src/point_add';reports=[]
for name in ['mod.rs','leapfrog.rs','pingpong.rs','y15_onefold.rs']:
 paths=[a/name,b/name];texts=[p.read_text().replace('\r','')for p in paths]
 def constants(s):
  result={}
  for m in re.finditer(r'\bconst\s+([A-Za-z_0-9]+)\s*:[^;=]+?=\s*(.*?);',s,re.S):
   value=' '.join(m[2].split());result[m[1]]=value if len(value)<350 else 'sha256:'+hashlib.sha256(value.encode()).hexdigest()
  return result
 ca,cb=map(constants,texts);changes={n:{'public_toffoli_parent':ca.get(n),'raw1264_lineage':cb.get(n)}for n in sorted(set(ca)|set(cb))if ca.get(n)!=cb.get(n)}
 def literals(s):
  result={m[1]:m[2]for m in re.finditer(r'(?:std::env::set_var|env::set_var)\(\s*"([A-Z0-9_]+)"\s*,\s*"([^"\n]*)"\s*\)',s)}
  for m in re.finditer(r'\(\s*"([A-Z0-9_]+)"\s*,\s*"([^"\n]*)"\s*\)',s):result['tuple:'+m[1]]=m[2]
  return result
 ea,eb=map(literals,texts);env={n:{'public_toffoli_parent':ea.get(n),'raw1264_lineage':eb.get(n)}for n in sorted(set(ea)|set(eb))if ea.get(n)!=eb.get(n)}
 reports.append({'file':name,'source_sha256':[hashlib.sha256(p.read_bytes()).hexdigest()for p in paths],'constant_differences':changes,'textual_literal_env_differences':env})
result={'scope':'Textual source comparison, not an executed recipe trace or proof. No candidate changes or gate verdict. Omitted/inactive constants do not establish arithmetic differences.','files':reports};(r/'PROFILE-COMPARISON.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
