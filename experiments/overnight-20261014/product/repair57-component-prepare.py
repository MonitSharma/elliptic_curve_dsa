"""Source-bound actual104 fold and roomy forward/inverse finite fixtures."""
from pathlib import Path
import json,sys,subprocess
base,out,manifest,frames,kernel=map(Path,sys.argv[1:])
r=next(r for r in json.loads(manifest.read_text())['rows'] if r['payload']==[False,104])
row=next(x.split('\t') for x in frames.read_text().splitlines() if x.startswith('before-fold-producer\t104\t'))
tg=list(map(int,row[3].split(',')));assert tg[:56]==r['acc'] and len(tg)==256
ids=lambda a:'&['+','.join(map(str,a))+']'
header='const NQ:usize=%d;const NB:usize=%d;\n'%(r['entry_dims'][0],r['entry_dims'][1])
for name,a in [('TG',tg),('E',r['e']),('NM',r['nm']),('K',r['k']),('FQ',r['entry_state'][0]),('FB',r['entry_state'][1])]:header+='const '+name+':&[u64]='+ids(a)+';\n'
(out/'product_repair57_tests.rs').write_text(header+Path(__file__).with_name('repair57-component-tests.rs').read_text(),newline='\n')
(out/'product_repair57_kernel.rs').write_bytes(kernel.read_bytes())
s=subprocess.check_output(['git','-C',str(base),'show','c5bb1ec876db859a3f9f8a9052c140a145df834e:src/point_add/y15_onefold.rs'],text=True)
needle='fn fold_window(t: usize, rev: bool) -> usize {';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    #[cfg(test)] if let Some((a,b))=PRODUCT_REPAIR57_WIDTH.with(|x|x.get()){return if rev{b}else{a};}')
s+='\n#[cfg(test)] thread_local!{static PRODUCT_REPAIR57_WIDTH:std::cell::Cell<Option<(usize,usize)>>=const{std::cell::Cell::new(None)};}\n#[cfg(test)] #[path="product_repair57_tests.rs"]mod product_repair57_tests;\n'
(out/'y15_onefold.rs').write_text(s,newline='\n')
