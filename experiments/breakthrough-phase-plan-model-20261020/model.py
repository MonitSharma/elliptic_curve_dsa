"""Specified uniform-rank cost model, never a scored arithmetic result."""
import functools,hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;results=[]
for rank in[1,2]:
 for budget in range(7,13):
  @functools.lru_cache(None)
  def solve(left,kept):
   room=budget-kept
   if room<0:return None
   best=None
   for width in range(1,left+1):
    last=width==left;owned=max(0,width-2)if last else width;need=max(0,owned-room)
    inner=max(0,width-2)if last else width-1
    if need and(inner<3 or need>(inner-1)//2):continue
    tail=(0,())if last else solve(left-width,kept+1)
    if tail is None:continue
    choice=((0 if last else width-1)+need*rank+tail[0],((width,need),)+tail[1])
    if best is None or(choice[0],len(choice[1]),choice[1])<(best[0],len(best[1]),best[1]):best=choice
   return best
  answer=solve(50,0)
  results.append({'uniform_adjacent_source_row_rank':rank,'carry_budget':budget,'bits':50,'feasible':answer is not None,
   'extra_toffoli_x2':answer[0]if answer else None,'model_total_expected_toffoli':49+answer[0]/2 if answer else None,
   'chunks_and_internal_drop_counts':answer[1]if answer else None})
report={'status':'EXACT_DP_FOR_SPECIFIED_UNIFORM_RANK_MODEL_ONLY','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'cost':'Base n-1; nonfinal boundary expected(w-1)/2; each internal phase drop expected source-row-rank/2. Retained boundary count contributes to each chunk peak.',
 'admission':'Nonfinal width w owns w wires including external output, inner pebble prefix m=w-1. Final width w owns max(w-2,0). Internal drops need <=floor((m-1)/2).',
 'limitations':['Not a native or scored point-add result.','Uniform source ranks, disjoint operands, no boundary drops and no extra fixed-core workspace are assumed.','Existing source-specific gate cancellations, copy/phase contracts and conditional source rows require a native weighted planner and validation.','Does not prove a lower bound over arbitrary adders or circuits.'], 'results':results}
(r/'MODEL-RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(results,indent=2))
