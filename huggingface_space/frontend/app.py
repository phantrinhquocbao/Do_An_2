"""Compatibility entrypoint; use the canonical app and model from repo root."""

from pathlib import Path
import runpy
import streamlit as st

try:
    app = Path(__file__).resolve().parents[2] / "frontend" / "app.py"
    runpy.run_path(str(app), run_name="__main__")
except Exception as e:
    st.error(str(e))
