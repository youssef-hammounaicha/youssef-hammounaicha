"""Build the public CW3 terminal log from reviewed, non-confidential reports."""
from __future__ import annotations
import argparse, json, re
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]; STATUS=ROOT/"data/cw3-status.json"; REPORTS=ROOT/"reports"; README=ROOT/"README.md"
START,END="<!-- CW3_TERMINAL_LOG:START -->","<!-- CW3_TERMINAL_LOG:END -->"

def load(path):
    try: return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc: raise SystemExit(f"Invalid JSON: {path}: {exc}")
def check_date(value,label):
    try: return date.fromisoformat(value)
    except Exception: raise SystemExit(f"{label} must use YYYY-MM-DD: {value!r}")
def clean(value,limit=None):
    text=re.sub(r"\s+"," ",str(value or "")).strip()
    return text if not limit or len(text)<=limit else text[:max(1,limit-3)].rstrip()+"..."
def md(value): return clean(value).replace("|","\\|")
def read_reports():
    items=[]; required=["summary","completed_features","bugs_fixed","tests","remaining_difficulties","next_objective","validated_milestones"]
    for path in sorted(REPORTS.glob("*.json")):
        if path.name=="report-template.json": continue
        item=load(path); d=check_date(item.get("date"),f"{path.name}.date")
        missing=[k for k in required if k not in item]
        if missing: raise SystemExit(f"{path.name} missing: {', '.join(missing)}")
        for key in ("completed_features","bugs_fixed","tests","remaining_difficulties","validated_milestones"):
            if not isinstance(item[key],list): raise SystemExit(f"{path.name}.{key} must be an array")
        items.append((d,item))
    return sorted(items,key=lambda pair:pair[0])
def svg(state,history,mode):
    dark=mode=="dark"; bg="#08090B" if dark else "#F4F5F6"; ink="#E8EAED" if dark else "#15171B"; muted="#858B95" if dark else "#626A74"; silver="#B8BEC7"; line="#343941" if dark else "#C8CDD3"
    latest=history[-1][1] if history else None; updated=state.get("last_updated") or (latest.get("date") if latest else "NOT RECORDED"); status=clean(state.get("status") or "IN DEVELOPMENT",22); phase=clean(state.get("phase") or "NOT PUBLISHED",22); summary=clean(latest.get("summary") if latest else "NO PUBLIC REPORTS",48)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="250" viewBox="0 0 960 250" role="img" aria-labelledby="title desc" data-mode="{mode}"><title id="title">CW3 public execution signal</title><desc id="desc">Terminal-style public status for CTRLZ Warehouse 3D.</desc><style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}}.fade{{animation:fade .45s cubic-bezier(.23,1,.32,1) both}}.pulse{{animation:pulse 2.4s ease-in-out infinite}}.scan{{animation:scan 5s ease-in-out infinite}}@keyframes fade{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:translateY(0)}}}}@keyframes pulse{{50%{{opacity:.32;transform:scale(.72)}}}}@keyframes scan{{50%{{opacity:.25;transform:translateX(26px)}}}}@media(prefers-reduced-motion:reduce){{.fade,.pulse,.scan{{animation:none}}}}</style><rect width="960" height="250" rx="12" fill="{bg}"/><rect x="1" y="1" width="958" height="248" rx="12" fill="none" stroke="{line}"/><path d="M0 42H960M640 42V250" stroke="{line}"/><circle cx="22" cy="21" r="4" fill="{silver}"/><text x="38" y="26" font-size="13" letter-spacing="2" fill="{muted}">CW3 / PUBLIC EXECUTION LOG</text><text x="930" y="26" text-anchor="end" font-size="11" fill="{muted}">STATUS: {escape(status)}</text><g class="fade"><text x="28" y="78" font-size="12" letter-spacing="2" fill="{muted}">$ phase --current</text><text x="28" y="112" font-size="24" font-weight="700" fill="{ink}">{escape(phase)}</text><text x="28" y="146" font-size="12" fill="{muted}">last update / {escape(clean(updated,16))}</text><path d="M28 178H590" stroke="{line}"/><path class="scan" d="M28 178H180" stroke="{silver}" stroke-width="2"/></g><g class="fade"><text x="676" y="78" font-size="12" letter-spacing="2" fill="{muted}">$ report --latest</text><text x="676" y="112" font-size="14" fill="{ink}">{escape(summary)}</text><text x="676" y="150" font-size="12" fill="{muted}">reports / {len(history):02d}</text><text x="676" y="176" font-size="12" fill="{muted}">milestones / {len(state.get("validated_milestones",[])):02d}</text><circle class="pulse" cx="918" cy="178" r="4" fill="{silver}"/></g></svg>'''
def block(state,history):
    latest=history[-1][1] if history else None; updated=state.get("last_updated") or (latest.get("date") if latest else "Not publicly recorded"); summary=latest.get("summary") if latest else "No public daily report has been recorded yet."; next_step=state.get("next_step") or (latest.get("next_objective") if latest else "No public next step recorded."); milestones=", ".join(md(x) for x in state.get("validated_milestones",[])) or "None publicly recorded"; rows="\n".join(f"| {d.isoformat()} | {md(item.get('summary'))} |" for d,item in history[-5:]) or "| - | No public report recorded yet. |"
    return f'''{START}
### CW3 / EXECUTION LOG

```text
$ cw3 status
STATUS   {clean(state.get("status") or "IN DEVELOPMENT")}
PHASE    {clean(state.get("phase") or "NOT PUBLISHED")}
UPDATED  {clean(updated)}
ACCESS   PRIVATE / PUBLIC STATUS ONLY
```

**Latest public change:** {md(summary)}<br>
**Next public objective:** {md(next_step)}<br>
**Validated milestones:** {milestones}

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/cw3-terminal-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/cw3-terminal-light.svg"><img src="assets/cw3-terminal-light.svg" width="100%" alt="CW3 public execution signal"></picture>

| Date | Public report |
| --- | --- |
{rows}
{END}'''
def build():
    state=load(STATUS); history=read_reports()
    for mode in ("dark","light"): (ROOT/f"assets/cw3-terminal-{mode}.svg").write_text(svg(state,history,mode),encoding="utf-8",newline="\n")
    text=README.read_text(encoding="utf-8-sig"); pattern=re.compile(re.escape(START)+r".*?"+re.escape(END),re.S)
    if not pattern.search(text): raise SystemExit("README terminal markers not found")
    README.write_text(pattern.sub(block(state,history),text,1),encoding="utf-8",newline="\n"); print(f"Built terminal profile: {len(history)} public report(s)")
def new_report(value):
    d=check_date(value,"date"); path=REPORTS/f"{d.isoformat()}.json"
    if path.exists(): raise SystemExit(f"Report already exists: {path.name}")
    path.write_text(json.dumps({"date":d.isoformat(),"summary":"","completed_features":[],"bugs_fixed":[],"tests":[],"remaining_difficulties":[],"next_objective":"","validated_milestones":[]},indent=2)+"\n",encoding="utf-8"); print(path.relative_to(ROOT))
parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command",required=True); p=sub.add_parser("new"); p.add_argument("--date",required=True); sub.add_parser("build"); args=parser.parse_args(); new_report(args.date) if args.command=="new" else build()
