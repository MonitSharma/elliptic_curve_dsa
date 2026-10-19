from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'preflight_v14.py').read_text()
needle="processes=subprocess.check_output(['ps'";assert s.count(needle)==1
insert='''# New source-hashed descriptors avoid editing any live profile for each job.
from resource_registry import declared_jobs,observed_job
descriptor_receipts=[]
for path,spec,descriptor_hash in declared_jobs(ws):
    p=observed_job(spec,live,lambda pid:Path(f'/proc/{pid}/cwd').resolve(),lambda pid:[x.decode() for x in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\\0') if x])
    descriptor_receipts.append({'path':str(path),'sha256':descriptor_hash,'active_pid':p,'slots':spec['slots'],'kind':spec['kind']})
    if p is None:continue
    assert not any(row['pid']==p for row in registered),'duplicate static/dynamic reservation'
    members=descendants(p);allowed.update(members)
    if p not in own_ancestors:extra_slots+=spec['slots']
    registered.append({'directory':spec['root'].name,'pidfile':spec['pidfile'].name,'pid':p,'reserved_slots':spec['slots'],'tree':sorted(members),'descriptor_sha256':descriptor_hash})
'''
s=s.replace(needle,insert+needle).replace("'registered_jobs':registered,'unknown_active_research'","'registered_jobs':registered,'dynamic_descriptors':descriptor_receipts,'unknown_active_research'")
p=r/'preflight_v15.py';assert not p.exists();p.write_text(s,newline='\n')
