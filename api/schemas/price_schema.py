from pydantic import BaseModel, Field
from typing import Optional, List

class PriceRequest(BaseModel):
    sku: Optional[str] = Field(default=None, description="SKU opcional")
    product_line: Optional[str] = Field(default=None, description="Línea de producto opcional")
    cost: float = Field(default=5.0, description="Costo unitario estimado")

class PriceResponse(BaseModel):
    sku: Optional[str]
    product_line: Optional[str]
    recommended_price: float
    best_margin: float
    price_grid: List[float]
    elasticity: float
    base_demand: float
    reference_price: float
    cost: float
