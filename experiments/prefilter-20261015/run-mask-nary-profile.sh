#!/bin/bash
set -u
cd /home/hclau/ecdsa_research/prefilter-20261015
echo $$ > evidence/mask-nary-profile.pid
trap 'echo $? > evidence/mask-nary-profile.exit' EXIT
free -m > evidence/mask-nary-profile.resources
prlimit --as=1073741824 -- python3 profile-mask-nary.py > evidence/mask-nary-profile.log 2>&1
