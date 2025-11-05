# schemas.py - used for request validation and reponse models

from pydantic import BaseModel, Field
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
    id: int = Field(..., gt=0)  # Required and must be > 0
    title: str = Field(..., min_length=1)  # Required and non-empty
    description: Optional[str] = None
    category: Optional[str] = None
    price: float # Required 
    discountPercentage: Optional[float] = None
    rating: Optional[float] = None
    stock: Optional[int] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    weight: Optional[float] = None
    warrantyInformation: Optional[str] = None
    shippingInformation: Optional[str] = None
    availabilityStatus: Optional[str] = None
    returnPolicy: Optional[str] = None
    minimumOrderQuantity: Optional[int] = None
    thumbnail: Optional[str] = None
    dimensions: Optional[Dimensions] = None
    meta: Optional[Meta] = None
    reviews: List[Review] = Field(default_factory=list) # Field is optional
    tags: List[str] = Field(default_factory=list) # Field is optional
    images: List[str] = Field(default_factory=list) # Field is optional
    
    
# for POST requests
class ProductCreate(ProductBase): 
    pass  # inherit ProductBase

# for PUT requests
class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    discountPercentage: Optional[float] = None
    rating: Optional[float] = None
    stock: Optional[int] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    weight: Optional[float] = None
    warrantyInformation: Optional[str] = None
    shippingInformation: Optional[str] = None
    availabilityStatus: Optional[str] = None
    returnPolicy: Optional[str] = None
    minimumOrderQuantity: Optional[int] = None
    thumbnail: Optional[str] = None
    dimensions: Optional[Dimensions] = None
    meta: Optional[Meta] = None
    reviews: Optional[List[Review]] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None


# for GET responses - includes the id field
class ProductResponse(ProductBase):
    pass  # inherit ProductBase



class Config:
    orm_mode = True  # Allows SQLAlchemy model -> Pydantic conversion


# print(p)  
# Product(title='10', description='', category='') pydantic obj

# print(p.model_dump())  
# {'width': 10, 'height': 20, 'depth': 30} dict