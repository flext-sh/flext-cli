#!/usr/bin/env python3
<<<<<<< HEAD
from __future__ import annotations

=======
>>>>>>> origin/integration/sweep-20260830
import json
import sys

payload = json.load(sys.stdin)
if not isinstance(payload, dict):
<<<<<<< HEAD
    msg = "hook input must be a JSON object"
    raise TypeError(msg)
response = json.loads("{}")
json.dump(response, sys.stdout, ensure_ascii=False, separators=(",", ":"))
sys.stdout.write("\n")
=======
    raise TypeError('hook input must be a JSON object')
response = json.loads('{}')
json.dump(response, sys.stdout, ensure_ascii=False, separators=(',', ':'))
sys.stdout.write('\n')
>>>>>>> origin/integration/sweep-20260830
