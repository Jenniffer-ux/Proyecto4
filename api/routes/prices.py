from fastapi import APIRouter, Depends, HTTPException
from pathlib import Path
from api.schemas.price_schema import PriceRequest, PriceResponse
from src.service.recommendation import recommend_price

router = APIRouter()

def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]

@router.post("/recommend", response_model=PriceResponse)
def recommend(req: PriceRequest, project_root: Path = Depends(get_project_root)):
    try:
        result = recommend_price(project_root=project_root, sku=req.sku,
                                 product_line=req.product_line, cost=req.cost)
        return PriceResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
