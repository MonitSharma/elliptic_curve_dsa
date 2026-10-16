"""Normalize this prepared patch without staging the other chat's working notes."""
from pathlib import Path
import difflib,subprocess
r=Path(__file__).resolve().parents[2];d=Path(__file__).resolve().parent
base=subprocess.check_output(['git','show','HEAD:README.md'],cwd=r).decode()
pairs={'The06:09':'The 06:09','records22.5million':'records 22.5 million','at06:08':'at 06:08',
    'confirms753,721':'confirms 753,721','source`b5adb653`':'source `b5adb653`','roughly753,670':'roughly 753,670',
    'current4b failures':'current 4b failures','isQ677':'is Q677','isQ676':'is Q676','remainsqueue':'remains queue',
    'measured19.609-hour':'measured 19.609-hour','at48threads':'at 48 threads','the753,721':'the 753,721',
    'the753,745':'the 753,745'}
for path in [r/'README.md',d/'README-owned-refresh.md']:
    text=path.read_text(encoding='utf-8')
    for old,new in pairs.items():text=text.replace(old,new)
    path.write_bytes(text.encode('utf-8'))
owned=(d/'README-owned-refresh.md').read_text(encoding='utf-8')
patch=''.join(difflib.unified_diff(base.splitlines(True),owned.splitlines(True),fromfile='a/README.md',tofile='b/README.md'))
(d/'README-owned-refresh.patch').write_bytes(patch.encode('utf-8'))
assert '[Upload receipt and fresh verification]' in (r/'README.md').read_text(encoding='utf-8')
print('Prepared LF patch against HEAD; other-chat working note/link preserved')
