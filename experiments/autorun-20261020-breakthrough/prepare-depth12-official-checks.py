from pathlib import Path
import ast,shutil
a=Path(__file__).parent;old=a.parent/'breakthrough-groups-context-final-20261020';r=a.parent/'breakthrough-depth12-final-20261020';shutil.copyfile(old/'wait-official.py',r/'wait-official.py');s=(old/'verify-official-source.py').read_text().replace("747453-b['rounded_mean_executed_toffoli']","747226-b['rounded_mean_executed_toffoli']");ast.parse(s);(r/'verify-official-source.py').write_text(s);print(r)
