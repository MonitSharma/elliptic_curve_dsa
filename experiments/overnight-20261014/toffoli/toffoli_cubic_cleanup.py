"""Explore measured-bank cleanup with fully charged controlled CCZ repairs."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
from toffoli_guided_joint import Space,combination
from toffoli_quadratic_closure import load
from toffoli_phase_basis import phase_expression


def cubic_expression(target,available):
    quad=Space(available)
    quad_terms=[('one',0,0)]+[('z',i,i) for i in range(1,len(available))]
    quad_values=list(available)
    for i,j in itertools.combinations(range(1,len(available)),2):
        quad_terms.append(('cz',i,j));quad_values.append(available[i]&available[j]);quad.add(quad_values[-1])
    cubic_terms=[];cubic_values=[]
    for i,j,k in itertools.combinations(range(1,len(available)),3):
        value=available[i]&available[j]&available[k]
        if quad.express(value) is not None:continue
        cubic_terms.append(('ccz',i,j,k));cubic_values.append(value)
    full=Space(quad_values+cubic_values)
    answer=full.express(target)
    if answer is None:return None
    # Space stores independent original values and expresses against that
    # independent list, so recover corresponding terms by original insertion.
    terms=[];builder=Space()
    for term,value in zip(quad_terms+cubic_terms,quad_values+cubic_values):
        if builder.add(value):terms.append(term)
    assert len(terms)==len(full.values)
    chosen=[terms[i] for i in range(len(terms)) if answer>>i&1]
    assert combination(answer,full.values)==target
    return chosen


def main():
    p=argparse.ArgumentParser();p.add_argument('netlist',type=Path);p.add_argument('basis',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    net=json.loads(a.netlist.read_text());basis=json.loads(a.basis.read_text());raw,targets,original=load(net)
    rows=[(name,mask) for name,mask in basis['basis_rows'] if name in basis['remaining_banks']]
    banks=[(name,combination(mask,original[len(raw):])) for name,mask in rows]
    data=list(raw);data[1:7]=targets[21:27]
    steps=[];started=time.monotonic()
    while banks:
        candidates=[]
        for index,(name,value) in enumerate(banks):
            other=[b for j,b in enumerate(banks) if j!=index]
            expression=cubic_expression(value,data+[v for name,v in other])
            if expression is not None:
                count=sum(term[0]=='ccz' for term in expression)
                candidates.append((count,len(expression),index,expression))
        if not candidates:break
        count,terms,index,expression=min(candidates,key=lambda c:c[:3])
        name,value=banks.pop(index)
        steps.append({'erased':name,'controlled_CCZ':count,'phase_terms':expression,
                      'available_order':[f'data{i}' for i in range(len(data))]+[name for name,v in banks]})
    report={'status':'cubic_cleanup_found' if not banks else 'cubic_greedy_cleanup_incomplete',
            'source_lf_sha256':net['source_lf_sha256'],'domain_rows':1<<14,
            'basis_sha256':hashlib.sha256(a.basis.read_bytes()).hexdigest(),
            'controlled_CCZ_total':sum(s['controlled_CCZ'] for s in steps),'steps':steps,
            'remaining':[name for name,v in banks],'seconds':time.monotonic()-started,
            'limits':'All repair identities exact on constructor domain. Each CCZ costs a Toffoli conditioned on an independent measurement. No native integration or all-input full-circuit verification. This greedy term basis is not a minimum-cost phase synthesis.'}
    a.output.write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps({k:report[k] for k in ['status','controlled_CCZ_total','remaining','seconds']}))


if __name__=='__main__':main()
