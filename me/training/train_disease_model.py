from pathlib import Path

import joblib
import kagglehub
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator


ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

print("Downloading dataset from KaggleHub...")
dataset_path = kagglehub.dataset_download("vipoooool/new-plant-diseases-dataset")
print("Dataset path:", dataset_path)

data_dir = Path(dataset_path) / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)"
train_dir = data_dir / "train"
valid_dir = data_dir / "valid"

img_size = (224, 224)
batch_size = 32

train_gen = ImageDataGenerator(
    rescale=1.0 / 255.0,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
)
valid_gen = ImageDataGenerator(rescale=1.0 / 255.0)

train_ds = train_gen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
)
valid_ds = valid_gen.flow_from_directory(
    valid_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
)

base = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3), include_top=False, weights="imagenet"
)
base.trainable = False

model = models.Sequential(
    [
        base,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(512, activation="relu"),
        layers.Dense(train_ds.num_classes, activation="softmax"),
    ]
)
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

callbacks = [
    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2),
    tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
]

model.fit(train_ds, validation_data=valid_ds, epochs=8, callbacks=callbacks)
model.save(MODELS_DIR / "disease_cnn.keras")

class_names = sorted(train_ds.class_indices, key=train_ds.class_indices.get)
joblib.dump(class_names, MODELS_DIR / "class_names.joblib")
print("Saved disease model and class labels.")
