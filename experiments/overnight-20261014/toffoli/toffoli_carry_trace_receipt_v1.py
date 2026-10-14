"""Compact guard trace receipt with all tight-plan failures preserved."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

def main():
    parser=argparse.ArgumentParser();parser.add_argument('evidence',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();text=(args.evidence/'run.log').read_text(errors='replace')
    records=[];context=None
    for line in text.splitlines():
        if match:=re.search(r'TOFFOLI_CARRY_CONTEXT_START cap=(\d+) room=(\d+) tick=(\d+)',line):
            context={'cap':int(match[1]),'room':int(match[2]),'tick':int(match[3])};records.append(context)
        if match:=re.search(r'TOFFOLI_CARRY_LIVE payload=Some\(\(false, (\d+)\)\) fin=(\d+) ttm=(true|false).*drop=(\d+)',line):
            assert context is not None and context['tick']==int(match[1])
            context.update(fin=int(match[2]),ttm=match[3]=='true',drop=int(match[4]))
    exits={tuple(map(int,line.split()[:2])):int(line.split()[2]) for line in (args.evidence/'context-exits.tsv').read_text().splitlines()[1:]}
    assert len(exits)==len(records)==126
    for record in records:record['exit']=exits[(record['room'],record['tick'])]
    result={'status':'resource_guard_trace_completed_with_individual_plan_failures_preserved',
            'run_exit':int((args.evidence/'run.exit').read_text()),'pid':int((args.evidence/'run.pid').read_text()),
            'contexts':records,'context_exit_counts':dict(Counter(str(record['exit']) for record in records)),
            'successful_fin_ttm_counts':dict(Counter(f"fin{record.get('fin')}_ttm{record.get('ttm')}" for record in records if record['exit']==0)),
            'quarter_TT_MAJ_regeneration_guard_contexts':sum(record['exit']==0 and record.get('fin')==0 and record.get('ttm') for record in records),
            'H45_preliminary_guard_contexts_lean_unchecked':sum(record['exit']==0 and record.get('fin')==0 and not record.get('ttm') and record.get('drop')==0 for record in records),
            'hashes':{name:hashlib.sha256((args.evidence/name).read_bytes()).hexdigest() for name in ['run.log','settings.txt','test-binary.sha256','receipt/receipt.json','context-exits.tsv']},
            'limits':'Resource-only original body atcap1234;126 arbitrary initial room/tick recipes, not actual full-circuit occurrence counts. Missing guards on failed plans remain missing. H45 needs additional nonlean guard. No native producer/value/phase or scored claim.'}
    args.output.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    print(json.dumps({key:result[key] for key in ['status','context_exit_counts','successful_fin_ttm_counts','quarter_TT_MAJ_regeneration_guard_contexts','H45_preliminary_guard_contexts_lean_unchecked']}))
if __name__=='__main__':main()
