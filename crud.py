# crud.py - CRUD functions 

from sqlalchemy.orm import Session
from . import models, schemas
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


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
    

    # Insert new product
    db_product = models.Product(**validated.model_dump())
    db.add(db_product)

    try:
        db.commit()
        db.refresh(db_product)
    except SQLAlchemyError as e:
        db.rollback()
        print(f"DB error while inserting product ID {product_id}: {e}")
        return None
    
    return db_product


def bulk_create_product(db: Session, products: list[dict]):
    """
    Insert multiple products at once, skipping duplicates or invalid ones.
    """
    created_count = 0

    for p in products:
        create_product(db,p)
        created_count += 1
    
    print(f"✅ Loaded {created_count} products into database.")
    return created_count