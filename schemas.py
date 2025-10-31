# schemas.py - used for request validation and reponse models

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Arrays & Nested types
class Dimensions(BaseModel):
    width: float
    height: float
    depth: float

class Meta(BaseModel):
    createdAt: datetime
    updatedAt: datetime
    barcode: str
    qrCode: str

class Review(BaseModel):
    rating: int
    comment: str
    date: datetime
    reviewerName: str
    reviewerEmail: str

# Product 
class ProductBase(BaseModel):
    title: str
    description: Optional[str]
    category: Optional[str]
    price: float
    discountPercentage: Optional[float]
    rating: Optional[float]
    stock: Optional[int]
    brand: Optional[str]
    sku: Optional[str]
    weight: Optional[float]
    warrantyInformation: Optional[str]
    shippingInformation: Optional[str]
    availabilityStatus: Optional[str]
    returnPolicy: Optional[str]
    minimumOrderQuantity: Optional[int]
    thumbnail: Optional[str]
    dimensions: Optional[Dimensions]
    meta: Optional[Meta]
    reviews: Optional[List[Review]] = []
    tags: Optional[List[str]] = []
    images: Optional[List[str]] = []

# for POST requests
class ProductCreate(ProductBase): 
    pass  # all fields optional for flexibility if needed

# for GET responses - includes the id field
class ProductResponse(ProductBase):
    id: int 

    class Config:
        orm_mode = True  # Allows SQLAlchemy model -> Pydantic conversion
