from __future__ import annotations

from flask import Flask, flash, redirect, render_template, request, url_for

from dss.data import CRITERIA, DEFAULT_WEIGHTS, load_alternatives
from dss.engine import run_decision
from dss.scenarios import SCENARIOS, run_all_scenarios, sensitivity_table

app = Flask(__name__)
app.secret_key = "cloudselect-local-dev"


def form_from_request() -> dict:
    if request.method == "POST":
        return request.form.to_dict()
    return {
        "max_budget": request.args.get("max_budget", "40"),
        "required_certification": request.args.get("required_certification", ""),
        "weight_cost": request.args.get("weight_cost", str(DEFAULT_WEIGHTS["cost"])),
        "weight_security": request.args.get("weight_security", str(DEFAULT_WEIGHTS["security"])),
        "weight_scalability": request.args.get("weight_scalability", str(DEFAULT_WEIGHTS["scalability"])),
        "weight_performance": request.args.get("weight_performance", str(DEFAULT_WEIGHTS["performance"])),
        "weight_ease": request.args.get("weight_ease", str(DEFAULT_WEIGHTS["ease"])),
        "workload_notes": request.args.get(
            "workload_notes",
            "Small web application: 2 vCPU, 4 GiB RAM, 100 GB storage, ~200 GB monthly traffic.",
        ),
        "scenario": request.args.get("scenario", "custom"),
    }


@app.context_processor
def inject_globals():
    return {
        "criteria": CRITERIA,
        "default_weights": DEFAULT_WEIGHTS,
        "certification_options": ["", "ISO 27001", "SOC 2", "PCI DSS"],
    }


@app.route("/")
def home():
    return render_template("index.html", form=form_from_request(), scenarios=SCENARIOS)


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
        flash(str(error), "error")
        return redirect(url_for("home"))
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
        flash("Unknown evaluation scenario.", "error")
        return redirect(url_for("evaluation"))
    decision = run_decision(spec["form"])
    sensitivity = sensitivity_table(spec["form"])
    return render_template(
        "results.html",
        form=spec["form"],
        decision=decision,
        sensitivity=sensitivity,
        scenario_meta=spec,
    )


@app.route("/evaluation")
def evaluation():
    return render_template("evaluation.html", scenarios=run_all_scenarios())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
