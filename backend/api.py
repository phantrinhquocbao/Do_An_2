"""Optional local API. Streamlit Cloud calls inference directly."""

from functools import lru_cache
import os

from fastapi import FastAPI
import pandas as pd
import uvicorn

from backend.inference import load_artifacts, load_features, predict_price

app = FastAPI()
cached_artifacts = lru_cache(maxsize=1)(load_artifacts)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/update")
def trigger_update():
    try:
        from backend.cap_nhat_model import cap_nhat_chinh

        cap_nhat_chinh()
        cached_artifacts.cache_clear()
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/predict/{ticker}")
def predict_stock(ticker: str):
    try:
        end = pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").normalize().tz_localize(None)
        start = end - pd.Timedelta(days=365)
        features = load_features(ticker, str(start.date()), str(end.date()))
        model, scaler = cached_artifacts()
        return {"ticker": ticker.upper(), "predicted_price_vnd": predict_price(features, model, scaler)}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
