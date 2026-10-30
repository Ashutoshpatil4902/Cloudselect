from __future__ import annotations


def evaluate_eligibility(
    alternative: dict,
    max_budget: float | None,
    required_certification: str | None,
) -> dict:
    failures = []

    if max_budget is not None and alternative["monthly_cost_usd"] > max_budget:
        failures.append(
            f"Monthly estimate ${alternative['monthly_cost_usd']:.2f} exceeds the "
            f"maximum budget of ${max_budget:.2f}."
        )

    required = (required_certification or "").strip()
    if required and required not in alternative["certifications"]:
        listed = ", ".join(alternative["certifications"]) or "none recorded"
        failures.append(
            f"Required security condition '{required}' is not in the documented "
            f"certifications ({listed})."
        )

    return {
        "eligible": not failures,
        "failures": failures,
    }
