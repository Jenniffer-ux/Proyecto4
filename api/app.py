from fastapi import FastAPI
from routes.prices import router as prices_router
app = FastAPI(title="API Optimización de Precios")
app.include_router(prices_router, prefix="/prices", tags=["prices"])
