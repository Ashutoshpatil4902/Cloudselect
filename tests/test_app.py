import pytest

from app import app
from dss.data import DEFAULT_WEIGHTS


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    return app.test_client()


def valid_form(**overrides):
    form = {f"weight_{key}": str(value) for key, value in DEFAULT_WEIGHTS.items()}
    form.update({"max_budget": "40", "required_certification": "", "workload_notes": "test"})
    form.update(overrides)
    return form


@pytest.mark.parametrize("path", ["/", "/compare", "/evaluation", "/scenario/A", "/scenario/b"])
def test_pages_render(client, path):
    assert client.get(path).status_code == 200


def test_results_ranks_with_valid_input(client):
    response = client.post("/results", data=valid_form())
    assert response.status_code == 200
    assert b"Best match for these weights" in response.data


def test_invalid_weights_keep_user_input(client):
    response = client.post("/results", data=valid_form(weight_cost="50", workload_notes="keep me"))
    assert response.status_code == 400
    assert b"Weights must sum to 100%" in response.data
    assert b"keep me" in response.data


def test_non_numeric_weight_gives_clear_error(client):
    response = client.post("/results", data=valid_form(weight_ease="abc"))
    assert response.status_code == 400
    assert b"must be a number" in response.data


def test_no_eligible_alternative_message(client):
    response = client.post("/results", data=valid_form(max_budget="5"))
    assert b"No alternative meets your hard rules" in response.data


def test_unknown_page_is_404(client):
    assert client.get("/nope").status_code == 404
