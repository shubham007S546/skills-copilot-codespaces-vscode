import io
import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .ml import estimate_cost, predict_disease
from .recommendations import get_recommendation
from .schemas import CostEstimatorRequest, CostEstimatorResponse, DiseasePrediction


ROOT = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(ROOT / "frontend" / "templates"))

app = FastAPI(title="Smart Agri AI", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "frontend" / "static")), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/cost-estimator", response_class=HTMLResponse)
def cost_page(request: Request):
    return templates.TemplateResponse("cost_estimator.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    if request.cookies.get("admin_ok") == "1":
        return templates.TemplateResponse("admin.html", {"request": request, "ok": True})
    return templates.TemplateResponse("admin.html", {"request": request, "ok": False})


@app.post("/admin/login")
def admin_login(password: str = Form(...)):
    expected = os.getenv("ADMIN_PASSWORD", "admin123")
    if password != expected:
        raise HTTPException(status_code=401, detail="Invalid password")
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie("admin_ok", "1", httponly=True, samesite="lax")
    return response


@app.post("/admin/logout")
def admin_logout():
    response = RedirectResponse(url="/admin", status_code=303)
    response.delete_cookie("admin_ok")
    return response


@app.post("/api/predict", response_model=DiseasePrediction)
async def classify_disease(file: UploadFile = File(...), xai_layer: str = Form(default="")):
    contents = await file.read()
    disease_name, confidence, confidence_calibrated, top_k, xai_img = predict_disease(
        contents, xai_layer=xai_layer
    )
    advisory = get_recommendation(disease_name)
    return DiseasePrediction(
        disease_name=disease_name,
        confidence=confidence,
        confidence_calibrated=confidence_calibrated,
        top_k=top_k,
        recommendation=advisory["recommendation"],
        pesticide=advisory["pesticide"],
        dosage=advisory["dosage"],
        spray_interval_days=advisory["spray_interval_days"],
        estimated_recovery_days=advisory["estimated_recovery_days"],
        approx_pesticide_cost_inr=advisory["approx_pesticide_cost_inr"],
        xai_image_base64=xai_img or None,
    )


@app.post("/api/report/pdf")
async def prediction_pdf(file: UploadFile = File(...), xai_layer: str = Form(default="")):
    contents = await file.read()
    disease_name, confidence, confidence_calibrated, _, _ = predict_disease(contents, xai_layer=xai_layer)
    advisory = get_recommendation(disease_name)
    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    y = 800
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, "Smart Agri AI - Disease Report")
    y -= 35
    p.setFont("Helvetica", 11)
    lines = [
        f"Disease: {disease_name}",
        f"Raw confidence: {confidence * 100:.2f}%",
        f"Calibrated confidence: {confidence_calibrated * 100:.2f}%",
        f"Recommendation: {advisory['recommendation']}",
        f"Pesticide: {advisory['pesticide']}",
        f"Dosage: {advisory['dosage']}",
        f"Spray interval (days): {advisory['spray_interval_days']}",
        f"Estimated recovery (days): {advisory['estimated_recovery_days']}",
        f"Approx pesticide price (INR): {advisory['approx_pesticide_cost_inr']}",
    ]
    for line in lines:
        p.drawString(40, y, line[:110])
        y -= 22
    p.showPage()
    p.save()
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=prediction_report.pdf"},
    )


@app.post("/api/estimate-cost", response_model=CostEstimatorResponse)
def estimate_crop_cost(payload: CostEstimatorRequest):
    req = payload.model_dump()
    predicted = estimate_cost(req)
    breakdown = {
        "land": req["land_rent_inr"],
        "labor": req["labor_count"] * req["labor_daily_wage_inr"] * req["duration_months"] * 26,
        "self_work_imputed": req["self_work_hours_per_day"] * 70 * req["duration_months"] * 26,
        "water": req["water_cycles"] * req["water_cost_per_cycle_inr"],
        "seed": req["seed_cost_inr"],
        "fertilizer": req["fertilizer_cost_inr"],
        "pesticide": req["pesticide_cost_inr"],
        "insecticide": req["insecticide_cost_inr"],
        "spray": req["spray_cost_inr"],
        "tractor": req["tractor_cost_inr"],
        "transport": req["transport_to_market_inr"],
        "misc": req["misc_cost_inr"],
    }
    return CostEstimatorResponse(
        predicted_total_cost_inr=round(predicted, 2),
        min_expected_cost_inr=round(predicted * 0.9, 2),
        max_expected_cost_inr=round(predicted * 1.15, 2),
        breakdown={k: round(v, 2) for k, v in breakdown.items()},
    )


@app.get("/health")
def health():
    return {"status": "ok"}
