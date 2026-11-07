"""Build the public CW3 Command Deck from reviewed, non-confidential reports."""
from __future__ import annotations
import argparse, json, re
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data/cw3-status.json"
REPORTS = ROOT / "reports"
README = ROOT / "README.md"
START, END = "<!-- CW3_EXECUTION_DECK:START -->", "<!-- CW3_EXECUTION_DECK:END -->"

def load_json(path: Path):
    try: return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc: raise SystemExit(f"Invalid JSON: {path}: {exc}")

def check_date(value, label):
    try: return date.fromisoformat(value)
    except Exception: raise SystemExit(f"{label} must use YYYY-MM-DD: {value!r}")

def reports():
    items=[]
    for path in sorted(REPORTS.glob("*.json")):
        if path.name == "report-template.json": continue
        item=load_json(path)
        d=check_date(item.get("date"), f"{path.name}.date")
        required=["summary","completed_features","bugs_fixed","tests","remaining_difficulties","next_objective","validated_milestones"]
        missing=[key for key in required if key not in item]
        if missing: raise SystemExit(f"{path.name} missing: {', '.join(missing)}")
        for key in ["completed_features","bugs_fixed","tests","remaining_difficulties","validated_milestones"]:
            if not isinstance(item[key], list): raise SystemExit(f"{path.name}.{key} must be an array")
        items.append((d,item))
    return sorted(items, key=lambda pair: pair[0])

def safe(value): return escape(str(value))
def compact(value, limit):
    """Keep dynamic labels inside the native Command Deck text boxes."""
    if len(str(value or "").strip()) > limit:
        text = re.sub(r"\s+", " ", str(value or "")).strip()
        return text[: max(1, limit - 3)].rstrip() + "..."
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text if len(text) <= limit else text[: max(1, limit - 1)].rstrip() + "â€¦"
def lines(values, empty="None publicly recorded"):
    return "<br/>".join(f"â€¢ {safe(v)}" for v in values) if values else empty

def svg(state, history, mode):
    template_path = ROOT / f"assets/closed-loop-{mode}.svg"
    template = template_path.read_text(encoding="utf-8")
    latest = history[-1][1] if history else None
    updated = state.get("last_updated") or (latest.get("date") if latest else "NOT RECORDED")
    status = compact(state.get("status") or "IN DEVELOPMENT", 14)
    phase = compact(state.get("phase") or "NOT PUBLISHED", 18)
    updated = compact(updated, 10)
    # Keep the original Command Deck geometry and animation system. Only replace
    # text payloads inside its existing labels and panels.
    template = template.replace("Ã‚Â·", " / ").replace("Ã¢â‚¬Â¦", "...")
    template = template.replace("Ã‚Â·", "Â·")
    template = re.sub(r"\d+ CHANNELS [^<]+", f"01 CHANNELS Â· STATUS {safe(status)} Â· {safe(updated)}", template, count=1)
    template = re.sub(r"(?:COMMAND BUS|PHASE / [^<]+)", f"PHASE / {safe(phase)}", template, count=1)
    template = template.replace("Ã‚Â·", " / ").replace("Ã¢â‚¬Â¦", "...")
    return template
    # The code below documents the former standalone renderer; the native
    # template above is intentionally authoritative.
    dark=mode=="dark"; bg="#080A0D" if dark else "#E8ECF0"; panel="#11151A" if dark else "#F7F9FA"; ink="#E8ECF0" if dark else "#15181D"; muted="#7F8A98"; silver="#C4CBD4"; grid="#303740" if dark else "#AEB6C0"
    latest=history[-1][1] if history else None; updated=state.get("last_updated") or (latest.get("date") if latest else "NOT RECORDED")
    phase=state.get("phase") or "NOT PUBLISHED"; status=state.get("status") or "IN DEVELOPMENT"
    milestones=state.get("validated_milestones",[]); planned=state.get("planned_milestones",[])
    rows=[]
    for idx,(d,item) in enumerate(history[-3:],1): rows.append(f'<text x="760" y="{222+idx*24}" font-size="10" fill="{muted}">{safe(item["date"])}  /  {safe(item["summary"][:48])}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360" viewBox="0 0 1200 360" role="img" aria-label="CW3 execution deck" data-mode="{mode}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{bg}"/><stop offset="1" stop-color="{panel}"/></linearGradient><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}.flow{{stroke-dasharray:6 9;animation:flow 7s linear infinite}}.pulse{{animation:pulse 2.4s ease-in-out infinite}}.scan{{animation:scan 5s ease-in-out infinite}}.boot{{animation:boot .8s ease-out both}}@keyframes flow{{to{{stroke-dashoffset:-150}}}}@keyframes pulse{{50%{{opacity:.35;transform:scale(.72)}}}}@keyframes scan{{50%{{opacity:.28;transform:translateX(24px)}}}}@keyframes boot{{from{{opacity:0}}to{{opacity:1}}}}@media(prefers-reduced-motion:reduce){{.flow,.pulse,.scan,.boot{{animation:none}}}}</style>
<rect width="1200" height="360" rx="18" fill="url(#bg)"/><path d="M0 1H1200M0 44H1200" stroke="{silver}" stroke-opacity=".7"/><path d="M720 44V344" stroke="{grid}"/>
<g transform="translate(20 22)"><circle r="4" fill="{silver}" filter="url(#glow)"/><text x="16" y="4" font-size="9" letter-spacing="2" fill="{muted}">CW3 / EXECUTION DECK</text></g><text x="1040" y="26" font-size="9" letter-spacing="2" fill="{muted}">PUBLIC STATUS</text>
<g class="boot"><text x="38" y="82" font-size="11" letter-spacing="2.5" font-weight="700" fill="{silver}">// CTRLZ WAREHOUSE 3D</text><text x="38" y="132" font-size="30" font-weight="900" fill="{ink}">{safe(status)}</text><text x="38" y="160" font-size="12" fill="{muted}">PHASE  /  {safe(phase)}</text><path d="M38 190H650" stroke="{grid}"/><path class="scan" d="M38 190H210" stroke="{silver}" stroke-width="2"/><text x="38" y="218" font-size="10" fill="{muted}">LAST UPDATE  /  {safe(updated)}</text><text x="38" y="248" font-size="10" fill="{muted}">VALIDATED  /  {len(milestones)}     PLANNED  /  {len(planned)}</text><text x="38" y="292" font-size="10" fill="{silver}">NEXT  /  {safe(state.get("next_step","No public next step recorded.")[:74])}</text></g>
<g class="boot"><text x="760" y="82" font-size="11" letter-spacing="2.5" font-weight="700" fill="{silver}">REPORT HISTORY</text><circle class="pulse" cx="760" cy="112" r="4" fill="{silver}" filter="url(#glow)"/><text x="776" y="116" font-size="11" fill="{muted}">{len(history)} PUBLIC REPORTS</text>{''.join(rows) or f'<text x="760" y="168" font-size="10" fill="{muted}">NO PUBLIC REPORTS RECORDED</text>'}<path d="M760 314H1148" stroke="{grid}"/><text x="760" y="338" font-size="10" fill="{muted}">MILESTONE SIGNAL / {len(milestones)} VALIDATED</text></g><rect x="1" y="1" width="1198" height="358" rx="18" fill="none" stroke="{silver}" stroke-opacity=".55"/></svg>'''

def block(state, history):
    latest=history[-1][1] if history else None; updated=state.get("last_updated") or (latest.get("date") if latest else "Not publicly recorded")
    summary=latest.get("summary") if latest else "No public daily report has been recorded yet."
    return f'''{START}
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/cw3-execution-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/cw3-execution-light.svg"><img alt="CW3 execution deck â€” public development status" src="assets/cw3-execution-light.svg" width="100%"></picture>

**Last public update:** {updated}  
**Latest public change:** {summary}
{END}'''

def build():
    state=load_json(STATUS); history=reports();
    for mode in ("dark","light"): (ROOT/f"assets/cw3-execution-{mode}.svg").write_text(svg(state,history,mode),encoding="utf-8")
    text=README.read_text(encoding="utf-8"); replacement=block(state,history)
    pattern=re.compile(re.escape(START)+r".*?"+re.escape(END),re.S)
    if not pattern.search(text): raise SystemExit("README execution markers not found")
    README.write_text(pattern.sub(replacement,text,1),encoding="utf-8")
    print(f"Built CW3 deck: {len(history)} public report(s), updated {len(history) and history[-1][0].isoformat() or 'none'}")

def new_report(value):
    d=check_date(value,"date"); path=REPORTS/f"{d.isoformat()}.json"
    if path.exists(): raise SystemExit(f"Report already exists: {path.name}")
    path.write_text(json.dumps({"date":d.isoformat(),"summary":"","completed_features":[],"bugs_fixed":[],"tests":[],"remaining_difficulties":[],"next_objective":"","validated_milestones":[]},indent=2)+"\n",encoding="utf-8")
    print(path.relative_to(ROOT))

parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command",required=True); pnew=sub.add_parser("new"); pnew.add_argument("--date",required=True); sub.add_parser("build"); args=parser.parse_args()
new_report(args.date) if args.command=="new" else build()
