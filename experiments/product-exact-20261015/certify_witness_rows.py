import hashlib,json,struct,subprocess,sys
from pathlib import Path
left,right,log=map(Path,sys.argv[1:]);sentinel=(1<<64)-1
changes={}
for line in log.read_text().splitlines():
    if line.startswith('I25_WITNESS_ROW '):
        fields=dict(x.split('=',1) for x in line.split()[1:]);at=int(fields['at']);assert at not in changes;changes[at]=int(fields['control'])
def open_records(path):
    source=path.open('rb',buffering=0);magic,count=struct.unpack('<8sQ',source.read(16));assert magic==b'QECCOPSZ'
    proc=subprocess.Popen(['zstd','-dcq'],stdin=source,stdout=subprocess.PIPE)
    return source,proc,count
ls,lp,ln=open_records(left);rs,rp,rn=open_records(right);assert ln==rn
index=0;seen=0
while index<ln:
    count=min(100000,ln-index);a=lp.stdout.read(count*56);b=rp.stdout.read(count*56);assert len(a)==len(b)==count*56
    for j in range(count):
        i=index+j;aa=a[j*56:(j+1)*56];bb=b[j*56:(j+1)*56]
        if i not in changes:assert aa==bb,('unreported modification',i)
        else:
            old=struct.unpack('<7Q',aa);control=changes[i]
            assert old[0]==13 and control!=old[3]
            expected=(8,sentinel,control,old[3],sentinel,old[5],sentinel)
            assert struct.unpack('<7Q',bb)==expected,('bad reported CX replacement',i)
            seen+=1
    index+=count
assert not lp.stdout.read(1) and not rp.stdout.read(1) and lp.wait()==rp.wait()==0
ls.close();rs.close();assert seen==len(changes)
print(json.dumps({'left':str(left),'right':str(right),'operations':ln,'exact_reported_ccx_to_cx_rows':seen,'all_other_records_byte_identical':True,'original_measurements_and_identity_tail_unchanged':True,'right_stream_sha256':hashlib.sha256(right.read_bytes()).hexdigest(),'scope':'Complete syntactic row certificate. Immutable ANF witness proof and native tests establish the algebra; anchored full-state/phase replay is separately required.'}),flush=True)
