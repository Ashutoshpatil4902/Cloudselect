# CloudSelect

A model-driven decision support system that compares three cloud virtual machines for a small web application. The app checks mandatory budget and security rules, scores eligible alternatives with user-defined weights, ranks them, and explains the result.

This is a student DSS prototype. Rankings are only as trustworthy as the ratings, weights, and assumptions shown in the interface.

## What is included

- Three alternatives: AWS EC2 `t3.medium`, Azure VM `B2s`, GCP Compute Engine `e2-medium`
- Five criteria: estimated cost, security fit, scalability, performance, ease of management
- Hard constraints: maximum monthly budget and optional mandatory certification
- Flask web UI: requirements form, comparison table, ranked results, scenario evaluation
- Unit tests for weights, eligibility, scoring, and the three discussion-guide scenarios

Dataset values are labelled **illustrative**. Replace them with dated provider quotes before a final report.

## Mac setup

Command Line Tools are required before Python, `git`, or Homebrew will work on this Mac.

### 1. Install Xcode Command Line Tools

In Terminal:

```bash
xcode-select --install
```

Click **Install** in the macOS dialog and wait until it finishes. Confirm with:

```bash
xcode-select -p
git --version
python3 --version
```

You should see a path such as `/Library/Developer/CommandLineTools` and a Git/Python version.

### 2. (Optional) Install Homebrew and a current Python

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
brew install python
```

Apple Silicon Macs use `/opt/homebrew`. Intel Macs typically use `/usr/local`.

### 3. Open the project

```bash
cd ~/cloudselect
```

If Git is now available and this folder is not yet a repository:

```bash
git init
git add .
git commit -m "Add CloudSelect DSS prototype"
```

### 4. Create a virtual environment and install packages

```bash
cd ~/cloudselect
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run tests

```bash
pytest
```

### 6. Start the web app

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

- Requirements: set budget, certification, and weights
- Comparison: inspect 1-5 ratings and evidence notes
- Results: eligibility, weighted scores, explanations, sensitivity table
- Evaluation: scenarios A (cost), B (security), C (growth)

Stop the server with `Ctrl+C`. Leave the virtual environment with `deactivate`.

## Decision model

1. User sets weights that sum to 100% and optional hard constraints.
2. Alternatives that fail budget or a required certification are marked ineligible and not recommended.
3. Eligible alternatives receive

   `S(j) = Σ weight(i) × rating(i, j)`

   where weights are fractions (30% = 0.30) and ratings are 1-5.
4. The dashboard shows the total, each criterion contribution, failed rules, and assumptions.

## Project layout

```text
cloudselect/
  app.py
  requirements.txt
  data/cloud_alternatives.csv
  dss/eligibility.py
  dss/scoring.py
  dss/ranking.py
  dss/engine.py
  templates/
  static/
  tests/test_scoring.py
  README.md
```

The scoring engine is separate from the Flask routes so the decision logic can be tested on its own.
