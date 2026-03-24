RECOMMENDATIONS_DB = {
    "Tomato___Bacterial_spot": {
        "recommendation": "Use copper oxychloride spray and remove infected leaves.",
        "pesticide": "Copper Oxychloride 50% WP",
        "dosage": "2 g per 1 liter water",
        "spray_interval_days": 15,
        "estimated_recovery_days": 20,
        "approx_pesticide_cost_inr": 450.0,
    },
    "Tomato___Early_blight": {
        "recommendation": "Spray chlorothalonil/mancozeb and avoid leaf wetness.",
        "pesticide": "Mancozeb 75% WP",
        "dosage": "2.5 g per 1 liter water",
        "spray_interval_days": 10,
        "estimated_recovery_days": 18,
        "approx_pesticide_cost_inr": 380.0,
    },
    "Tomato___Late_blight": {
        "recommendation": "Use systemic fungicide quickly and improve drainage.",
        "pesticide": "Metalaxyl + Mancozeb",
        "dosage": "2 g per 1 liter water",
        "spray_interval_days": 7,
        "estimated_recovery_days": 14,
        "approx_pesticide_cost_inr": 520.0,
    },
    "Tomato___Leaf_Mold": {
        "recommendation": "Spray wettable sulfur and improve ventilation.",
        "pesticide": "Sulfur 80% WDG",
        "dosage": "2 g per 1 liter water",
        "spray_interval_days": 12,
        "estimated_recovery_days": 16,
        "approx_pesticide_cost_inr": 340.0,
    },
    "Tomato___Septoria_leaf_spot": {
        "recommendation": "Apply protective fungicide and avoid overhead irrigation.",
        "pesticide": "Chlorothalonil 75% WP",
        "dosage": "2 g per 1 liter water",
        "spray_interval_days": 10,
        "estimated_recovery_days": 21,
        "approx_pesticide_cost_inr": 430.0,
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "recommendation": "Use acaricide and monitor lower leaf surfaces.",
        "pesticide": "Abamectin 1.9% EC",
        "dosage": "0.5 ml per 1 liter water",
        "spray_interval_days": 10,
        "estimated_recovery_days": 15,
        "approx_pesticide_cost_inr": 600.0,
    },
    "Tomato___Target_Spot": {
        "recommendation": "Use broad-spectrum fungicide and sanitize crop residue.",
        "pesticide": "Azoxystrobin 23% SC",
        "dosage": "1 ml per 1 liter water",
        "spray_interval_days": 10,
        "estimated_recovery_days": 18,
        "approx_pesticide_cost_inr": 700.0,
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "recommendation": "Control whiteflies and remove infected plants early.",
        "pesticide": "Imidacloprid 17.8% SL",
        "dosage": "0.3 ml per 1 liter water",
        "spray_interval_days": 12,
        "estimated_recovery_days": 28,
        "approx_pesticide_cost_inr": 550.0,
    },
    "Tomato___Tomato_mosaic_virus": {
        "recommendation": "Destroy infected plants and disinfect farm tools.",
        "pesticide": "No direct curative spray (preventive care)",
        "dosage": "Use preventive hygiene protocol",
        "spray_interval_days": 0,
        "estimated_recovery_days": 30,
        "approx_pesticide_cost_inr": 200.0,
    },
    "Tomato___healthy": {
        "recommendation": "Plant appears healthy. Continue preventive monitoring.",
        "pesticide": "No pesticide required",
        "dosage": "N/A",
        "spray_interval_days": 0,
        "estimated_recovery_days": 0,
        "approx_pesticide_cost_inr": 0.0,
    },
}


def get_recommendation(disease_name: str) -> dict:
    default_item = {
        "recommendation": "No exact advisory found. Consult local agriculture officer.",
        "pesticide": "General broad-spectrum fungicide/insecticide",
        "dosage": "Follow label dose",
        "spray_interval_days": 10,
        "estimated_recovery_days": 20,
        "approx_pesticide_cost_inr": 500.0,
    }
    return RECOMMENDATIONS_DB.get(disease_name, default_item)
