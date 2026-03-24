# Smart Agri AI (FastAPI + CNN + XAI + Cost Estimator)

Complete project with:

- Leaf disease classifier API + web UI
- Treatment recommendation (solution, dosage, pesticide, recovery time, approximate price)
- XAI heatmap (Grad-CAM when TensorFlow model is available)
- Crop cost estimator page
- Synthetic 20k Himachal-style crop costing dataset + trained model
- Training notebook and scripts
- Admin login page
- PDF report export
- Hindi/English UI toggle
- Docker + Render + Railway deployment config

## Project Structure

`backend/app/main.py` - FastAPI app and routes  
`backend/app/ml.py` - model loading, prediction, XAI, cost inference  
`backend/app/recommendations.py` - disease -> solution mapping  
`frontend/templates` - HTML pages  
`frontend/static` - CSS and JS  
`training/train_disease_model.py` - CNN training with KaggleHub dataset  
`training/generate_cost_dataset_and_train.py` - 20k synthetic data + RF model  
`training/plant_disease_complete_notebook.ipynb` - complete notebook workflow

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Train Models

Disease model:

```bash
python training/train_disease_model.py
```

Cost model + synthetic dataset:

```bash
python training/generate_cost_dataset_and_train.py
```

## Run API + Website

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Open:

- `http://127.0.0.1:8000/` (Disease detection)
- `http://127.0.0.1:8000/cost-estimator` (Cost estimator)
- `http://127.0.0.1:8000/admin` (Admin)

## Docker

```bash
docker compose up --build
```

## Deploy

- Render: `render.yaml`
- Railway: `railway.json`
- Procfile platforms: `Procfile`

## Environment variables

- `ADMIN_PASSWORD` (default `admin123`)
- `CONFIDENCE_TEMPERATURE` (default `1.3`)

## Notes

- If disease model is not trained yet, app uses a fallback dummy model so UI works immediately.
- After training, real TensorFlow model and class labels are loaded automatically from `models/`.
- You can extend `recommendations.py` with more classes from the Kaggle dataset.
