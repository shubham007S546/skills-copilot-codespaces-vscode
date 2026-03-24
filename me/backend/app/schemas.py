from typing import Dict, List, Optional

from pydantic import BaseModel, Field, PositiveFloat, conint, confloat


class DiseasePrediction(BaseModel):
    disease_name: str
    probable_cause: str
    confidence: confloat(ge=0.0, le=1.0)
    top_k: List[Dict[str, float]]
    recommendation: str
    pesticide: str
    insecticide: str
    dosage: str
    spray_interval_days: int
    estimated_recovery_days: int
    approx_pesticide_cost_inr: PositiveFloat
    approx_insecticide_cost_inr: confloat(ge=0.0)
    confidence_calibrated: confloat(ge=0.0, le=1.0) = 0.0
    xai_image_base64: Optional[str] = None


class CostEstimatorRequest(BaseModel):
    crop_name: str = Field(default="tomato")
    land_area_acre: confloat(gt=0.0, le=20.0)
    is_land_rented: bool
    land_rent_inr: confloat(ge=0.0, le=500000.0)
    duration_months: conint(ge=1, le=18)
    labor_count: conint(ge=0, le=50)
    labor_daily_wage_inr: confloat(ge=0.0, le=3000.0)
    self_work_hours_per_day: confloat(ge=0.0, le=16.0)
    water_cycles: conint(ge=0, le=40)
    water_cost_per_cycle_inr: confloat(ge=0.0, le=10000.0)
    seed_cost_inr: confloat(ge=0.0, le=100000.0)
    fertilizer_cost_inr: confloat(ge=0.0, le=200000.0)
    pesticide_cost_inr: confloat(ge=0.0, le=200000.0)
    insecticide_cost_inr: confloat(ge=0.0, le=200000.0)
    spray_cost_inr: confloat(ge=0.0, le=100000.0)
    tractor_cost_inr: confloat(ge=0.0, le=150000.0)
    transport_to_market_inr: confloat(ge=0.0, le=100000.0)
    misc_cost_inr: confloat(ge=0.0, le=100000.0)
    soil_quality_index: confloat(ge=0.0, le=10.0) = 6.0
    irrigation_quality_index: confloat(ge=0.0, le=10.0) = 6.0
    expected_rainfall_mm: confloat(ge=0.0, le=3000.0) = 700.0
    pest_pressure_index: confloat(ge=0.0, le=10.0) = 4.0
    expected_yield_quintal: confloat(ge=0.0, le=1000.0) = 120.0
    expected_market_price_inr_per_quintal: confloat(ge=0.0, le=20000.0) = 1800.0


class CostEstimatorResponse(BaseModel):
    predicted_total_cost_inr: float
    min_expected_cost_inr: float
    max_expected_cost_inr: float
    projected_revenue_inr: float
    projected_profit_inr: float
    breakdown: Dict[str, float]
