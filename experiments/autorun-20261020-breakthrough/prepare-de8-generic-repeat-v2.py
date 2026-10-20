from pathlib import Path
a=Path(__file__).parent
old=a.parent/'breakthrough-de8-generic-repeat-20261020'
(old/'STATUS.md').write_text('# Setup stopped before tests or generation\n\nWindows default cp1252 could not decode a UTF-8 source comment while assembling the patch. Partial verified source/freeze retained. V2 reruns preparation in UTF-8 mode in a separate folder; no gate/input/nonce work ran.\n',encoding='utf-8')
s=(a/'prepare-de8-generic-repeat.py').read_text(encoding='utf-8').replace('breakthrough-de8-generic-repeat-20261020','breakthrough-de8-generic-repeat-v2-20261020')
exec(compile(s,str(a/'prepare-de8-generic-repeat.py'),'exec'))
