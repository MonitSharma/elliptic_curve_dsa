"""Exact inherited-table ID floor for the bank-only width tradeoff."""
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
BASE=ROOT/'agents/product'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    table=BASE/'src/point_add/y42_bound.bin';blob=table.read_bytes();ne=struct.unpack_from('<I',blob,24)[0];flat=28+12*ne
    rows=[struct.unpack_from('<6H',blob,i) for i in range(flat,len(blob),12)]
    hits=[]
    for edit in range(ne):
        idx,first,count=struct.unpack_from('<III',blob,28+12*edit)
        for j in range(first,first+count):
            if 1233 in rows[j][1:4]:
                hits.append({'edit':edit,'input_op_index':idx,'row_index':j,'rows_in_replacement':count,
                             'row_kind_qcontrol2_qcontrol1_qtarget_ctarget_ccondition':list(rows[j])})
    assert len(hits)==2
    linear=BASE/'src/point_add/linear_restore.bin';b=linear.read_bytes();ln=struct.unpack_from('<I',b,0)[0];lflat=4+12*ln
    lrows=[struct.unpack_from('<6H',b,i) for i in range(lflat,len(b),12)]
    maximum=max(x for row in lrows for x in row[1:4] if x!=65535)
    assert maximum==1200
    result={'status':'retained_stream_tables_force_scored_qubit_ID_floor_1234',
            'conditional_minimum_scored_qubits':1234,'literal_q1233_emitted_rows':hits,
            'y42_table_sha256':sha(table),'linear_table_sha256':sha(linear),
            'linear_expected_and_replacement_max_qubit_ID':maximum,
            'scorer_source_sha256':sha(BASE/'src/bin/eval_circuit.rs'),
            'analyze_ops_source_sha256':sha(BASE/'src/circuit.rs'),
            'logic':'Every selected y42 replacement row is appended verbatim. Two referenced rows contain q1233. linear_restore asserts its expected six-field record before replacing an op; no expected row refers to q1233, so it cannot remove either high-ID row. The active stream has no later general rewrite (skywalk branch inactive in the leapfrog recipe), only the q0 tail. analyze_ops counts max quantum field ID+1 without consulting measurement/control values. Thus a bank-only candidate retaining these tables and applying them successfully cannot score fewer than1234 qubits.',
            'limits':'This is a structural conditional width floor, not a completed builder or scored record. Does not exclude a separately proved qubit remapping or revised inherited table. No row is removed based on sampled or never-observed control values.'}
    HERE.joinpath('bank-table-width-obstruction.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result,indent=2))

if __name__=='__main__':main()
