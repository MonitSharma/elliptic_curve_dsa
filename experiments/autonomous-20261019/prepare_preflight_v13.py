from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'preflight_v12.py').read_text()
first=s.index('workers={int(');last=s.index('\nregistered=[];extra_slots=0',first)
replacement='''active_workers=[];active_roots=[]
for search_name in ['parent4-operational-sat-20261019','product-classical-nine-operational-20261019']:
    search_root=ws/search_name;members=[]
    for lane in range(4):
        record=search_root/f'worker{lane}.pid'
        if not record.exists():continue
        p=int(record.read_text())
        if not live(p):continue
        assert Path(f'/proc/{p}/cwd').resolve()==search_root
        expected=search_root/'tool/target/release/value_prefilter'
        assert Path(f'/proc/{p}/exe').resolve()==expected.resolve()
        assert str(expected).encode() in Path(f'/proc/{p}/cmdline').read_bytes().split(b'\\0')
        members.append(p);active_workers.append(p);allowed.update([p,parent(p)])
    record=search_root/'search.pid'
    if record.exists():
        p=int(record.read_text())
        if live(p):
            assert Path(f'/proc/{p}/cwd').resolve()==search_root
            allowed.add(p)
    if members:active_roots.append({'directory':str(search_root),'workers':members,'reserved_slots':15*len(members)})
'''
s=s[:first]+replacement+s[last:]
needle=" ('product-classical-twelve-native-20261019','gate.pid',3),";assert s.count(needle)==1
s=s.replace(needle,needle+"\n ('rail-sx-20261019','run.pid',1),\n ('rail-sx-20261019','branch.pid',1),\n ('rail-sx-prefix-20261019','run.pid',1),\n ('scalar-window-20261019','run.pid',1),")
s=s.replace("'component.pid':b'run-component.sh'","'component.pid':b'run-component.sh','branch.pid':b'run-branch.sh'")
s=s.replace("'active_search_workers':active_workers,","'active_search_workers':active_workers,'active_search_roots':active_roots,")
(r/'preflight_v13.py').write_text(s,newline='\n');compile(s,'preflight_v13.py','exec')
for name in ['run-prepare.sh','run-control.sh']:
    p=r.parent/'product-classical-nine-operational-20261019'/name;s=p.read_text();assert 'preflight_v10.py' in s
    p.write_text(s.replace('preflight_v10.py','preflight_v13.py'),newline='\n')
print('Prepared explicit current/next search registry; only unlaunched wrappers updated')
