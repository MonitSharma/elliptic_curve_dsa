"""Compact exact-search receipt; raw solver details remain outside Git."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('raw',type=Path)
    parser.add_argument('--pid',type=int,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();receipt=json.loads(args.raw.read_bytes())
    records=receipt.get('examined',receipt.get('planes',[]))
    summary={key:value for key,value in receipt.items() if key not in ['examined','planes']}
    summary.update(records_examined=len(records),status_counts=dict(Counter(record.get('status','incomplete') for record in records)),
                   closed_prefix_AND_distribution=dict(Counter(str(record.get('final_ANDs')) for record in records)),
                   witnesses=int(receipt['status'] in ['value_witness_found','30_AND_complete_value_witness',
                                                       '24_AND_joint_reverse_value_witness']),
                   solver_unknowns=sum(record.get('status')=='factor_unknown_unresolved' for record in records),
                   raw_receipt_bytes=args.raw.stat().st_size,raw_receipt_sha256=hashlib.sha256(args.raw.read_bytes()).hexdigest(),pid=args.pid)
    for suffix in ['log','settings']:
        path=args.raw.with_suffix('.'+suffix)
        summary[suffix+'_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    summary['exit']=int(args.raw.with_suffix('.exit').read_text())
    args.output.write_bytes((json.dumps(summary,indent=2)+'\n').encode())
    print(json.dumps({key:summary[key] for key in ['status','records_examined','status_counts','solver_unknowns','exit']}))


if __name__=='__main__':main()
