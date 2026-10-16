from pathlib import Path
import json,tarfile,re,ast,collections,hashlib
r=Path(__file__).parent;old=r.parent/'free-borrow-family-20261016';archive=old/'evidence.tar.gz';t=tarfile.open(archive);sources={}
for p in t.getnames():
 if p.startswith('observer/src/point_add/')and p.endswith('.rs'):sources[Path(p).name]=t.extractfile(p).read().decode().splitlines()
def function(file,line):
 rows=sources[file]
 for j in range(min(line,len(rows))-1,-1,-1):
  m=re.search(r'\bfn\s+([a-zA-Z_]\w*)\s*[(<]',rows[j])
  if m:return m.group(1)
 return 'unknown_function'
def opt(s):return None if s=='None'else int(s[5:-1])
callers=collections.defaultdict(list);frames={};hmr={};interfaces=[]
for raw in t.extractfile('source-map.log'):
 line=raw.decode(errors='replace').rstrip('\n');f=line.split('\t')
 if f[0]=='C35_SITE':
  source,line=f[1].rsplit(':',1);file=Path(source).name;row=dict(source_file=file,source_line=int(line),source_function=function(file,int(line)),source_width=int(f[2]),seeded=bool(int(f[3])),raw_at=int(f[4]));callers[row['raw_at']].append(row)
 elif f[0]=='PHASE_CMP':interfaces.append(dict(raw_at=int(f[1]),u=ast.literal_eval(f[2]),v=ast.literal_eval(f[3]),borrow=opt(f[4]),context=ast.literal_eval(f[5].replace('true','True').replace('false','False'))))
 elif f[0]=='PHASE_HMR':hmr[int(f[1])]=dict(q=int(f[2]),bit=int(f[3]),source_file=Path(f[4]).name,source_line=int(f[5]))
 elif f[0]=='FREE_BORROW_CHUNK':
  at,round,mul,lo=map(int,f[1:5]);frames[at+2]=dict(kind='ordinary_chunk',raw_hmr=at,round=round,multiply=bool(mul),lo=lo,a=ast.literal_eval(f[5]),b=ast.literal_eval(f[6]),borrow=opt(f[7]))
 elif f[0]=='FREE_BORROW_TOP1':frames[int(f[1])]=dict(kind='TOP1',lo=int(f[2]),a=ast.literal_eval(f[3]),b=ast.literal_eval(f[4]),borrow=opt(f[5]))
rows=[]
for m in interfaces:
 cs=callers.get(m['raw_at'],[]);assert cs,('missing caller',m['raw_at']);caller=next((c for c in cs if c['source_width']==len(m['u'])),cs[-1]);row=dict(**m,**{k:v for k,v in caller.items()if k!='raw_at'});frame=frames.get(m['raw_at']);row['full_operand_frame']=frame;row['effective_width']=len(m['u']);row['immediate_source_hmr']=hmr.get(m['raw_at']-2)
 file=caller['source_file'];row['family']=('ordinary_chunk'if caller['source_function']=='chunked_add'else'TOP1'if file=='y15_onefold.rs'else'joint_lowfold'if file=='joint_lowfold.rs'else file[:-3]+'::'+caller['source_function']);rows.append(row)
out=dict(raw_stream_sha256='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69',source_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),caller_records=sum(map(len,callers.values())),interface_records=len(rows),family_counts=dict(collections.Counter(x['family']for x in rows)),all_source_calls_included=True,no_witness_selection=True,rows=rows)
(r/'source-inventory.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='rows'},indent=2))
