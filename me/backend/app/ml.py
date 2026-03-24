import base64
import io
import os
from pathlib import Path
from typing import Tuple

import cv2
import joblib
import numpy as np
from PIL import Image

try:
    import tensorflow as tf
except Exception:  # pragma: no cover
    tf = None


ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT / "models"
DISEASE_MODEL_PATH = MODELS_DIR / "disease_cnn.keras"
COST_MODEL_PATH = MODELS_DIR / "cost_estimator.joblib"
ENCODER_PATH = MODELS_DIR / "cost_feature_encoder.joblib"
CLASS_NAMES_PATH = MODELS_DIR / "class_names.joblib"


class DummyDiseaseModel:
    class_names = [
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___Leaf_Mold",
        "Tomato___healthy",
    ]

    def predict(self, image_batch: np.ndarray) -> np.ndarray:
        sample = image_batch[0]
        redness = float(np.mean(sample[:, :, 0]))
        greeness = float(np.mean(sample[:, :, 1]))
        if greeness > redness + 0.1:
            probs = [0.07, 0.06, 0.05, 0.82]
        elif redness > greeness + 0.05:
            probs = [0.63, 0.2, 0.1, 0.07]
        else:
            probs = [0.2, 0.46, 0.24, 0.1]
        return np.array([probs], dtype=np.float32)


def load_disease_model():
    if tf is not None and DISEASE_MODEL_PATH.exists() and CLASS_NAMES_PATH.exists():
        model = tf.keras.models.load_model(DISEASE_MODEL_PATH)
        class_names = joblib.load(CLASS_NAMES_PATH)
        return model, class_names
    dummy = DummyDiseaseModel()
    return dummy, dummy.class_names


def preprocess_image(file_bytes: bytes, target_size: Tuple[int, int] = (224, 224)):
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    arr = np.array(image).astype("float32") / 255.0
    resized = cv2.resize(arr, target_size)
    return image, np.expand_dims(resized, axis=0)


def _resolve_target_conv_layer(model, preferred_layer_name: str = ""):
    if preferred_layer_name:
        try:
            return model.get_layer(preferred_layer_name)
        except Exception:
            pass
    conv_candidate = None
    for lyr in model.layers[::-1]:
        shape = getattr(lyr.output, "shape", None)
        if shape is not None and len(shape) == 4:
            conv_candidate = lyr
            break
    return conv_candidate


def generate_xai_heatmap_base64(
    orig_pil: Image.Image, image_batch: np.ndarray, model, xai_layer: str = ""
) -> str:
    if tf is None or not hasattr(model, "layers"):
        return ""
    try:
        target_layer = _resolve_target_conv_layer(model, xai_layer)
        if target_layer is None:
            return ""
        grad_model = tf.keras.models.Model([model.inputs], [target_layer.output, model.output])
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(image_batch)
            class_idx = tf.argmax(predictions[0])
            loss = predictions[:, class_idx]
        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)
        heatmap = np.maximum(heatmap, 0) / (np.max(heatmap) + 1e-8)
        heatmap = cv2.resize(
            heatmap.numpy(), (orig_pil.size[0], orig_pil.size[1]), interpolation=cv2.INTER_CUBIC
        )
        heatmap_u8 = np.uint8(255 * heatmap)
        heatmap_color = cv2.applyColorMap(heatmap_u8, cv2.COLORMAP_JET)
        original_bgr = cv2.cvtColor(np.array(orig_pil), cv2.COLOR_RGB2BGR)
        overlay = cv2.addWeighted(original_bgr, 0.6, heatmap_color, 0.4, 0)
        _, buffer = cv2.imencode(".jpg", overlay)
        return base64.b64encode(buffer.tobytes()).decode("utf-8")
    except Exception:
        return ""


def _calibrate_probs(probs: np.ndarray) -> np.ndarray:
    temperature = float(os.getenv("CONFIDENCE_TEMPERATURE", "1.3"))
    temperature = max(0.7, min(3.0, temperature))
    logits = np.log(np.clip(probs, 1e-9, 1.0))
    scaled = logits / temperature
    exp_scores = np.exp(scaled - np.max(scaled))
    return exp_scores / (np.sum(exp_scores) + 1e-9)


def predict_disease(file_bytes: bytes, xai_layer: str = ""):
    model, class_names = load_disease_model()
    orig_img, img_batch = preprocess_image(file_bytes)
    probs = model.predict(img_batch)[0]
    calibrated = _calibrate_probs(np.array(probs, dtype=np.float32))
    top_indices = np.argsort(probs)[::-1][:3]
    top_k = [{class_names[i]: float(probs[i])} for i in top_indices]
    best_idx = int(top_indices[0])
    xai_image = generate_xai_heatmap_base64(orig_img, img_batch, model, xai_layer=xai_layer)
    return (
        class_names[best_idx],
        float(probs[best_idx]),
        float(calibrated[best_idx]),
        top_k,
        xai_image,
    )


def load_cost_model():
    if COST_MODEL_PATH.exists() and ENCODER_PATH.exists():
        model = joblib.load(COST_MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
        return model, encoder
    return None, None


def estimate_cost(input_dict: dict):
    model, encoder = load_cost_model()

    manual_total = (
        input_dict["land_rent_inr"]
        + (input_dict["labor_count"] * input_dict["labor_daily_wage_inr"] * input_dict["duration_months"] * 26)
        + (input_dict["self_work_hours_per_day"] * 70 * input_dict["duration_months"] * 26)
        + (input_dict["water_cycles"] * input_dict["water_cost_per_cycle_inr"])
        + input_dict["seed_cost_inr"]
        + input_dict["fertilizer_cost_inr"]
        + input_dict["pesticide_cost_inr"]
        + input_dict["insecticide_cost_inr"]
        + input_dict["spray_cost_inr"]
        + input_dict["tractor_cost_inr"]
        + input_dict["transport_to_market_inr"]
        + input_dict["misc_cost_inr"]
    )

    if model is None or encoder is None:
        return float(manual_total)

    encoded = encoder.transform(
        [[input_dict["crop_name"], "rented" if input_dict["is_land_rented"] else "owned"]]
    )
    numeric = np.array(
        [
            [
                input_dict["land_area_acre"],
                input_dict["land_rent_inr"],
                input_dict["duration_months"],
                input_dict["labor_count"],
                input_dict["labor_daily_wage_inr"],
                input_dict["self_work_hours_per_day"],
                input_dict["water_cycles"],
                input_dict["water_cost_per_cycle_inr"],
                input_dict["seed_cost_inr"],
                input_dict["fertilizer_cost_inr"],
                input_dict["pesticide_cost_inr"],
                input_dict["insecticide_cost_inr"],
                input_dict["spray_cost_inr"],
                input_dict["tractor_cost_inr"],
                input_dict["transport_to_market_inr"],
                input_dict["misc_cost_inr"],
            ]
        ]
    )
    features = np.hstack([encoded, numeric])
    pred = float(model.predict(features)[0])
    return pred
