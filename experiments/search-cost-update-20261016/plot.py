from pathlib import Path
import hashlib,json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root=Path(__file__).resolve().parent
threads=64
costs={'protected':284.85/128,'simd_low':38.37*2/1024,'simd_high':6.538*16/1024}
rates={'four_stage':17.83154296875,'compact11':17.680938720703125}
def expected(rate):return math.exp(-141*math.log1p(-rate/141))
data={'status':'research_search_cost_projection_not_a_resource_record','workers_projected':threads,'cost_units':'measured thread-seconds per screened nonce','costs':costs,'assumptions':['Independent fresh packet success probability p=(1-lambda/141)^141.','Measured early-rejection cost treated as constant when varying failure rate.','Ideal scaling to64 threads; actual64-thread throughput is not measured.','Timing measured on original public product source; candidate timing is not established.','No product nonce search or benchmark pass follows from this projection.'],'measurements':{'protected':{'nonces':128,'thread_seconds':284.85},'simd_two_workers':{'nonces':1024,'workers':2,'wall_seconds':38.37},'simd_sixteen_workers':{'nonces':1024,'workers':16,'wall_seconds':6.538}},'census_rates':rates,'projected':{},'prefilter_terminal_archive_sha256':'d3007fe2a24e8c01c8428f3aa7b9de3a17bf37920c0fd22f6b2d92219f678c06'}
for name,rate in rates.items():
 n=expected(rate);data['projected'][name]={'expected_nonces':n,'failure_rate':rate,'hours_simd_low':n*costs['simd_low']/threads/3600,'hours_simd_high':n*costs['simd_high']/threads/3600,'hours_protected':n*costs['protected']/threads/3600}
(root/'data.json').write_text(json.dumps(data,indent=2)+'\n')
x=np.linspace(1,20,600);n=np.exp(-141*np.log1p(-x/141));factor=1/(threads*3600)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'ecdsa-search-cost-20261016'})
fig,ax=plt.subplots(figsize=(10.8,6.4),constrained_layout=True)
ax.plot(x,n*costs['protected']*factor,color='#8b93a7',lw=2,label='Original exact screener')
ax.fill_between(x,n*costs['simd_low']*factor,n*costs['simd_high']*factor,color='#2866a5',alpha=.22,label='Integrated exact screener: measured cost range')
ax.plot(x,n*costs['simd_high']*factor,color='#2866a5',lw=2)
for h,label in [(1,'1 hour'),(12,'12 hours'),(24,'1 day')]:
 ax.axhline(h,color='#b8bdc7',lw=.9,ls='--');ax.text(8.15,h*1.12,label,color='#666d7b',fontsize=9)
rate=rates['compact11'];row=data['projected']['compact11'];low,high=row['hours_simd_low'],row['hours_simd_high']
ax.plot([rate,rate],[low,high],color='#cb6b32',lw=3,zorder=4);ax.scatter([rate],[math.sqrt(low*high)],color='#cb6b32',s=48,zorder=5)
ax.annotate(f'Compact11 fresh census: lambda={rate:.3f}\nProjected {low:.0f}–{high:.0f} hours\nCandidate throughput still unmeasured',xy=(rate,math.sqrt(low*high)),xytext=(10.5,600),arrowprops={'arrowstyle':'-','color':'#cb6b32'},color='#9d491d',fontsize=10)
ax.set_yscale('log');ax.set_xlim(8,20);ax.set_ylim(1e-4,2e5)
ax.set_xlabel('Expected failed batches per 9,024-shot packet (lambda)')
ax.set_ylabel('Expected search time at 64 threads (hours; ideal scaling)')
ax.set_title('Product nonce search: measured costs and projected time',loc='left',fontweight='bold',pad=16)
ax.grid(axis='y',which='major',color='#e3e6eb',lw=.7);ax.legend(loc='upper left',frameon=False,fontsize=9)
fig.text(.01,-.045,'p = (1 - lambda / 141)^141; mean search = 1 / p nonces. Constant measured cost assumed across failure rates; actual early rejection work varies.\nOriginal-source timing near lambda17.8; ideal 64-thread scaling. Zero-MR tools excluded while their global proof remains unresolved.',fontsize=9,color='#525b6b')
for ext in ['png','svg']:fig.savefig(root/f'search-cost.{ext}',dpi=180,bbox_inches='tight',metadata={'Date':None} if ext=='svg' else {})
svg=root/'search-cost.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n',newline='\n')
print(json.dumps(data['projected'],indent=2))
