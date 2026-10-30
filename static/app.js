function updateWeightTotal() {
  const inputs = document.querySelectorAll(".weight-input");
  const sumEl = document.getElementById("weight-sum");
  if (!inputs.length || !sumEl) return;
  const total = Array.from(inputs).reduce((sum, input) => sum + Number(input.value || 0), 0);
  sumEl.textContent = String(total);
  sumEl.style.color = total === 100 ? "#1f4e79" : "#8a1f1f";
}

document.querySelectorAll(".weight-input").forEach((input) => {
  input.addEventListener("input", updateWeightTotal);
});
updateWeightTotal();

const form = document.getElementById("requirements-form");
if (form) {
  form.addEventListener("submit", (event) => {
    const total = Array.from(document.querySelectorAll(".weight-input"))
      .reduce((sum, input) => sum + Number(input.value || 0), 0);
    if (total !== 100) {
      event.preventDefault();
      alert("Weights must sum to 100%.");
    }
  });
}
