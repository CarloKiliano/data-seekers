"""
Launcher del API.

Ejecuta: python run_api.py

Es un atajo a `uvicorn api.main:app --reload --host 0.0.0.0 --port 8000`,
con la ventaja de que toma host/puerto del archivo .env.
"""

import uvicorn
from api.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,        # auto-recarga al editar código (solo dev)
        log_level="info",
    )
