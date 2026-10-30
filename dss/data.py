from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "cloud_alternatives.csv"

CRITERIA = (
    ("cost", "Estimated cost"),
    ("security", "Security fit"),
    ("scalability", "Scalability"),
    ("performance", "Performance"),
    ("ease", "Ease of management"),
)

DEFAULT_WEIGHTS = {
    "cost": 30,
    "security": 25,
    "scalability": 20,
    "performance": 15,
    "ease": 10,
}

SCORE_FIELDS = {
    "cost": "cost_score",
    "security": "security_score",
    "scalability": "scalability_score",
    "performance": "performance_score",
    "ease": "ease_score",
}

NOTE_FIELDS = {
    "cost": "cost_notes",
    "security": "security_notes",
    "scalability": "scalability_notes",
    "performance": "performance_notes",
    "ease": "ease_notes",
}


def load_alternatives(path: Path | None = None) -> list[dict]:
    csv_path = path or DATA_FILE
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    alternatives = []
    for row in rows:
        alternative = dict(row)
        alternative["monthly_cost_usd"] = float(row["monthly_cost_usd"])
        for key in SCORE_FIELDS.values():
            alternative[key] = int(row[key])
        alternative["certifications"] = [
            item.strip() for item in row["certifications"].split(";") if item.strip()
        ]
        alternatives.append(alternative)
    return alternatives
