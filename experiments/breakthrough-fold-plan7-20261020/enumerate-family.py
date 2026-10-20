"""Enumerate the existing nonadjacent-drop schedule family, not all adders."""
import itertools,json
from pathlib import Path
r=Path(__file__).resolve().parent

def capacities(budget,k,drops):
    held=set();caps=[]
    for j in range(k):
        caps.append(budget-len(held)+(2 if j==k-1 else 0))
        if caps[-1]<1:return None
        if j<k-1:held.add(j)
        if j>0 and j-1 in drops:
            if j==k-1 or(j>=2 and j-2 not in held):return None
            held.remove(j-1)
    for j in range(k-2,-1,-1):
        if j not in held:continue
        held.remove(j);available=budget-len(held)
        if j==0 or j-1 in held:caps[j]=min(caps[j],available+1)
        else:
            caps[j-1]=min(caps[j-1],available)
            caps[j]=min(caps[j],available)
    assert not held
    return caps if min(caps)>=1 else None

results=[]
for budget in range(2,9):
    maximum=0;best=None;patterns=0;admitted=0
    # Before non-final chunk j, at least ceil(j/2) boundaries are held:
    # no adjacent drops and each drop happens only after the next chunk.
    # Hence a nonempty non-final chunk needs j<=2*budget-2, so K<=2*budget.
    for k in range(1,2*budget+1):
        for mask in range(1<<max(0,k-2)):
            if mask&(mask<<1):continue
            drops={i for i in range(k-2)if mask>>i&1};patterns+=1
            caps=capacities(budget,k,drops)
            if caps is None:continue
            admitted+=1;maximum=max(maximum,sum(caps))
            n=50
            if k>n or sum(caps)<n:continue
            # Width bounds are independent after the allocation simulation.
            # Last-chunk width has weight-1/2, ordinary widths0, dropped
            # widths+3/4. Fill in increasing cost order for an exact integer LP.
            plan=[1]*k;left=n-k
            order=[k-1]+[j for j in range(k-1)if j not in drops]+sorted(drops)
            for j in order:
                amount=min(left,caps[j]-1);plan[j]+=amount;left-=amount
            assert left==0
            ordinary=n-plan[-1]-(k-1)
            emitted=n-1+ordinary+sum(2*plan[j]-1 for j in drops)
            expected_quarters=4*(n-1)+2*ordinary+sum(3*plan[j]-1 for j in drops)
            item={'expected_quarters':expected_quarters,'modeled_expected_ccx':expected_quarters/4,'modeled_emitted_ccx':emitted,
                'plan':plan,'drops':sorted(drops),'caps':caps}
            if best is None or(expected_quarters,emitted,k,plan)<(best['expected_quarters'],best['modeled_emitted_ccx'],len(best['plan']),best['plan']):best=item
    results.append({'budget':budget,'enumerated_patterns':patterns,'admitted_patterns':admitted,'maximum_covered_bits':maximum,'best_fifty_bit_schedule':best})
report={'status':'COMPLETE_ENUMERATION_OF_SPECIFIED_NONADJACENT_DROP_ALLOCATION_FAMILY',
    'family_bound':'K<=2r: before a non-final chunk j at least ceil(j/2) boundaries remain live; width>=1 requires ceil(j/2)+1<=r.',
    'objective':'Uniform generic carry/compare model: T_emit=n-1 + sum_nonfinal(w-1) + sum_dropped(2w-1); E[T]=n-1 + sum_nonfinal(w-1)/2 + sum_dropped(3w-1)/4.',
    'limitations':['Bounds apply to this existing nonadjacent-drop algorithm and uniform generic-stage cost only, not arbitrary adders or point addition.',
        'Source-specific affine cancellations and fixed-core/helper allocation are outside the model. Native source counts remain authoritative.',
        'These schedules are not installed into any new circuit by this enumeration.'],
    'results':results}
(r/'PLAN-FAMILY-ENUMERATION.json').write_text(json.dumps(report,indent=2)+'\n')
for row in results:print(row['budget'],row['maximum_covered_bits'],row['best_fifty_bit_schedule'])
