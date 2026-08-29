from pathlib import Path
import json
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory, abort
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = json.loads((BASE / "data" / "cases.json").read_text(encoding="utf-8"))
EVIDENCE_ROOT = BASE / "evidence"

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html", cases=DATA, active="dashboard")

@app.get("/cases")
def cases():
    return render_template("cases.html", cases=DATA, active="cases")

@app.get("/case/<case_id>")
def case_detail(case_id):
    case = next((c for c in DATA if c["id"] == case_id), None)
    if not case:
        return "Case not found", 404

    folder = EVIDENCE_ROOT / f"Case{case_id[1:]}_Evidence"
    evidence_files = []
    if folder.exists():
        for f in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
            if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
                evidence_files.append({
                    "name": f.name,
                    "url": url_for("evidence_file", case_id=case_id, filename=f.name)
                })
    return render_template("case.html", case=case, evidence_files=evidence_files, active="cases")

@app.get("/evidence/<case_id>/<path:filename>")
def evidence_file(case_id, filename):
    folder = EVIDENCE_ROOT / f"Case{case_id[1:]}_Evidence"
    if not folder.exists():
        abort(404)
    return send_from_directory(folder, filename)

@app.get("/api/cases")
def api_cases():
    return jsonify(DATA)

@app.post("/api/prompt")
def api_prompt():
    case_id = request.json.get("case_id")
    case = next((c for c in DATA if c["id"] == case_id), None)
    if not case:
        return jsonify({"error":"Unknown case"}), 404
    prompt = f"""You are NetSage AI, an AI-assisted network troubleshooting helper.
Analyze only the evidence provided. Do not invent evidence.

CASE: {case['id']} — {case['fault']}
SYMPTOM:
{case['symptom']}

EVIDENCE:
- """ + "\n- ".join(case["evidence"]) + f"""

Return:
1. Root Cause
2. Confidence
3. Evidence
4. Next Command
5. Fix Steps
6. OSI Layer
7. Alternative Diagnosis
"""
    return jsonify({"prompt": prompt})

@app.post("/api/check")
def api_check():
    # Demo-friendly deterministic comparison against the curated case rule.
    case_id = request.json.get("case_id")
    case = next((c for c in DATA if c["id"] == case_id), None)
    if not case:
        return jsonify({"error":"Unknown case"}), 404
    return jsonify({"case_id": case["id"], "finding": case["python"], "status":"Rule-based check complete"})

if __name__ == "__main__":
    app.run(debug=True)
