"""Read-only schedule budget for proposed N274 map lifetimes; no gates/proof."""
from pathlib import Path
import hashlib,json,sys
schedule,out=map(Path,sys.argv[1:3])
rows=[list(map(int,l.split()[1:])) for l in schedule.read_text().splitlines() if l.startswith('C ')]
first_fin=next((i for i,r in enumerate(rows) if r[4]),len(rows))
result=[]
for i,r in enumerate(rows):
    sw,dn=bool(r[2]),bool(r[3]);m=min(r[10],128)
    nc=min(7,(i-first_fin).bit_length()) if i>first_fin else 0
    extra=(256+21-274) if sw else (257+21-274)
    park=dn and m>121
    parked=nc if park else 0
    # Proposed all ordinary/switch maps erase minimum size before core.
    # mp has ten clean owners; extension starts with bq. A switch counter
    # first parks in sw, while an ordinary counter consumes all nc mp owners.
    mp_park=max(0,parked-1) if sw else parked
    mp_extension=extra-1
    fl=1
    hl=10-mp_park-mp_extension-fl+1
    result.append(dict(column=i,sw=sw,dn=dn,m=m,cntw=nc,lean_park=park,parked=parked,extra=extra,mp_park=mp_park,mp_extension=mp_extension,hl=hl,syp_three_helpers_fit=hl>=3))
receipt=dict(scope='Proposed clean-owner numerical budget from unchanged source schedule only; no lifetime, gates, phase, input-domain or width proof',N=274,K=15,first_fin=first_fin,source_schedule_sha256=hashlib.sha256(schedule.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),columns=result,minimum_hl=min(r['hl'] for r in result),unsafe=[r for r in result if not r['syp_three_helpers_fit']],switch_max_cntw=max(r['cntw'] for r in result if r['sw']),B0=dict(extra=4,proposed_owners=['bq','Q120','Q119','Q118'],counter='Q121..127; outerSW/g retained',status='lifetime_unproved'))
out.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k]for k in ['scope','first_fin','minimum_hl','unsafe','switch_max_cntw','B0']},indent=2))
