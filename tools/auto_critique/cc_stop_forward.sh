#!/bin/bash
# Hook Stop do Claude Code: copia a resposta final e dispara a rodada no Hammerspoon.
# Só age com o laço ligado (arquivo /tmp/loop_on, criado pelo loopStart do Hammerspoon).
[ -f /tmp/loop_on ] || exit 0
input=$(cat)
active=$(printf '%s' "$input" | /usr/bin/python3 -c 'import json,sys; print(json.load(sys.stdin).get("stop_hook_active", False))')
[ "$active" = "True" ] && exit 0
msg=$(printf '%s' "$input" | /usr/bin/python3 -c 'import json,sys; print(json.load(sys.stdin).get("last_assistant_message", ""))')
[ -z "$msg" ] && exit 0
printf '%s' "$msg" > /tmp/cc_last_answer.txt
open -g "hammerspoon://cctodsh"
exit 0
