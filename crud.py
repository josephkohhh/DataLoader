# crud.py - CRUD functions

from sqlalchemy.orm import Session
import models, schemas
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


def to_json_safe(data):
    """
    Recursively converts any Pydantic model, list, or dict into
    plain Python types that are JSON-serializable.
    """
    if data is None:
        return None
    elif isinstance(data, (datetime, date)):
        # datetime objs are not serializable by json hence
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


def get_all_products(db: Session):
    """
    Fetch all products from the database with error handling
    """
    try:
        products = db.query(models.Product).all()
        return products
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching products: {e}", exc_info=True)
        return [] # return empty list if DB fails
    

def get_product_by_id(product_id: int, db: Session, ):
    """
    Fetch all products from the database with error handling
    """
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        return product
    except SQLAlchemyError as e:
        logger.error(f"DB error fetching product: {e}", exc_info=True)
        return None


def create_product(db: Session, product: dict):
    """
    Insert a product into the database
    Accepts a dict from DummyJSON API
    Skips insertion if product with same ID already exists
    """
    id = product.get("id")

    # Check if product already exists
    existing = db.query(models.Product).filter(models.Product.id == id).first()
    if existing:
        logger.info(f"Skipping duplicate product ID {id}: {existing.title}")
        return existing, False # Not created

    # Validate product data format
    try:
        validated = schemas.ProductCreate(**product)
    except ValidationError as e:
        logger.warning(f"Skipping invalid product ID {id}: {e.errors()}")
        return None, False # validation error

    # Convert to plain JSON-serializable dict
    data = to_json_safe(validated)

    db_product = models.Product(**data) # Unpacked to kwargs
    db.add(db_product)

    try:
        db.commit()
        db.refresh(db_product)
        logger.info(f"Inserted product ID {id}: {validated.title}")
        return db_product, True  # Newly created 
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error while inserting product ID {id}: {e}", exc_info=True)
        return None, False  # DB error

    


def bulk_create_products(db: Session, products: list[dict]):
    """
    Insert multiple products at once, skipping duplicates or invalid ones.
    """
    created_count = 0

    for p in products:
        # Unpack tuple
        # _ -> ignore first value (product_instance)
        # is_created -> keep second value (True/False)
        _, is_created = create_product(db, p)
        if is_created:
            created_count += 1

    logger.info(f"Loaded {created_count} products into database.")
    return created_count



def update_product(id: int, product_data: dict, db: Session):
    """
    Update product by ID. Safely merges JSON fields and updates meta.updatedAt.
    Converts any datetime objects to ISO strings before saving.
    """
    try:
        db_product = db.query(models.Product).filter(models.Product.id == id).first()
        if not db_product:
            return None

        json_fields = ["meta", "dimensions", "reviews", "tags", "images"]

        for key, value in product_data.items():
            if value is None:
                continue

            if key in json_fields:
                # Get current value or empty dict/list
                current = getattr(db_product, key)
                if current is None:
                    current = {} if isinstance(value, dict) else []
                
                # Convert new value to JSON-safe types
                safe_value = to_json_safe(value)

                # Merge if dict, replace if list
                if isinstance(current, dict) and isinstance(safe_value, dict):
                    current.update(safe_value)
                    setattr(db_product, key, current)
                else:
                    setattr(db_product, key, safe_value)
            else:
                setattr(db_product, key, value)

        # Update internal meta.updatedAt
        meta = to_json_safe(db_product.meta) or {}  # Ensure dict and JSON-safe
        meta["updatedAt"] = datetime.utcnow().isoformat()
        db_product.meta = meta  # Reassign to trigger SQLAlchemy change tracking

        db.commit()
        db.refresh(db_product)
        return db_product

    except SQLAlchemyError as e:
        logger.error(f"DB error updating product {id}: {e}", exc_info=True)
        db.rollback()
        return None




def delete_product(id: int, db: Session):
    """
    Delete a product from the database by product_id.
    """
    try:
        product = db.query(models.Product).filter(models.Product.id == id).first()
        if not product:
            return None
        
        db.delete(product)
        db.commit()
        return product  
    
    except SQLAlchemyError as e:
        logger.error(f"DB error deleting product ID {id}: {e}", exc_info=True)
        db.rollback()
        return None
    

def delete_all_products(db: Session):
    """
    Delete all products from the database.
    """
    try:
        # Delete all rows
        db.query(models.Product).delete()
        db.commit()

        # Reset PostgreSQL sequence
        db.execute(text('ALTER SEQUENCE "products_columnId_seq" RESTART WITH 1'))
        db.commit()

        return True
    
    except SQLAlchemyError as e:
        logger.error(f"DB error deleting all products: {e}", exc_info=True)
        db.rollback()
        return False