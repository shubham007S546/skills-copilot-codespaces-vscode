const costForm = document.getElementById("costForm");
const costResult = document.getElementById("costResult");

function parseNumber(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

costForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(costForm);
  const payload = {
    crop_name: formData.get("crop_name"),
    land_area_acre: parseNumber(formData.get("land_area_acre")),
    is_land_rented: String(formData.get("is_land_rented")) === "true",
    land_rent_inr: parseNumber(formData.get("land_rent_inr")),
    duration_months: parseNumber(formData.get("duration_months")),
    labor_count: parseNumber(formData.get("labor_count")),
    labor_daily_wage_inr: parseNumber(formData.get("labor_daily_wage_inr")),
    self_work_hours_per_day: parseNumber(formData.get("self_work_hours_per_day")),
    water_cycles: parseNumber(formData.get("water_cycles")),
    water_cost_per_cycle_inr: parseNumber(formData.get("water_cost_per_cycle_inr")),
    seed_cost_inr: parseNumber(formData.get("seed_cost_inr")),
    fertilizer_cost_inr: parseNumber(formData.get("fertilizer_cost_inr")),
    pesticide_cost_inr: parseNumber(formData.get("pesticide_cost_inr")),
    insecticide_cost_inr: parseNumber(formData.get("insecticide_cost_inr")),
    spray_cost_inr: parseNumber(formData.get("spray_cost_inr")),
    tractor_cost_inr: parseNumber(formData.get("tractor_cost_inr")),
    transport_to_market_inr: parseNumber(formData.get("transport_to_market_inr")),
    misc_cost_inr: parseNumber(formData.get("misc_cost_inr")),
  };

  const res = await fetch("/api/estimate-cost", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const out = await res.json();
  costResult.classList.remove("hidden");
  document.getElementById("predCost").textContent = out.predicted_total_cost_inr;
  document.getElementById("minCost").textContent = out.min_expected_cost_inr;
  document.getElementById("maxCost").textContent = out.max_expected_cost_inr;
  document.getElementById("breakdown").textContent = JSON.stringify(out.breakdown, null, 2);
});
