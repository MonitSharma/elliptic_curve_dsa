"""Minimum cost disjoint capsule cover of complete peak intervals; no scores."""
import bisect,collections,heapq,json,unittest
from pathlib import Path

def cover(cells,peaks,entry=None):
    starts=[p[0] for p in peaks];ends=[p[1] for p in peaks]
    assert all(a<=b for a,b in peaks)
    assert all(peaks[i][1]+1<peaks[i+1][0] for i in range(len(peaks)-1))
    candidates=[];excluded=collections.Counter();covered=[0]*len(peaks)
    for j,c in enumerate(cells):
        if entry is not None and not entry[j]:excluded['entry_not_all_top_with_zero_target']+=1;continue
        first=bisect.bisect_left(ends,c['start'])
        last=bisect.bisect_left(starts,c['full_end_exclusive'])-1
        if first>last:excluded['no_peak_intersection']+=1;continue
        # After the old Hmr, the carry may already be free. Do not count those
        # later cleanup ops as a saving, even if scan.json's tentative window did.
        lo=c['start']+2;hi=c['last_main_measurement']
        if starts[first]<lo or ends[last]>hi:
            excluded['cannot_cover_all_peak_points_in_frame']+=1;continue
        candidates.append((c['start'],c['full_end_exclusive'],first,last,c['worst_case_added_T'],j))
        for k in range(first,last+1):covered[k]+=1
    candidates.sort()
    best={0:(0,())};pending=[];serial=0
    def flush(before):
        while pending and pending[0][0]<=before:
            _,_,state,cost,path=heapq.heappop(pending)
            if state not in best or cost<best[state][0]:best[state]=(cost,path)
    for start,end,first,last,cost,j in candidates:
        flush(start)
        if first in best:
            old,path=best[first];serial+=1
            heapq.heappush(pending,(end,serial,last+1,old+cost,path+(j,)))
    flush(float('inf'))
    final=best.get(len(peaks))
    return {'status':'DISJOINT_CARRY_PEAK_COVER_DIAGNOSTIC_NOT_A_SCORE',
            'peak_regions':len(peaks),'admissible_intersecting_cells':len(candidates),
            'excluded':dict(excluded),'uncovered_regions':sum(x==0 for x in covered),
            'first_uncovered_regions':[peaks[i] for i,x in enumerate(covered) if x==0][:20],
            'furthest_reachable_peak_index':max(best),
            'complete_cover':final is not None,'minimum_worst_case_added_T':final[0] if final else None,
            'within_600_T_budget':final is not None and final[0]<=600,
            'selected_cell_indices':list(final[1]) if final else [],
            'selected_cells':[cells[j] for j in final[1]] if final else [],
            'saving_window':'start+2 through original Hmr inclusive; full frames pairwise disjoint',
            'scope':'Coverage is necessary under this method; final complete width and cost still require measurement.'}

class Controls(unittest.TestCase):
    def c(self,s,e,m,cost=1):
        return dict(start=s,full_end_exclusive=e,last_main_measurement=m,worst_case_added_T=cost)
    def test_one_frame_can_cover_several_peaks(self):
        x=cover([self.c(0,20,18)],[(4,5),(10,12)])
        self.assertEqual(x['minimum_worst_case_added_T'],1)
    def test_disjoint_frames_combine(self):
        x=cover([self.c(0,10,8),self.c(10,20,18)],[(4,5),(14,15)])
        self.assertEqual(x['minimum_worst_case_added_T'],2)
    def test_overlapping_frames_do_not_combine(self):
        x=cover([self.c(0,12,8),self.c(10,20,18)],[(4,5),(14,15)])
        self.assertFalse(x['complete_cover'])
    def test_partial_continuous_peak_cannot_be_chained(self):
        x=cover([self.c(0,10,8),self.c(10,20,18)],[(4,15)])
        self.assertFalse(x['complete_cover'])
    def test_entry_filter(self):
        self.assertFalse(cover([self.c(0,20,18)],[(4,5)],[False])['complete_cover'])
    def test_less_expensive_complete_cover(self):
        x=cover([self.c(0,10,8,2),self.c(10,20,18,2),self.c(0,20,18,3)],[(4,5),(14,15)])
        self.assertEqual(x['minimum_worst_case_added_T'],3)
    def test_cleanup_after_measurement_is_not_a_saved_live_carry(self):
        self.assertFalse(cover([self.c(0,20,12)],[(13,14)])['complete_cover'])

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='test':unittest.main(argv=[sys.argv[0]])
    else:
        r=Path(__file__).resolve().parent;s=json.loads((r/'scan.json').read_text())
        p=json.loads((r/'profile.json').read_text())
        assert json.loads((r/'profile-control.json').read_text())['status']=='INSTRUMENTATION_OUTPUT_AND_ALL_EXISTING_FIELDS_IDENTICAL'
        result={'input_full_sha3_256':s['input_sha3_256'],
                'all_structural_cells':cover(s['cells'],p['full_width_regions']),
                'all_top_entry_cells':cover(s['cells'],p['full_width_regions'],p['carry_entry_all_operands_unknown_and_target_zero'])}
        (r/'coverage.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:{a:b for a,b in v.items() if a not in ('selected_cells','selected_cell_indices')} if isinstance(v,dict) else v for k,v in result.items()},indent=2))
