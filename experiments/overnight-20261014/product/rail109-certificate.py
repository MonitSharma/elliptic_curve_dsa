"""Exact integer certificate for the first point249 multiply rail deviation."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[3];raw=root/'research-output/overnight-20261014/product/walk-replay/run.log'
rows=[]
for line in raw.read_text().splitlines():
 if line.startswith('PRODUCT_WALK_FRAME '):
  r=dict(re.findall(r'(\w+)=(\S+)',line))
  if (r['mode'],r['index'],r['scope'],r['t'])==('official_known_bad','249','mul','109'):rows.append(r)
def signed(r,i):
 n=int(r[f'r{i}'],16);w=int(r[f'r{i}_width']);return n-2**w if n>>(w-1)else n
certificates=[]
for source in ['c5_raw','b3_raw']:
 before=next(r for r in rows if r['source']==source and r['label']=='fwd_tick_before');after=next(r for r in rows if r['source']==source and r['label']=='fwd_tick_after')
 T=signed(before,1);B=signed(before,0);assert after['letter']=='00001'
 trace=[]
 for i in range(3):
  total=T+B;assert total%2==0
  T=total//2;trace.append(dict(step=i,unbounded_sum=total,exact_halved_target=T))
 assert T%4==0
 exact=T//4;actual=signed(after,1)
 # Active fixed recipe selects pack_t0hat_tail0_138_steps_k770_lw2.txt, row109 W/n0/n1/n2/nb=62/62/61/60/59.
 # Under LF_LOWREL the choice acts on n2-1 physical bits and produces an even full-word target there.
 choice_output_width=59
 wrapped=T%(2**choice_output_width);wrapped_signed=wrapped-2**choice_output_width if wrapped>>(choice_output_width-1)else wrapped
 assert wrapped_signed%4==0
 assert wrapped_signed//4==actual
 assert exact-actual==2**57
 assert -(2**59)<=exact<2**59 # exact final target fits the actual60-bit reported full-word output
 certificates.append(dict(source=source,before=before,after=after,source_integer=B,trace=trace,choice_output_width=choice_output_width,choice_exact_fits=False,
  choice_wrapped_signed=wrapped_signed,barrel_exponent=2,exact_final=exact,actual_final=actual,final_difference=actual-exact,exact_final_fits_observed_output=True))
doc=dict(status='EXACT_FINITE_INTEGER_OVERFLOW_CERTIFICATE',qualified_score=None,
 explanation='With s0=s1=s3=0, the exact second-forced result fits its full-word60-bit width, but the choice result requires60 signed bits. fast_add_halve_choice_lr writes its even halved full-word target into59 physical bits (n2-1). Its modular rail addition wraps by2^59; the subsequent two-bit barrel divides this signed wrapped value by4, giving the observed -2^57 error. Later sign extension to the reported60-bit full-word output cannot recover the lost bit.',
 native_log_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),schedule='Active installed LF_G10_TABLE=770; leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt row109=[62,62,61,60,59].',
 source_locations=['leapfrog.rs::fwd_tick_fast resize target to n2-lowrel','leapfrog.rs::fast_add_halve_choice_lr unsigned rail_add on n2-1 physical bits','leapfrog.rs::fast_rail_barrel','leapfrog.rs::fwd_tick_fast resize to next tick width'],certificates=certificates,
 scope='One exact source-supported counterexample, matching both native original streams; not a global repair or score. Original full byteidentity and all binding checks preserved.')
out=Path(__file__).with_name('rail109-certificate.json');out.write_text(json.dumps(doc,indent=2)+'\n',newline='\n')
print(json.dumps(doc,indent=2))
