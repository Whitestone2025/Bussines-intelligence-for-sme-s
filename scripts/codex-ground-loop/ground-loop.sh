#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: ground-loop.sh <run-dir>" >&2
  exit 1
fi

RUN_DIR="$1"
PLAN_MD="$RUN_DIR/plan.md"
PRD_JSON="$RUN_DIR/prd.json"
PROGRESS_TXT="$RUN_DIR/progress.txt"
LAST_MESSAGE_TXT="$RUN_DIR/last-message.txt"

if [[ ! -f "$PLAN_MD" ]]; then
  echo "Missing $PLAN_MD" >&2
  exit 1
fi

mkdir -p "$RUN_DIR"
touch "$PROGRESS_TXT"

python3 scripts/codex-ground-loop/build_prd.py "$PLAN_MD" "$PRD_JSON" >/dev/null

python3 - "$PRD_JSON" "$PROGRESS_TXT" "$LAST_MESSAGE_TXT" <<'PY'
import json
import re
import sys
from pathlib import Path

prd_path = Path(sys.argv[1])
progress_path = Path(sys.argv[2])
last_message_path = Path(sys.argv[3])

prd = json.loads(prd_path.read_text(encoding="utf-8"))
stories = prd.get("stories", [])

progress = progress_path.read_text(encoding="utf-8").strip()
progress_tail = progress.splitlines()[-5:] if progress else ["No progress recorded yet."]
completed = set(re.findall(r"Completed story:\s*([A-Z]+\d+)", progress))
blocked = set(re.findall(r"Blocked story:\s*([A-Z]+\d+)", progress))

for story in stories:
    if story["id"] in completed:
        story["status"] = "completed"
    elif story["id"] in blocked:
        story["status"] = "blocked"

prd["stories"] = stories
prd_path.write_text(json.dumps(prd, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
pending = next((story for story in stories if story.get("status") == "pending"), None)

if pending is None:
    message = "<promise>GROUND LOOP COMPLETE</promise>\n"
else:
    lines = [
        f"Next story: {pending['id']} - {pending['title']}",
        f"Goal: {pending['goal']}",
        "Deliverables:",
    ]
    for item in pending.get("deliverables", []):
        lines.append(f"- {item}")
    lines.append("Acceptance:")
    for item in pending.get("acceptance", []):
        lines.append(f"- {item}")
    lines.append("Checks:")
    for item in pending.get("checks", []):
        lines.append(f"- {item}")
    lines.append("Recent progress:")
    for item in progress_tail:
        lines.append(f"- {item}")
    message = "\n".join(lines) + "\n"

last_message_path.write_text(message, encoding="utf-8")
print(message, end="")
PY
