from fastapi import FastAPI
from rtl_verify_platform.core.config import config_manager

app = FastAPI(title="AI RTL Verification Platform API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/config")
def get_config():
    return config_manager.config
