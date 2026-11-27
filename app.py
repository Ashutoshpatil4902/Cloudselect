from __future__ import annotations

import os

from flask import Flask, redirect, render_template, request, url_for

from dss.data import CRITERIA, DEFAULT_WEIGHTS, load_alternatives
from dss.engine import run_decision
from dss.scenarios import SCENARIOS, run_all_scenarios, sensitivity_table

DEFAULT_WORKLOAD = (
    "Small web application: 2 vCPU, 4 GiB RAM, 100 GB storage, ~200 GB monthly traffic."
)
CERTIFICATION_OPTIONS = ["", "ISO 27001", "SOC 2", "PCI DSS"]

app = Flask(__name__)
# Set CLOUDSELECT_SECRET_KEY in any shared or deployed environment.
app.secret_key = os.environ.get("CLOUDSELECT_SECRET_KEY", "cloudselect-local-dev")


def form_from_request() -> dict:
    if request.method == "POST":
        return request.form.to_dict()
    args = request.args
    form = {
        "max_budget": args.get("max_budget", "40"),
        "required_certification": args.get("required_certification", ""),
        "workload_notes": args.get("workload_notes", DEFAULT_WORKLOAD),
        "scenario": args.get("scenario", "custom"),
    }
    for key, _ in CRITERIA:
        form[f"weight_{key}"] = args.get(f"weight_{key}", str(DEFAULT_WEIGHTS[key]))
    return form


@app.context_processor
def inject_globals():
    return {
        "criteria": CRITERIA,
        "default_weights": DEFAULT_WEIGHTS,
        "certification_options": CERTIFICATION_OPTIONS,
        "active_page": request.endpoint,
    }


def render_requirements(form: dict, error: str | None = None, status: int = 200):
    return (
        render_template("index.html", form=form, scenarios=SCENARIOS, error=error),
        status,
    )


@app.route("/")
def home():
    return render_requirements(form_from_request())


@app.route("/compare")
def compare():
    return render_template("compare.html", alternatives=load_alternatives())


@app.route("/results", methods=["GET", "POST"])
def results():
    form = form_from_request()
    try:
        decision = run_decision(form)
        sensitivity = sensitivity_table(form)
    except ValueError as error:
        # Re-render the form with the user's input intact instead of losing it.
        return render_requirements(form, error=str(error), status=400)
    return render_template(
        "results.html",
        form=form,
        decision=decision,
        sensitivity=sensitivity,
    )


@app.route("/scenario/<key>")
def scenario(key: str):
    spec = SCENARIOS.get(key.upper())
    if not spec:
        return redirect(url_for("evaluation"))
    return render_template(
        "results.html",
        form=spec["form"],
        decision=run_decision(spec["form"]),
        sensitivity=sensitivity_table(spec["form"]),
        scenario_meta=spec,
    )


@app.route("/evaluation")
def evaluation():
    return render_template("evaluation.html", scenarios=run_all_scenarios())


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "1") == "1",
    )
