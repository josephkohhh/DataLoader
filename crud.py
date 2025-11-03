# crud.py - CRUD functions 

from sqlalchemy.orm import Session
import models, schemas
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date 

def to_json_safe(data):
    """
    Recursively converts any Pydantic model, list, or dict into
    plain Python types that are JSON-serializable.
    """
    if data is None:
        return None
    elif isinstance(data, (datetime, date)):
        # Convert datetime/date to ISO 8601 string (safe for JSON)
        return data.isoformat()
    elif hasattr(data, "model_dump"):  # Pydantic model
        return {k: to_json_safe(v) for k, v in data.model_dump().items()}
    elif isinstance(data, list):
        return [to_json_safe(item) for item in data]
    elif isinstance(data, dict):
        return {k: to_json_safe(v) for k, v in data.items()}
    else:
        return data  # already a primitive type


def create_product(db: Session, product: dict):
    """
    Insert a product into the database
    Accepts a dict from DummyJSON API
    Skips insertion if product with same ID already exists
    """
    product_id = product.get('id')

    # Check if product already exists
    existing = db.query(models.Product).filter(models.Product.id == product_id).first()
    if existing:
        print(f"Skipping duplicate product ID {product_id}: {existing.title}")
        return existing

    # Validate product data format
    try:
        validated = schemas.ProductCreate(**product)
    except ValidationError as e:
        print(f"Skipping invalid product ID {product_id}: {e.errors()}")
        return None 
    

    # Convert to plain JSON-serializable dict
    data = to_json_safe(validated)

    db_product = models.Product(**data)
    db.add(db_product)

    try:
        db.commit()
        db.refresh(db_product)
        print(f"Inserted product ID {product_id}: {validated.title}")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"DB error while inserting product ID {product_id}: {e}")
        return None
    
    return db_product


def bulk_create_products(db: Session, products: list[dict]):
    """
    Insert multiple products at once, skipping duplicates or invalid ones.
    """
    created_count = 0

    for p in products:
        result = create_product(db,p)
        if result:
            created_count += 1
    
    print(f"Loaded {created_count} products into database.")
    return created_count