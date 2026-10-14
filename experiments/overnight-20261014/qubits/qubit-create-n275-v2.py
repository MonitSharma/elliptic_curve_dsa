"""Exclude extension owners from map carry loans; add new width boundaries."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
source,dest,packet,out=map(lambda s:Path(s).resolve(),sys.argv[1:5])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for path in subprocess.check_output(['git','-C',str(source),'diff','--name-only'],text=True).splitlines():
    assert path.startswith('src/point_add/');shutil.copyfile(source/path,dest/path)
p=dest/'src/point_add/frogdrop.rs';t=p.read_text();old='loaned.anc.extend_from_slice(&q[par.m..]);';assert t.count(old)==1;t=t.replace(old,'loaned.anc.extend(q[par.m..].iter().copied().filter(|qid|!ring.contains(qid)));');p.write_text(t)
# The geometric primitive test banners must reflect their actual new cutoff.
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text();a=t.index('#[test]\nfn n275_sz_donor_boundaries');t=t[:a]+t[a:].replace('boundaries=98,99,128','boundaries=96,97,128')
script=Path(__file__).with_name('qubit-add-k32-column-tests.py').read_text()
prefix=script[script.index('def states(dx):'):script.index('\n\nselected={}')] ;ns={'P':2**256-2**32-977};exec(prefix,ns);states=ns['states'];P=ns['P'];selected={}
for line in packet.read_text().splitlines():
    if line.startswith('#'):continue
    w=line.split();idx=int(w[0]);tx,ty,ox,oy,ex,ey=[int(x,16)for x in w[1:7]]
    for division,dx in ((1,(tx-ox)%P),(2,(ex-ox)%P)):
        for ci,state in enumerate(states(dx)):
            labels=[]
            if idx==0 and division==1 and ci==0:labels.append('wide_first_column')
            if state['kind']in('HR','HT')and state['sy_actual']in(96,97):labels.append(f"{state['kind']}_SY{state['sy_actual']}")
            if state['quotient']>=2**22:continue
            for label in labels:
                if label not in selected:selected[label]=dict(label=label,shot=idx,division=division,dx=hex(dx),column=ci,**state)
    if len(selected)==5:break
assert len(selected)==5,selected.keys()
cases=[]
for label,row in sorted(selected.items()):
    a,z=row['before'],row['after'];cases.append('("'+label+'",'+str(row['column'])+',['+','.join('"'+format(v,'x')+'"'for v in a[:3])+'],'+','.join(str(v)for v in a[3:])+',['+','.join('"'+format(v,'x')+'"'for v in z[:3])+'],'+','.join(str(v)for v in z[3:])+')')
a=t.index('#[test]\nfn reserve9_columns_crossing_3713_positive_native');z=t.index('#[test]',a+10);test=t[a:z].replace('reserve9_columns_crossing_3713_positive_native','n275_v2_full_column_new_boundaries_native');a=test.index('let cases=&[')+len('let cases=&[');z=test.index('];let (cols',a);test=test[:a]+','.join(cases)+test[z:];test=test.replace('RESERVE9_COLUMN_CASE_PASS','N275_NEW_BOUNDARY_CASE_PASS').replace('RESERVE9_NATIVE_SUITE_PASS','N275_NEW_BOUNDARY_SUITE_PASS');p.write_text(t+test)
out.write_text(json.dumps(dict(scope='Native fixtures only, independent of benchmark schedule/nonce',packet_sha256=hashlib.sha256(packet.read_bytes()).hexdigest(),cases=list(selected.values())),indent=2)+'\n')
