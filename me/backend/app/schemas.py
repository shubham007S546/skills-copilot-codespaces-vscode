from typing import Dict, List, Optional

from pydantic import BaseModel, Field, PositiveFloat, conint, confloat


class DiseasePrediction(BaseModel):
    disease_name: str
    confidence: confloat(ge=0.0, le=1.0)
    top_k: List[Dict[str, float]]
    recommendation: str
    pesticide: str
    dosage: str
    spray_interval_days: int
    estimated_recovery_days: int
    approx_pesticide_cost_inr: PositiveFloat
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


class CostEstimatorResponse(BaseModel):
    predicted_total_cost_inr: float
    min_expected_cost_inr: float
    max_expected_cost_inr: float
    breakdown: Dict[str, float]
