"""Static descriptive profile figure; never a resource-score or speedup plot."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent;source=root.parent/'repair67-prep-profile-20261016/ANALYSIS.json'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='fb339ba657ba9a5f4941aa62280b70e768fac0e9d8ad98b2b380a9813ef290d0'
data=json.loads(source.read_text());worker=data['selected_nonoverlap_worker_seconds'];startup=data['startup_main_to_window_seconds']
groups=[
 ('Repeated preparation', 'Summed worker time (seconds)', [('Curve points',data['curve_C_worker_seconds'],'#245a81'),('Rail predictor',data['rail_C_worker_seconds'],'#248a87'),('Other preparation',worker-data['curve_C_worker_seconds']-data['rail_C_worker_seconds'],'#a7b5c0')]),
 ('One-time startup', 'Serial wall time (seconds)', [('Own-input checks',data['candidate_seed_diagnostic_seconds'],'#245a81'),('Curve table',data['fixed_scalar_table_init_seconds'],'#248a87'),('Unused C hash',data['unused_C_SHAKE8_update_seconds'],'#d49a4b'),('Actual input hash',data['actual_Rust_SHAKE_prefix_update_seconds'],'#9673a6'),('Other startup',startup-data['candidate_seed_diagnostic_seconds']-data['fixed_scalar_table_init_seconds']-data['unused_C_SHAKE8_update_seconds']-data['actual_Rust_SHAKE_prefix_update_seconds'],'#a7b5c0')])]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False})
fig,axes=plt.subplots(1,2,figsize=(12,6.4));fig.subplots_adjust(left=.05,right=.98,bottom=.36,top=.68,wspace=.22)
for ax,(title,unit,items) in zip(axes,groups):
 total=sum(v for _,v,_ in items);left=0
 for label,value,color in items:
  ax.barh([0],[value],left=left,height=.38,color=color,label=f'{label}: {value:.2f}s ({value/total:.1%})')
  if value/total>.2:ax.text(left+value/2,0,f'{value/total:.1%}',ha='center',va='center',color='white',weight='bold',fontsize=12)
  left+=value
 ax.set_xlim(0,total*1.02);ax.set_ylim(-.4,.4);ax.set_yticks([]);ax.set_xlabel(unit);ax.set_title(f'{title}\n{total:.2f} seconds',loc='left',fontsize=12,pad=12)
 ax.legend(loc='upper left',bbox_to_anchor=(0,-.30),frameon=False,fontsize=9,handlelength=1.2)
fig.suptitle('Where the repaired-candidate filter spends time',x=.05,y=.95,ha='left',fontsize=16,weight='bold')
fig.text(.05,.84,'One fixed 4,096-nonce profile · 3,139,328 input pairs · two worker threads',fontsize=11,color='#374151')
fig.text(.05,.035,'Timing scopes differ and must not be added. One instrumented run under shared load; counters add overhead.\nDescriptive bottleneck evidence only: no stable speedup, persistent-search forecast, or resource record.',fontsize=9,color='#4b5563')
for suffix in ['png','svg']:fig.savefig(root/f'preparation-profile.{suffix}',dpi=180,facecolor='white')
plt.close(fig)
provenance=dict(source=str(source.relative_to(root.parent)),analysis_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),profile_archive_sha256='c8b3551351a57a63d7eeb32edd8b16f53e09e10cca8842bdabc5494abcf56674',fixed_nonces=4096,scalar_pairs=3139328,groups=[dict(title=t,time_unit=u,components=[dict(name=n,seconds=v)for n,v,_ in items])for t,u,items in groups],no_resource_score_or_speedup_claim=True)
(root/'plot-data.json').write_text(json.dumps(provenance,indent=2)+'\n');print('Saved descriptive PNG/SVG and source provenance')
