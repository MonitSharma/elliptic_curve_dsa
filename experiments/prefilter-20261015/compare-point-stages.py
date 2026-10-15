import json,re
from pathlib import Path
import walk_model as m
root=Path(__file__).parent
rows=json.loads((root/'packets/audit-rows.json').read_text())
points={};reverse={};forward={}
for line in (root/'evidence/observer-reverse.log').read_text().splitlines():
    z=re.match(r'POINT_OBS shot=(\d+) stage=(\w+) x=(0x\w+) y=(0x\w+)',line)
    if z:
        shot,stage,x,y=z.groups();points[int(shot),stage]=(int(x,16),int(y,16))
    z=re.match(r'MODEL_REV shot=(\d+) phase=(\w+) tick=(\d+) r0=(0x\w+) r1=(0x\w+)',line)
    if z:
        shot,phase,tick,x,y=z.groups();reverse[int(shot),phase,int(tick)]=(int(x,16),int(y,16))
    z=re.match(r'MODEL_OBS shot=(\d+) phase=(\w+) tick=(\d+) r0=(0x\w+) r1=(0x\w+)',line)
    if z:
        shot,phase,tick,x,y=z.groups();forward[int(shot),phase,int(tick)]=(int(x,16),int(y,16))
offsets=[]
for shot,row in enumerate(rows):
    if row['value']!='0':continue
    tx,ox=[int(row[k],16) for k in ('tx','ox')]
    offsets.append((points[shot,'after_divide'][0]-(tx-ox+3*ox))%m.P)
assert len(set(offsets))==1
offset=offsets[0]
report=[]
for shot,row in enumerate(rows):
    tx,ty,ox,oy=[int(row[k],16) for k in ('tx','ty','ox','oy')]
    d=(tx-ox)%m.P;dy=(ty-oy)%m.P
    slope,_,_=m.walk(d,leg='divide',payload=dy)
    div=points[shot,'after_divide'];square=points[shot,'after_square'];mul=points[shot,'after_multiply']
    recovered=(2*reverse[shot,'divide',1][1])%m.P
    recovered_m=(2*reverse[shot,'multiply',1][1])%m.P
    actual_d=(div[0]-3*ox-offset)%m.P
    square_field=(2*forward[shot,'multiply',0][1])%m.P
    product,_,_=m.walk(square_field,False,'multiply',payload=square[1])
    div_unit=all(v in (1,m.P-1) for v in forward[shot,'divide',137])
    mul_unit=all(v in (1,m.P-1) for v in forward[shot,'multiply',137])
    park=reverse[shot,'multiply',76][1]
    park=park if park<m.P//2 else park-m.P
    park_clean=m.trunc(park,m.STEPS[76][0]-2)==park
    record=dict(shot=shot,value=int(row['value']),division_payload_model_matches=slope==div[1],
                denominator_restored=recovered==d,RT0_recovered_denominator_matches=recovered==actual_d,
                square_on_observed_division_matches=(div[0]-div[1]*div[1]-offset)%m.P==square_field,
                square_seed_encoding_matches=square[0]==(square_field if square_field&1 else (square_field+(1<<32)+977)%(1<<256)),
                modeled_divide_plus_recovered_denominator_matches=(recovered+3*ox-slope*slope)%m.P==square_field,
                multiply_payload_on_observed_input_matches=product==mul[1],
                multiply_restoration_matches=(ox-recovered_m)%m.P==mul[0],
                division_N2_loan_clean=div_unit,multiply_N2_loan_clean=mul_unit,multiply_FM_loan_clean=park_clean,
                recovered_denominator=f'{recovered:x}',original_denominator=f'{d:x}')
    report.append(record)
summary={k:sum(r[k]for r in report) for k in report[0] if k.endswith('_matches') or k=='denominator_restored'}
result=dict(shots=len(rows),source='4b2ec52f',status='DIAGNOSTIC_COMPONENT_CHECKS_NOT_CERTIFICATE',offset_inferred_for_diagnostic_only=f'{offset:x}',summary=summary,details=report)
(root/'evidence/point-stage-differential.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k!='details'}))
