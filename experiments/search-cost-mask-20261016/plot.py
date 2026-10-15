from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
root=Path(__file__).resolve().parent
old=json.loads((root.parent/'search-cost-update-20261016/data.json').read_text())
acceptance=json.loads((root.parent/'product25-operational-20261016/ACCEPTANCE.json').read_text())
assert acceptance['cost_gate_pass'] and acceptance['failure_gate_pass']
rate=acceptance['census']['candidate']['failures_per_packet'];expected=acceptance['expected_nonces']
steady=acceptance['measured_expected_hours_48threads']['steady'];startup=acceptance['measured_expected_hours_48threads']['including_startup_per_timing_packet']
x=np.linspace(8,20,500);n=np.exp(-141*np.log1p(-x/141))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'source-bound-mask-search-cost-20261016'})
fig,ax=plt.subplots(figsize=(10.8,6.6),constrained_layout=True)
ax.fill_between(x,n*old['costs']['simd_low']/64/3600,n*old['costs']['simd_high']/64/3600,color='#2d64a0',alpha=.2,label='Previous exact screener: projected at 64 threads')
ax.plot(x,n*old['costs']['simd_high']/64/3600,color='#2d64a0',lw=1.8)
ax.fill_between(x,n/expected*steady,n/expected*startup,color='#23856b',alpha=.25,label='Certified masked screener: measured at 48 threads')
ax.plot(x,n/expected*steady,color='#23856b',lw=2)
for hours,label in [(1,'1 hour'),(12,'12 hours'),(24,'1 day')]:
 ax.axhline(hours,color='#a9b0bd',lw=.8,ls='--');ax.text(8.1,hours*1.11,label,fontsize=9,color='#626a77')
ax.scatter([rate],[steady],s=55,color='#176c54',zorder=5)
ax.annotate(f'Frozen product25: lambda = {rate:.3f}\nMean search: {steady:.1f} h on 48 threads\nConservative startup charge: {startup:.1f} h',xy=(rate,steady),xytext=(11.1,140),arrowprops={'arrowstyle':'-','color':'#176c54'},color='#176c54',fontsize=10)
ax.set(xlim=(8,20),ylim=(1e-4,5e3),yscale='log',xlabel='Expected failed batches per 9,024-shot packet (lambda)',ylabel='Expected search time (hours)',title='Product nonce search after source-bound mask certification')
ax.grid(axis='y',which='major',color='#e0e4ea',lw=.7);ax.legend(loc='upper left',frameon=False,fontsize=9)
fig.text(.01,-.05,'Mean search = 1/(1-lambda/141)^141. Lines hold measured cost constant as failure rate varies. Mean time is not a completion guarantee.\nNew timing: 262,144 fixed candidate25 nonces, 4 processes x 12 threads, 115.36 s including startup. All proof/runtime gates passed; research tool only.',fontsize=9,color='#525b6b')
for ext in ['png','svg']:fig.savefig(root/f'search-cost-mask.{ext}',dpi=180,bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {})
svg=root/'search-cost-mask.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n',newline='\n')
data={'status':'SEARCH_COST_PROJECTION_NOT_A_RESOURCE_RECORD','census_rate':rate,'expected_nonces':expected,'new_measured_threads':48,'mean_hours48':steady,'conservative_startup_hours48':startup,'ideal64_hours':acceptance['ideal64thread_projection_hours'],'median_hours48':math.log(2)*steady,'ninety_percent_hours48':math.log(10)*steady,'previous_original_exact_ideal64_hours':old['projected']['compact25'],'source':'product25-operational-20261016/ACCEPTANCE.json','assumptions':['Fresh packet independence approximation','Constant observed early rejection cost across lambda','New48thread throughput actually measured; previous64thread scaling ideal','No resource record implied by search or diagnostic counts']}
(root/'data.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
