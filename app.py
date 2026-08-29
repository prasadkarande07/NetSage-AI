from pathlib import Path
import json
from flask import Flask, render_template, request, jsonify

BASE = Path(__file__).resolve().parent
DATA = json.loads((BASE / "data" / "cases.json").read_text(encoding="utf-8"))

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
    return render_template("case.html", case=case, active="cases")

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
