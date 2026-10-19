"""Explicit immutable-source descriptors for future research jobs."""
import hashlib,json,re
from pathlib import Path

def validated_spec(workspace,record):
    ws=Path(workspace).resolve();name=record['directory']
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]{0,127}',name),'invalid job directory'
    root=(ws/name).resolve();assert root.parent==ws,'job directory escapes workspace'
    kind=record['kind'];slots=record['slots'];assert type(slots) is int
    assert (kind=='compute' and 1<=slots<=64) or (kind=='idle' and slots==0),'invalid reservation'
    for key in ['pidfile','entrypoint','exitfile']:
        value=record[key];assert Path(value).name==value and value not in ['.','..'] and '/' not in value and '\\' not in value
    assert record['pidfile'].endswith('.pid')
    sources=record['source_hashes'];assert record['entrypoint'] in sources and sources
    for rel,expected in sources.items():
        p=(root/rel).resolve();assert p.is_relative_to(root) and re.fullmatch('[0-9a-f]{64}',expected)
        assert p.is_file()
        with p.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        assert actual==expected,'changed registered source: '+str(p)
    return {'root':root,'slots':slots,'pidfile':root/record['pidfile'],'exitfile':root/record['exitfile'],'entrypoint':record['entrypoint'],'kind':kind}

def declared_jobs(workspace):
    ws=Path(workspace);folder=ws/'resource-registry-20261020';result=[]
    for path in sorted(folder.glob('*.json')):
        raw=path.read_bytes();record=json.loads(raw);spec=validated_spec(ws,record)
        result.append((path,spec,hashlib.sha256(raw).hexdigest()))
    return result

def observed_job(spec,live,read_cwd,read_command):
    if not spec['pidfile'].exists():return None
    pid=int(spec['pidfile'].read_text())
    if not live(pid):return None
    cwd=Path(read_cwd(pid)).resolve()
    command=read_command(pid);entry=spec['entrypoint']
    matches=cwd==spec['root'] and (entry in command or str(spec['root']/entry) in command)
    if not matches and spec['exitfile'].exists():return None  # old terminal PID reused
    assert matches,'registered PID cwd/entrypoint mismatch'
    return pid
