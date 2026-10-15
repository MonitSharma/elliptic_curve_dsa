exec((__import__('pathlib').Path(__file__).parent/'prepare-region.py').read_text().split('oldwhole=')[0])
contract=json.loads((r/'source-middle-interface.json').read_text());assert contract['status']=='SOURCE_PREFIX_AND_ACTUAL_MIDDLE_INTERFACE_PROVED'
start=contract['actual_begin'];hmr=contract['actual_hmr'];stop=hmr+whole_end-site
oldwhole=final[start*56:stop*56];oldrows=list(struct.iter_unpack('<7Q',oldwhole));off=hmr-start
assert oldrows[off:off+len(block)]==block
newwhole=oldrows[:off]+new+oldrows[off+len(block):];flatnew=b''.join(struct.pack('<7Q',*o)for o in newwhole)
assert [o for o in newwhole if o[0]in[11,12]]==[o for o in oldrows if o[0]in[11,12]]
assert sum(o[0]in[13,14]for o in newwhole)==sum(o[0]in[13,14]for o in oldrows)
assert {q for o in newwhole for q in o[1:4]if q!=none}=={q for o in oldrows for q in o[1:4]if q!=none}
(r/'front_seam.bin').write_bytes(b'FRONTSE1'+struct.pack('<2I',len(oldrows),len(newwhole))+oldwhole+flatnew)
candidateraw=final[:start*56]+flatnew+final[stop*56:];bound=z.ZSTD_compressBound(len(candidateraw));out=ctypes.create_string_buffer(bound);size=z.ZSTD_compress(out,bound,candidateraw,len(candidateraw),3);(r/'prototype.bin').write_bytes(b'QECCOPSZ'+struct.pack('<Q',len(candidateraw)//56)+out.raw[:size])
save(r/'old-component.bin',block);save(r/'new-component.bin',new)
result=dict(admission='B',source_primitive='leapfrog::seed_r0_seam classical-ox overflow erase',raw_begin=begin,raw_end=whole_end,raw_hmr=site,final_begin=start,final_end=stop,final_hmr=hmr,subtraction_end=contract['actual_subtraction_end'],old_component_ops=len(block),new_component_ops=len(new),component_offset=off,lower_q=lowq,lower_classical_bit=lowbit,measured_and_borrow_target=target,measurement_bit=bit,u=u,v=v,first_ccx_local=first,first_carry_phase_cz_local=cz,source_prefix_actual_middle_contract=contract,old_region_sha256=hashlib.sha256(oldwhole).hexdigest(),new_region_sha256=hashlib.sha256(flatnew).hexdigest(),prototype_sha256=hashlib.sha256((r/'prototype.bin').read_bytes()).hexdigest(),delta_toffoli=0,delta_mr=0,delta_ops=4,unchanged_ops_outside_full_seam=True,all_inherited_edits_retained=True)
(r/'region.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items()if k not in['source_prefix_actual_middle_contract','u','v']})
