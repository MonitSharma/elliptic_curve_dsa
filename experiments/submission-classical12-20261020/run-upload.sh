#!/usr/bin/env bash
cd /home/hclau/ecdsa_research/submission-classical12-20261020 || exit 1
python3 submit.py --submit > upload.log 2>&1
rc=$?
printf '%s\n' "$rc" > runner.exit
exit "$rc"
