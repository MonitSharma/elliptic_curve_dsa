"""Observe payload and rotation membership directly; emit the same raw circuit."""
import hashlib, json, re, subprocess
from pathlib import Path

r = Path(__file__).resolve().parent
t = r / 'observer'
ws = r.parent
base = '90e777ea8242faa0acb2462c5cb5be7c318a2d64'
assert not t.exists()
subprocess.run(['git', '-C', str(ws/'toffoli'), 'worktree', 'add', '--detach', str(t), base], check=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
paths = subprocess.check_output(['git', '-C', str(t), 'ls-files']).decode().splitlines()
protected = {name: sha(t/name) for name in paths if not name.startswith('src/point_add/')}
assert len(protected) == 17
old = ws/'breakthrough-cap-cost-20261020/observer'
for name in ['builder.rs', 'record.rs', 'break_profile.rs', 'mod.rs']:
    (t/'src/point_add'/name).write_bytes((old/'src/point_add'/name).read_bytes())

def closing_brace(s, begin):
    """Rust lexical brace scan, excluding strings/chars and nested comments."""
    i, depth = begin, 0
    while i < len(s):
        if s.startswith(b'//', i):
            end = s.find(b'\n', i); i = len(s) if end < 0 else end+1; continue
        if s.startswith(b'/*', i):
            nesting = 1; i += 2
            while nesting:
                if s.startswith(b'/*', i): nesting += 1; i += 2
                elif s.startswith(b'*/', i): nesting -= 1; i += 2
                else: i += 1
                assert i <= len(s)
            continue
        raw = re.match(rb'(?:br|r)(#*)"', s[i:])
        if raw:
            end = s.find(b'"'+raw[1], i+raw.end()); assert end >= 0
            i = end+1+len(raw[1]); continue
        if s[i:i+1] == b'"':
            i += 1
            while s[i:i+1] != b'"':
                i += 2 if s[i:i+1] == b'\\' else 1
            i += 1; continue
        char = re.match(rb"'(?:[^'\\\r\n]|\\.)'", s[i:])
        if char: i += char.end(); continue
        if s[i:i+1] == b'{': depth += 1
        if s[i:i+1] == b'}':
            depth -= 1
            if depth == 0: return i
        i += 1
    raise AssertionError('Unclosed body')

wrapped = []
def wrap(file, name, domain, builder='c'):
    p = t/'src/point_add'/file
    raw = p.read_bytes()
    hits = list(re.finditer(rb'\bfn '+name.encode()+rb'\s*\(', raw)); assert len(hits) == 1, (file, name, len(hits))
    begin = raw.index(b'{', hits[0].end()); end = closing_brace(raw, begin)
    body = raw[begin+1:end]
    prefix = f'\nlet break_domain_start = {builder}.op_count();\nlet break_domain_result = (|| {{\n'.encode()
    suffix = (f'\n}})();\neprintln!("BREAK_DOMAIN\\t{{}}\\t{domain}\\t{file}:{name}\\t{{}}\\t{{}}", '
              f'{builder}.current_phase(), break_domain_start, {builder}.op_count());\nbreak_domain_result\n').encode()
    p.write_bytes(raw[:begin+1]+prefix+body+suffix+raw[end:])
    wrapped.append({'file':file,'function':name,'domain':domain})

for name in ['pay_fwd_tick','pay_rev_tick','n2_pay_fwd_last','n2_pay_rev_last','cmod_barrel','merged_fwd','merged_rev']:
    wrap('leapfrog.rs', name, 'payload')
wrap('leapfrog.rs', 'rot4', 'rotation')
for name in ['fwd_tick','rev_tick']:
    wrap('y15_onefold.rs', name, 'payload')
for name in ['add_halve','double_add','mod_double','mod_halve']:
    wrap('pingpong.rs', name, 'payload', 'circ')
wrap('modular.rs', 'mod_addsub', 'payload', 'circ')
assert all(sha(t/name) == h for name,h in protected.items())
freeze = {'base':base, 'scope':'Direct function-membership observation of unchanged raw arithmetic; not a candidate.',
          'expected_native_raw_sha256':'13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b',
          'protected_files':protected, 'wrappers':wrapped,
          'source_files':{p.relative_to(t).as_posix():sha(p) for p in sorted((t/'src/point_add').rglob('*')) if p.is_file()}}
(r/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
