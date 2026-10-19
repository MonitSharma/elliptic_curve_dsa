"""Read the public challenge workflow associated with this official upload."""
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent
api = 'https://api.github.com/repos/Layr-Labs/ecdsafail-challenge'
for name, endpoint in [('official-workflow.json', '/actions/runs/39323443713'),
                       ('official-workflow-jobs.json', '/actions/runs/39323443713/jobs'),
                       ('official-pull-request.json', '/pulls/814')]:
    with urllib.request.urlopen(api + endpoint, timeout=45) as response:
        data = json.load(response)
    (root / name).write_text(json.dumps(data, indent=2) + '\n')
    if 'jobs' in data:
        for job in data['jobs']:
            print(json.dumps({'job': job['name'], 'status': job['status'],
                'conclusion': job['conclusion'], 'steps': [
                    {k: step.get(k) for k in ('name', 'status', 'conclusion', 'started_at', 'completed_at')}
                    for step in job.get('steps', [])]}, indent=2))
    elif 'head_branch' in data:
        print(json.dumps({k: data.get(k) for k in ('html_url', 'head_branch', 'head_sha', 'status', 'conclusion')}))
    else:
        print(json.dumps({'url': data['html_url'], 'title': data['title'],
            'head': data['head']['ref'], 'state': data['state'], 'merged': data['merged']}))
