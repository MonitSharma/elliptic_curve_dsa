from pathlib import Path
import ctypes,struct,hashlib,json,shutil
r=Path(__file__).resolve().parents[1];d=r/'a29-conditional-family-v1';family=json.loads((d/'PREDECLARED-FAMILY.json').read_text());owner=r.parent/'precision-family-20261016'
z=ctypes.CDLL('libzstd.so.1');z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
def load(p,expected=None):
 b=p.read_bytes()
 if expected:assert hashlib.sha256(b).hexdigest()==expected
 assert b[:8]==b'QECCOPSZ';n=struct.unpack_from('<Q',b,8)[0];o=ctypes.create_string_buffer(n*56);assert z.ZSTD_decompress(o,len(o),b[16:],len(b)-16)==len(o);return o.raw
old=load(r.parent/'product-exact-20261015/tip/ops.bin',family['source_old']);new=load(r.parent/'product-exact-20261015/repair-cache53-20261016/input-1cd3457b.bin',family['source_new']);assert len(old)//56==11630716 and len(new)//56==11636536
cursor_old=cursor_new=0;rows=[]
for frame in family['frames']:
 t=frame['tick'];a,b=frame['old_begin']*56,frame['old_end']*56;c,e=frame['new_begin']*56,frame['new_end']*56
 assert old[cursor_old:a]==new[cursor_new:c],('outside region',t)
 for suffix,actual in [('old',old[a:b]),('new',new[c:e])]:
  p=owner/'isolated'/f'tick-{t}.{suffix}.bin';assert load(p)==actual,('actual/frame mismatch',t,suffix);shutil.copyfile(p,d/p.name)
 shutil.copyfile(owner/'isolated'/f'tick-{t}.interface.json',d/f'tick-{t}.interface.json');rows.append(dict(**frame,actual_old_canonical_sha256=hashlib.sha256(old[a:b]).hexdigest(),actual_new_canonical_sha256=hashlib.sha256(new[c:e]).hexdigest()));cursor_old=b;cursor_new=e
assert old[cursor_old:]==new[cursor_new:]
shutil.copyfile(owner/'interface-analysis.json',d/'existing-interface-analysis.json')
p=json.loads((d/'existing-interface-analysis.json').read_text());assert p['admitted']==p['total']==29 and all(x['admitted_classical_interface']for x in p['rows'])
(d/'actual-fullstream-frame-binding.json').write_text(json.dumps(dict(status='ALL29_ACTUAL_OLD_NEW_FRAMES_AND_ALL_OUTSIDE_OPS_BYTE_IDENTICAL',source_old=family['source_old'],source_new=family['source_new'],frames=rows,live_classical_receipt_sha256=hashlib.sha256((d/'existing-interface-analysis.json').read_bytes()).hexdigest()),indent=2)+'\n');print('ACTUAL_FULL_STREAM_BINDING_PASS',len(rows))
