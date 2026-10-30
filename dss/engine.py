from __future__ import annotations

from dss.data import CRITERIA, DEFAULT_WEIGHTS, load_alternatives
from dss.eligibility import evaluate_eligibility
from dss.ranking import rank_results
from dss.scoring import normalise_weights, score_alternative


def parse_inputs(form: dict) -> dict:
    weights = {}
    for key, _ in CRITERIA:
        raw = form.get(f"weight_{key}", DEFAULT_WEIGHTS[key])
        weights[key] = float(raw)

    budget_raw = str(form.get("max_budget", "")).strip()
    max_budget = float(budget_raw) if budget_raw else None
    if max_budget is not None and max_budget <= 0:
        raise ValueError("Maximum budget must be greater than 0, or left blank.")

    required = str(form.get("required_certification", "")).strip() or None
    scenario = str(form.get("scenario", "custom")).strip() or "custom"
    return {
        "weights": weights,
        "max_budget": max_budget,
        "required_certification": required,
        "scenario": scenario,
        "workload_notes": str(form.get("workload_notes", "")).strip(),
    }


def run_decision(form: dict, alternatives: list[dict] | None = None) -> dict:
    inputs = parse_inputs(form)
    weight_fractions = normalise_weights(inputs["weights"])
    rows = alternatives if alternatives is not None else load_alternatives()

    results = []
    for alternative in rows:
        eligibility = evaluate_eligibility(
            alternative,
            inputs["max_budget"],
            inputs["required_certification"],
        )
        scored = score_alternative(alternative, weight_fractions)
        results.append(
            {
                **alternative,
                "eligible": eligibility["eligible"],
                "failures": eligibility["failures"],
                "total": scored["total"] if eligibility["eligible"] else None,
                "contributions": scored["contributions"],
            }
        )

    ranked = rank_results(results)
    winner = next((item for item in ranked if item["eligible"]), None)
    return {
        "inputs": inputs,
        "weight_fractions": weight_fractions,
        "results": ranked,
        "winner": winner,
        "assumptions": [
            "All 1-5 ratings are suitability scores: higher always means a better fit.",
            "Weights are treated as percentages and converted to fractions (30% = 0.30).",
            "Ineligible alternatives are explained but not recommended.",
            "Dataset values are labelled illustrative until replaced with dated source quotes.",
            "The ranking supports a human decision; it is not a universally best provider.",
        ],
    }
