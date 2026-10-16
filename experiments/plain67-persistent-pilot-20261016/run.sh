#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/plain67-persistent-pilot-20261016
echo $$ > run.pid
trap 'rc=$?; echo "$rc" > run.exit' EXIT
hostname
free -h
ps -eo pid,pcpu,rss,args --sort=-pcpu | head -20 || true
timeout --signal=TERM --kill-after=20 900 python3 -u run.py
