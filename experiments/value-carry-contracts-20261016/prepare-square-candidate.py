from pathlib import Path
import json,hashlib,struct,subprocess,shutil
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016')
family=json.loads((r/'SQUARE4-PREDECLARATION.json').read_text());interface=json.loads((r/'square-interfaces.json').read_text())
assert len(family['sites'])==4 and len(interface['rows'])==4
exec((r/'analyze-square.py').read_text().split('rawpath=')[0])
final=load(r.parent/'product-exact-20261015/tip/ops.bin');assert len(final)//56==11630716
tail=final[-96*56:];tail_ops=list(struct.iter_unpack('<7Q',tail));assert len(tail_ops)==96
assert all(o[0]==6 and o[1:3]==(N,N)and o[3]in[0,1]and o[4:]==(N,N,N)for o in tail_ops)
assert all(tail_ops[i]==tail_ops[i+1]for i in range(0,96,2))
body=final[:-len(tail)];digest=hashlib.shake_256(body).digest(32)
blob=bytearray(b'QVCARY01'+struct.pack('<Q',4));metas=[];changes=[]
def ccx(a,b,t):return struct.pack('<7Q',13,a,b,t,N,N,N)
for x in interface['rows']:
 a,b=x['actual_window'];old=final[a*56:b*56];at=x['actual_terminal']-a;p=x['previous'];q=x['penultimate'];t=x['top_bit'];u=x['next'];d=0
 assert hashlib.sha256(old).hexdigest()==x['old_window_sha256'];assert old[at*56:(at+1)*56]==ccx(p,q,t)
 assert len({p,q,t,u,d})==5
 patch=(ccx(p,q,d)+ccx(d,t,u))*2+ccx(p,q,t)
 new=old[:at*56]+patch+old[(at+1)*56:];assert len(new)==len(old)+4*56
 blob+=struct.pack('<QQ',len(old)//56,len(new)//56)+old+new
 metas.append(f'Meta{{at:{at},p:{p},a:{q},t:{t},u:{u},d:0,shift:{x["shift"]}}}')
 changes.append((a,b,new))
(r/'square_carry.bin').write_bytes(blob)
s=(r/'square_carry.template.rs').read_text().replace('@INPUT_DIGEST@',str(list(digest))).replace('@INPUT_OPS@',str(len(body)//56)).replace('@META@',','.join(metas))
assert '@'not in s;(r/'square_carry.rs').write_text(s)
predicted=bytearray();cursor=0
for a,b,new in sorted(changes):predicted+=final[cursor*56:a*56]+new;cursor=b
predicted+=final[cursor*56:];assert len(predicted)==len(final)+16*56
receipt=dict(family_predeclaration_sha256=hashlib.sha256((r/'SQUARE4-PREDECLARATION.json').read_bytes()).hexdigest(),original_sha256=hashlib.sha256(final).hexdigest(),expected_candidate_canonical_sha256=hashlib.sha256(predicted).hexdigest(),expected_candidate_ops=len(predicted)//56,
 input_pre_tail_ops=len(body)//56,input_pre_tail_shake256_32=digest.hex(),input_full_native_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',old_tail_identical=True,
 physical_MR_sequence='all original906156R/HMR instructions and draw ordinals identical',added_CCX=16,added_Q=0,added_MR=0,new_classical_bits=0,source_family_all4=True)
(r/'square-predicted-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
tip=r.parent/'product-exact-20261015/tip';dest=r/'square4-candidate';rev=family['base_revision'];assert not dest.exists()
assert subprocess.check_output(['git','-C',str(tip),'rev-parse','HEAD'],text=True).strip()==rev
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(dest),rev],check=True)
for name in ['square_carry.rs','square_carry.bin']:shutil.copy2(r/name,dest/'src/point_add'/name)
p=dest/'src/point_add/mod.rs';s=p.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");';assert s.count(needle)==1
p.write_text('mod square_carry;\n'+s.replace(needle,'    ops = square_carry::run(ops);\n'+needle))
subprocess.run(['git','-C',str(dest),'add','-N','src/point_add/square_carry.rs','src/point_add/square_carry.bin'],check=True)
(r/'square4-source.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(r/'square4-source.json').write_text(json.dumps(dict(base=rev,only_point_add=True,all_original_tables_and_assertions_retained=True,new_pass_after_all_original_passes_before_identity_tail=True,
 files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
(r/'tool/src/bin/square_native_guard.rs').write_text('pub use quantum_ecc::circuit;\n#[path="/home/hclau/ecdsa_research/value-carry-contracts-20261016/square4-candidate/src/point_add/square_carry.rs"]mod square_carry;\nfn main(){}\n')
print(json.dumps(receipt))
