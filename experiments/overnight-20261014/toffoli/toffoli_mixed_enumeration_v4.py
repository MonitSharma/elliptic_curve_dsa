"""Independent old-rank4 plus coset construction of the mixed plane set."""
import hashlib
import json
from pathlib import Path
from toffoli_guided_joint import Space
from toffoli_external_planes_v2 import subspaces
from toffoli_external_mixed_v4 import mixed_planes


def reduced_rows(vectors):
    rows={}
    for value in vectors:
        for pivot,row in sorted(rows.items(),reverse=True):
            if value>>pivot&1:value^=row
        if value:
            pivot=value.bit_length()-1
            for key,row in list(rows.items()):
                if row>>pivot&1:rows[key]=row^value
            rows[pivot]=value
    return tuple(row for pivot,row in sorted(rows.items(),reverse=True))


def main():
    mixed=set();all_external=set();counts=[]
    for old in subspaces():
        table=Space(old)
        representatives=set()
        for value in range(64):
            for pivot,(row,mask) in sorted(table.rows.items(),reverse=True):
                if value>>pivot&1:value^=row
            representatives.add(value)
        assert len(representatives)==4
        counts.append(len(representatives))
        for value in representatives:
            basis=reduced_rows(list(old)+[64^value]);all_external.add(basis)
            if value:mixed.add(basis)
    direct={reduced_rows(rows) for rows in mixed_planes()}
    assert mixed==direct and len(mixed)==1953 and len(all_external)==2604
    result={'status':'independent_enumeration_passed','old_rank4_subspaces':651,
            'cosets_per_subspace':4,'outside_containing_planes':2604,
            'mixed_planes':1953,'old_only_rank5_planes':63,'total_rank5_planes':2667,
            'set_sha256':hashlib.sha256(json.dumps(sorted(mixed)).encode()).hexdigest(),
            'method':'Independent high-pivot coset elimination and full seven-coordinate rank5 RREF enumeration yield exactly the same1953 subspaces; no solver used.'}
    Path(__file__).with_name('external-mixed-v4-enumeration.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
