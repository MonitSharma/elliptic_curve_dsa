"""Independent scalar reference for the MRMASK01 conservative mask ABI."""
from pathlib import Path
import argparse,struct,hashlib,json,time
MASK=(1<<64)-1

def evaluate(program,input_words):
 assert program[:8]==b'MRMASK01', 'bad program magic'
 count,ports,outputs=struct.unpack_from('<QQQ',program,8)
 assert len(program)==32+16*count+4*outputs, 'program length mismatch'
 assert len(input_words)==ports
 values=[0]*count
 for i in range(count):
  kind,a,b,aux=struct.unpack_from('<IIII',program,32+16*i)
  assert aux==0
  if kind==0: value=0
  elif kind==1: value=MASK
  elif kind==2:
   assert a<ports
   value=input_words[a]
  elif kind in (3,4,5):
   assert a<i and b<i, 'forward child reference'
   value=values[a]^values[b] if kind==3 else values[a]&values[b] if kind==4 else values[a]|values[b]
  else: raise AssertionError('unsupported/unknown terminal cannot be treated as known input')
  values[i]=value
 roots=struct.unpack_from('<'+'I'*outputs,program,32+16*count)
 assert all(r<count for r in roots)
 return [MASK^values[r] for r in roots]

def main():
 p=argparse.ArgumentParser();p.add_argument('program');p.add_argument('input');p.add_argument('--expected');p.add_argument('--output');a=p.parse_args()
 raw=Path(a.program).read_bytes();data=Path(a.input).read_bytes();assert len(data)%8==0
 words=struct.unpack('<'+'Q'*(len(data)//8),data)
 start=time.perf_counter();known=evaluate(raw,words);elapsed=time.perf_counter()-start
 packed=struct.pack('<'+'Q'*len(known),*known)
 if a.expected: assert packed==Path(a.expected).read_bytes(),'scalar ABI masks differ from exporter full-DAG audit'
 if a.output: Path(a.output).write_bytes(packed)
 print(json.dumps(dict(program_sha256=hashlib.sha256(raw).hexdigest(),input_sha256=hashlib.sha256(data).hexdigest(),known_sha256=hashlib.sha256(packed).hexdigest(),outputs=len(known),known_bits=sum(w.bit_count() for w in known),seconds=elapsed,expected_match=bool(a.expected),status='INDEPENDENT_SCALAR_ABI_DIFFERENTIAL_ONLY')))
if __name__=='__main__':main()
