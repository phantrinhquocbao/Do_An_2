"""Optional manual fine-tuning: python -m backend.cap_nhat_model."""

import numpy as np
import pandas as pd

from backend.inference import (
    MODEL_PATH, TARGET_INDEX, TIME_STEPS, load_artifacts, load_features, scale_features,
)

EPOCHS = 5


def cap_nhat_chinh():
    model, scaler = load_artifacts()
    today = pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").date()
    features = load_features("HPG", "2024-01-01", str(today))
    scaled = scale_features(features, scaler)
    if len(scaled) <= TIME_STEPS:
        raise ValueError("Chưa đủ dữ liệu để tạo mẫu cập nhật model.")
    x_new = np.array([scaled[i - TIME_STEPS:i] for i in range(TIME_STEPS, len(scaled))])
    y_new = scaled[TIME_STEPS:, TARGET_INDEX]
    # Inference loads without optimizer state; explicitly compile for training.
    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(x_new, y_new, epochs=EPOCHS, batch_size=16)
    model.save(MODEL_PATH)


if __name__ == "__main__":
    cap_nhat_chinh()
