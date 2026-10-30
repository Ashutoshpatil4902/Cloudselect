from __future__ import annotations

from dss.engine import run_decision

SCENARIOS = {
    "A": {
        "label": "A. Cost-sensitive startup",
        "priority": "Cost and budget fit",
        "form": {
            "scenario": "A",
            "max_budget": "32",
            "required_certification": "",
            "weight_cost": "45",
            "weight_security": "15",
            "weight_scalability": "15",
            "weight_performance": "15",
            "weight_ease": "10",
            "workload_notes": "Early-stage team hosting a small web app with a hard monthly cap.",
        },
    },
    "B": {
        "label": "B. Security-sensitive workload",
        "priority": "Mandatory security needs",
        "form": {
            "scenario": "B",
            "max_budget": "50",
            "required_certification": "PCI DSS",
            "weight_cost": "15",
            "weight_security": "40",
            "weight_scalability": "15",
            "weight_performance": "15",
            "weight_ease": "15",
            "workload_notes": "Payment-related workload that must show PCI DSS in the recorded controls.",
        },
    },
    "C": {
        "label": "C. Rapidly growing application",
        "priority": "Scalability and performance",
        "form": {
            "scenario": "C",
            "max_budget": "50",
            "required_certification": "",
            "weight_cost": "10",
            "weight_security": "15",
            "weight_scalability": "35",
            "weight_performance": "30",
            "weight_ease": "10",
            "workload_notes": "Traffic may grow quickly; scalability and performance dominate the weights.",
        },
    },
}


def run_all_scenarios() -> list[dict]:
    output = []
    for key, spec in SCENARIOS.items():
        decision = run_decision(spec["form"])
        output.append({"key": key, **spec, "decision": decision})
    return output


def sensitivity_table(base_form: dict) -> list[dict]:
    """Vary cost weight and renormalise the remaining weights proportionally."""
    other_keys = ["security", "scalability", "performance", "ease"]
    other_total = sum(float(base_form.get(f"weight_{key}", 0)) for key in other_keys)
    base_decision = run_decision(base_form)
    base_id = base_decision["winner"]["id"] if base_decision["winner"] else None

    rows = []
    for cost_weight in (20, 30, 40, 50):
        form = dict(base_form)
        form["weight_cost"] = str(cost_weight)
        remaining = 100 - cost_weight
        if other_total <= 0:
            share = remaining / len(other_keys)
            for key in other_keys:
                form[f"weight_{key}"] = str(share)
        else:
            for key in other_keys:
                original = float(base_form.get(f"weight_{key}", 0))
                form[f"weight_{key}"] = str(remaining * original / other_total)
        decision = run_decision(form)
        winner = decision["winner"]
        top_id = winner["id"] if winner else None
        rows.append(
            {
                "cost_weight": cost_weight,
                "top_id": top_id,
                "top_name": winner["name"] if winner else "No eligible alternative",
                "top_score": winner["total"] if winner else None,
                "changed_from_base": top_id != base_id,
            }
        )
    return rows
