from __future__ import annotations

from dss.data import CRITERIA, NOTE_FIELDS, SCORE_FIELDS


def normalise_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(float(weights[key]) for key, _ in CRITERIA)
    if abs(total - 100) > 0.01:
        raise ValueError(f"Weights must sum to 100%. Received {total:.2f}%.")
    for key, _ in CRITERIA:
        value = float(weights[key])
        if value < 0:
            raise ValueError("Weights must be non-negative.")
    return {key: float(weights[key]) / 100.0 for key, _ in CRITERIA}


def score_alternative(alternative: dict, weight_fractions: dict[str, float]) -> dict:
    contributions = []
    total = 0.0
    for key, label in CRITERIA:
        rating = int(alternative[SCORE_FIELDS[key]])
        if rating < 1 or rating > 5:
            raise ValueError(f"{label} rating must be between 1 and 5.")
        contribution = weight_fractions[key] * rating
        total += contribution
        contributions.append(
            {
                "key": key,
                "label": label,
                "weight_percent": round(weight_fractions[key] * 100, 2),
                "rating": rating,
                "contribution": round(contribution, 4),
                "notes": alternative[NOTE_FIELDS[key]],
            }
        )
    return {
        "total": round(total, 4),
        "contributions": contributions,
    }
