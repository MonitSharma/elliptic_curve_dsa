from pathlib import Path
import subprocess,json,hashlib,struct
r=Path(__file__).resolve().parents[1];s=r/'a29-conditional-family-v1';d=r/'a29-conditional-validation-v1';f=json.loads((s/'PREDECLARED-FAMILY.json').read_text());rows=[]
for x in f['frames']:
 t=x['tick'];prefix=d/f'tick-{t}.guard';args=[str(r/'tool/target/release/a29_pair_fold_validate'),str(s/f'tick-{t}.old.bin'),str(s/f'tick-{t}.new.bin'),str(s/f'tick-{t}.prefix.json'),str(s/f'tick-{t}.interface.json'),str(prefix)]
 out=subprocess.check_output(args,text=True);(d/f'tick-{t}.result.json').write_text(out);p=json.loads(out);assert p['status']=='PAIRED_FULL_QUANTUM_INTERFACE_PASS_INPUT_ONLY_DIFFERENCE_GUARD'
 b=prefix.with_suffix('.guard.bin').read_bytes();assert b[:8]==b'MRMASK01';n,np,nr=struct.unpack_from('<QQQ',b,8);assert nr==1 and len(b)==32+n*16+nr*4;nodes=list(struct.iter_unpack('<4I',b[32:32+n*16]));root=struct.unpack_from('<I',b,32+n*16)[0];inp=prefix.with_suffix('.guard.input-u64le.bin').read_bytes();exp=prefix.with_suffix('.guard.expected-guard-u64le.bin').read_bytes();assert len(inp)==4*np*8 and len(exp)==4*8
 for trial in range(4):
  ports=struct.unpack_from('<'+'Q'*np,inp,trial*np*8);v=[]
  for i,(k,a,c,aux)in enumerate(nodes):
   assert aux==0
   if k==0:x=0
   elif k==1:x=(1<<64)-1
   elif k==2:assert a<np;x=ports[a]
   else:
    assert a<i and c<i and k in[3,4,5];x=v[a]^v[c]if k==3 else v[a]&v[c]if k==4 else v[a]|v[c]
   v.append(x)
  assert v[root]==struct.unpack_from('<Q',exp,trial*8)[0],(t,trial)
 rows.append(dict(tick=t,status='COMPILED_BINARY_INDEPENDENT_PYTHON_EQUALS_PROTECTED_HELPER',shots=256,nodes=n,guard_false_lanes=p['validation_guard_false_lanes'],guard_true_lanes=p['validation_guard_true_lanes'],guard_sha256=hashlib.sha256(b).hexdigest()));print(t,rows[-1]['status'],flush=True)
(d/'summary.json').write_text(json.dumps(dict(status='ALL29_COMPILED_GUARDS_INDEPENDENT_PARSE_AND_PROTECTED_QUANTUM_CONTROLS_PASS',total_shots=sum(x['shots']for x in rows),rows=rows,not_authority='Finite controls supplement universal paired component proofs; actual-prefix composition and source-chain proof remain required.'),indent=2)+'\n')
