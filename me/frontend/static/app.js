const form = document.getElementById("predictForm");
const loader = document.getElementById("loader");
const result = document.getElementById("result");
const pdfBtn = document.getElementById("pdfBtn");
const langToggle = document.getElementById("langToggle");
let isHindi = false;

const i18n = {
  recommendation: {
    en: "Recommendation:",
    hi: "सुझाव:",
  },
};

function translateRecommendationText(text) {
  if (!isHindi) return text;
  return "सुझाव: " + text;
}

form?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const imageInput = document.getElementById("imageInput");
  if (!imageInput.files.length) return;

  const data = new FormData();
  data.append("file", imageInput.files[0]);
  const xaiLayer = document.getElementById("xaiLayer");
  data.append("xai_layer", xaiLayer?.value || "");
  loader.classList.remove("hidden");

  const res = await fetch("/api/predict", { method: "POST", body: data });
  const out = await res.json();
  loader.classList.add("hidden");
  result.classList.remove("hidden");

  document.getElementById("diseaseName").textContent = out.disease_name;
  document.getElementById("confidence").textContent = (out.confidence * 100).toFixed(2) + "%";
  document.getElementById("confidenceCal").textContent =
    (out.confidence_calibrated * 100).toFixed(2) + "%";
  document.getElementById("recommendation").textContent = translateRecommendationText(
    out.recommendation
  );
  document.getElementById("pesticide").textContent = out.pesticide;
  document.getElementById("dosage").textContent = out.dosage;
  document.getElementById("interval").textContent = out.spray_interval_days;
  document.getElementById("recovery").textContent = out.estimated_recovery_days;
  document.getElementById("price").textContent = out.approx_pesticide_cost_inr;
  const xai = document.getElementById("xaiImage");
  if (out.xai_image_base64) {
    xai.src = `data:image/jpeg;base64,${out.xai_image_base64}`;
  } else {
    xai.removeAttribute("src");
  }
});

pdfBtn?.addEventListener("click", async () => {
  const imageInput = document.getElementById("imageInput");
  if (!imageInput.files.length) return;
  const data = new FormData();
  data.append("file", imageInput.files[0]);
  const xaiLayer = document.getElementById("xaiLayer");
  data.append("xai_layer", xaiLayer?.value || "");
  const res = await fetch("/api/report/pdf", { method: "POST", body: data });
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "prediction_report.pdf";
  a.click();
  window.URL.revokeObjectURL(url);
});

langToggle?.addEventListener("click", () => {
  isHindi = !isHindi;
  const rec = document.getElementById("recommendation");
  if (rec?.textContent) {
    const current = rec.textContent.replace(/^सुझाव:\s*/, "");
    rec.textContent = isHindi ? `सुझाव: ${current}` : current;
  }
});
