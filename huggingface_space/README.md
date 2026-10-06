# Legacy entrypoint

Deploy Streamlit Community Cloud from the full repository, Python 3.12,
using `frontend/app.py` at repository root. See `../README.md`.

This folder's frontend forwards to the canonical app. It is not a standalone
Hugging Face deployment: the root backend/model files and requirements are required.
The historical Dockerfile in this folder is not used by Streamlit Cloud.
