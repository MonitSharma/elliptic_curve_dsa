from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'collect-bound-audit-cycle.py').read_text();start=s.index('names=[');end=s.index('\nsha=',start);s=s[:start]+"names=['breakthrough-prefix-tick-isolated-20261020']"+s[end:];exec(compile(s,str(r/'collect-bound-audit-cycle.py'),'exec'),{'__file__':str(r/'collect-bound-audit-cycle.py')})
