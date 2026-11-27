# CloudSelect

A model-driven decision support system (DSS) that compares three cloud virtual machines for a small web application. It checks hard budget and security rules, scores the eligible alternatives with weights you choose, ranks them, and explains every number.

This is a student DSS prototype. Rankings are only as trustworthy as the ratings, weights, and assumptions shown in the interface.

## Features

- **Three alternatives:** AWS EC2 `t3.medium`, Azure VM `B2s`, GCP Compute Engine `e2-medium`
- **Five criteria:** estimated cost, security fit, scalability, performance, ease of management
- **Hard rules:** maximum monthly budget and an optional required certification (ISO 27001, SOC 2, PCI DSS)
- **Weight allocator:** sliders and a live stacked bar that must total 100%, with a one-click “Scale to 100%”
- **Results:** recommended option, stacked score bars showing each criterion’s contribution, per-criterion evidence, a cost-weight sensitivity check, and the model’s assumptions
- **Scenarios:** three preset evaluation cases (cost-sensitive, security-sensitive, fast-growing) that can also pre-fill the form
- Light and dark mode, responsive down to phone width, keyboard accessible
- Unit tests for the decision engine and the web routes

Dataset values are labelled **illustrative**. Replace them with dated provider quotes in `data/cloud_alternatives.csv` before a final report.

## Run it from the terminal (macOS)

You need Python 3.9 or newer. Check with:

```bash
python3 --version
```

If that fails, install the Xcode Command Line Tools first (`xcode-select --install`).

### 1. Get the code

```bash
git clone https://github.com/Ashutoshpatil4902/cloudselect.git
cd cloudselect
```

(If you already have the folder, just `cd ~/cloudselect`.)

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the tests

```bash
pytest
```

### 4. Start the app

```bash
python app.py
```

Open <http://127.0.0.1:5000>.

> **Port 5000 busy?** On macOS the AirPlay Receiver often uses port 5000. Start on another port instead:
>
> ```bash
> PORT=5001 python app.py
> ```
>
> then open <http://127.0.0.1:5001>.

Stop the server with `Ctrl+C`. Leave the virtual environment with `deactivate`.

### Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `5000` | Port for `python app.py` |
| `HOST` | `127.0.0.1` | Interface to bind |
| `FLASK_DEBUG` | `1` | Set to `0` to turn off the debugger |
| `CLOUDSELECT_SECRET_KEY` | dev value | Set a real secret anywhere other than your own machine |

For a production-style server:

```bash
gunicorn -w 2 -b 127.0.0.1:8000 app:app
```

## Pages

- **Requirements** (`/`): workload, budget, certification, weights, scenario presets
- **Providers** (`/compare`): 1–5 ratings and evidence notes for each alternative
- **Scenarios** (`/evaluation`): scenarios A (cost), B (security), C (growth)
- **Results** (`/results`, `/scenario/<A|B|C>`): ranking, explanations, sensitivity, assumptions

## Decision model

1. The user sets weights that total 100% and optional hard rules.
2. Alternatives that exceed the budget or lack the required certification are marked ineligible and are never recommended.
3. Eligible alternatives receive

   `S(j) = Σ weight(i) × rating(i, j)`

   where weights are fractions (30% = 0.30) and ratings are 1–5, so scores range from 1 to 5.
4. The results page shows the total, each criterion’s contribution, failed rules, and assumptions.
5. A sensitivity check reruns the model with the cost weight at 20/30/40/50%, rescaling the other weights proportionally, and flags any change of winner.

## Project layout

```text
cloudselect/
  app.py                     Flask routes
  requirements.txt
  data/cloud_alternatives.csv
  dss/
    data.py                  criteria, default weights, CSV loader
    eligibility.py           hard-rule checks
    scoring.py               weight validation and weighted sum
    ranking.py               ordering of eligible / ineligible results
    engine.py                input parsing and the full decision run
    scenarios.py             preset scenarios and sensitivity table
  templates/                 Jinja pages
  static/                    styles.css, app.js (weight allocator)
  tests/
    test_scoring.py          decision engine tests
    test_app.py              route and validation tests
```

The scoring engine is separate from the Flask routes, so the decision logic can be tested on its own.
