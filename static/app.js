// Weight allocator: keeps sliders, number inputs, and the stacked bar in sync.
(function () {
  const form = document.getElementById("requirements-form");
  if (!form) return;

  const numbers = Array.from(form.querySelectorAll(".weight-input"));
  const ranges = Array.from(form.querySelectorAll(".weight-range"));
  const segs = Array.from(document.querySelectorAll("#weight-stack .seg[data-key]"));
  const sumEl = document.getElementById("weight-sum");
  const totalEl = sumEl.closest(".total");
  const statusEl = document.getElementById("weight-status");
  const submit = document.getElementById("submit");
  const balance = document.getElementById("balance");
  const scenarioField = document.getElementById("scenario-field");
  const presets = Array.from(document.querySelectorAll(".preset"));
  let scenarios = {};
  try {
    scenarios = JSON.parse(document.getElementById("scenario-data").textContent);
  } catch (_) { /* presets simply won't fill */ }

  const byKey = (list, key) => list.find((el) => el.dataset.key === key);
  const value = (input) => {
    const n = Number(input.value);
    return Number.isFinite(n) && n > 0 ? n : 0;
  };
  const total = () => numbers.reduce((sum, input) => sum + value(input), 0);

  function render() {
    const sum = Math.round(total() * 100) / 100;
    const scale = Math.max(sum, 100);
    numbers.forEach((input) => {
      const key = input.dataset.key;
      const v = value(input);
      byKey(segs, key).style.width = (v / scale) * 100 + "%";
      const range = byKey(ranges, key);
      range.style.setProperty("--fill", Math.min(v, 100) + "%");
    });
    sumEl.textContent = String(sum);
    const ok = Math.abs(sum - 100) < 0.01;
    totalEl.classList.toggle("is-off", !ok);
    statusEl.classList.toggle("is-off", !ok);
    submit.disabled = !ok;
    balance.hidden = ok || sum === 0;
    if (ok) {
      statusEl.textContent = "Weights add up to 100%. Ready to rank.";
    } else if (sum < 100) {
      statusEl.textContent = `${Math.round((100 - sum) * 100) / 100}% left to allocate.`;
    } else {
      statusEl.textContent = `${Math.round((sum - 100) * 100) / 100}% over. Lower a weight or scale to 100%.`;
    }
  }

  function markCustom() {
    scenarioField.value = "custom";
    presets.forEach((p) => p.classList.remove("is-active"));
  }

  numbers.forEach((input) => {
    input.addEventListener("input", () => {
      byKey(ranges, input.dataset.key).value = value(input);
      markCustom();
      render();
    });
  });
  ranges.forEach((range) => {
    range.addEventListener("input", () => {
      byKey(numbers, range.dataset.key).value = range.value;
      markCustom();
      render();
    });
  });

  // Scale every weight proportionally so the total is exactly 100.
  balance.addEventListener("click", () => {
    const sum = total();
    if (!sum) return;
    const scaled = numbers.map((input) => Math.floor((value(input) / sum) * 100));
    let remainder = 100 - scaled.reduce((a, b) => a + b, 0);
    const order = numbers
      .map((input, i) => ({ i, frac: (value(input) / sum) * 100 - scaled[i] }))
      .sort((a, b) => b.frac - a.frac);
    for (let k = 0; remainder > 0; k++, remainder--) scaled[order[k % order.length].i] += 1;
    numbers.forEach((input, i) => {
      input.value = scaled[i];
      byKey(ranges, input.dataset.key).value = scaled[i];
    });
    markCustom();
    render();
  });

  presets.forEach((button) => {
    button.addEventListener("click", () => {
      const spec = scenarios[button.dataset.preset];
      if (!spec) return;
      const f = spec.form;
      form.elements.max_budget.value = f.max_budget;
      form.elements.workload_notes.value = f.workload_notes;
      form.querySelectorAll('input[name="required_certification"]').forEach((radio) => {
        radio.checked = radio.value === (f.required_certification || "");
      });
      numbers.forEach((input) => {
        const v = f["weight_" + input.dataset.key];
        input.value = v;
        byKey(ranges, input.dataset.key).value = v;
      });
      scenarioField.value = button.dataset.preset;
      presets.forEach((p) => p.classList.toggle("is-active", p === button));
      render();
    });
  });

  form.addEventListener("submit", (event) => {
    if (Math.abs(total() - 100) >= 0.01) {
      event.preventDefault();
      statusEl.focus?.();
    }
  });

  render();
})();
