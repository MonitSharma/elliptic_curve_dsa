"""Read server capacity and jobs without modifying other projects."""
import datetime
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess

memory = {}
for line in Path("/proc/meminfo").read_text().splitlines():
    key, rest = line.split(":", 1)
    if key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree"):
        memory[key + "_bytes"] = int(rest.split()[0]) * 1024
result = {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "hostname": socket.gethostname(), "cpu_affinity_count": len(os.sched_getaffinity(0)),
          "load_average": os.getloadavg(), "memory": memory,
          "disk_free_bytes": shutil.disk_usage("/home/hclau/ecdsa_research").free,
          "schedulers": {name: shutil.which(name) for name in ("squeue", "qstat")},
          "active_processes": subprocess.check_output(
              ["ps", "-eo", "pid,pcpu,pmem,comm", "--sort=-pcpu"], text=True).splitlines()[:15],
          "ecdsa_workspace": "/home/hclau/ecdsa_research",
          "chemistry_repository_modified": False}
print(json.dumps(result, indent=2))
