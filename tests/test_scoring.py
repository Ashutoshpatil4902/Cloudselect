from dss.data import load_alternatives
from dss.eligibility import evaluate_eligibility
from dss.engine import run_decision
from dss.scenarios import SCENARIOS, run_all_scenarios
from dss.scoring import normalise_weights, score_alternative


def test_weights_must_sum_to_100():
    fractions = normalise_weights(
        {"cost": 30, "security": 25, "scalability": 20, "performance": 15, "ease": 10}
    )
    assert abs(sum(fractions.values()) - 1) < 1e-9


def test_weights_reject_invalid_total():
    try:
        normalise_weights(
            {"cost": 40, "security": 25, "scalability": 20, "performance": 15, "ease": 10}
        )
    except ValueError as error:
        assert "100%" in str(error)
    else:
        raise AssertionError("Expected invalid weights to fail")


def test_score_stays_on_defined_scale():
    alternative = load_alternatives()[0]
    scored = score_alternative(
        alternative,
        {"cost": 0.3, "security": 0.25, "scalability": 0.2, "performance": 0.15, "ease": 0.1},
    )
    assert 1 <= scored["total"] <= 5


def test_over_budget_is_ineligible():
    alternative = {"monthly_cost_usd": 38.7, "certifications": ["ISO 27001"]}
    result = evaluate_eligibility(alternative, max_budget=32, required_certification=None)
    assert result["eligible"] is False
    assert "exceeds the maximum budget" in result["failures"][0]


def test_missing_certification_is_ineligible():
    alternative = {"monthly_cost_usd": 27.1, "certifications": ["ISO 27001", "SOC 2"]}
    result = evaluate_eligibility(alternative, max_budget=50, required_certification="PCI DSS")
    assert result["eligible"] is False


def test_cost_sensitive_scenario_excludes_azure():
    decision = run_decision(SCENARIOS["A"]["form"])
    azure = next(item for item in decision.results if item["id"] == "azure_b2s")
    assert azure["eligible"] is False
    assert decision.winner["id"] == "gcp_e2_medium"


def test_security_scenario_excludes_gcp():
    decision = run_decision(SCENARIOS["B"]["form"])
    gcp = next(item for item in decision.results if item["id"] == "gcp_e2_medium")
    assert gcp["eligible"] is False
    assert "PCI DSS" in gcp["failures"][0]


def test_growth_scenario_ranks_aws_first():
    decision = run_decision(SCENARIOS["C"]["form"])
    assert decision.winner["id"] == "aws_t3_medium"


def test_all_preset_scenarios_run():
    rows = run_all_scenarios()
    assert [row["key"] for row in rows] == ["A", "B", "C"]
