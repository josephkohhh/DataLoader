# main.py - FastAPI app and routes

# myenv\Scripts\Activate.ps1 source myenv/bin/activate
# uvicorn main:app --reload

from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv
import models, database, crud
from sqlalchemy.orm import Session
import os
import requests # pip install requests
import logging

load_dotenv() # Load .env file

logger = logging.getLogger(__name__)

app = FastAPI(title="DataLoader API", description="Fetch & load data into db") # Instantiate FastAPI class

models.Base.metadata.create_all(bind=database.engine) # Create tables in db defined in models.py

@app.get("/")
def root(): 
    return {
        "message": "Welcome to DataLoader API",
        "info": "Go to /docs to test out the API"
    }

@app.get('/get-all-products')
def fetch_all_products(db: Session = Depends(database.get_db)):
    """
    Fetch all products from the database
    """
    try:
        products = crud.get_all_products(db)
        return products
    except Exception as e:
        logger.error(f"Error fetching products: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@app.get('/get_product_by_id/{product_id}')
def fetch_product_by_id(product_id: int, db: Session = Depends(database.get_db)):
    """
    Fetch product by id from the database
    """
    product = crud.get_product_by_id(product_id,db)

    if not product:
        raise HTTPException(status_code=404, detail=f"Product ID {product_id} not found")

    return product


@app.post('/load-products')
def load_products(db: Session = Depends(database.get_db)):
    """
    Fetch products from DummyJSON and load into the database
    """
    url = os.getenv('EXTERNAL_API_URL')
    if not url:
        raise HTTPException(status_code=500, detail="EXTERNAL_API_URL not set in environment")
    
    try:
        response = requests.get(url) # raw JSON string
        response.raise_for_status() # checks the HTTP status code of the response
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from external API: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {e}")


    data = response.json() # convert to Parsed JSON
    products = data.get('products',[]) # It means dict.get(key, default)
    if not products: # if empty
        raise HTTPException(status_code=404, detail=f"No products found in DummyJSON API: {e}")

    # Use CRUD to insert
    inserted_count = crud.bulk_create_products(db, products)
    return {"message": f"Loaded {inserted_count} new products into the database"}


@app.delete('/delete-product/{product_id}')
def remove_product(product_id: int, db: Session = Depends(database.get_db)):
    """
    Delete a product by ID from the database
    """
    deleted_product = crud.delete_product(product_id, db)

    if not deleted_product:
        raise HTTPException(status_code=404, detail=f"Product ID {product_id} not found or could not be deleted")

    return {"message": f"Product ID {product_id} ({deleted_product.title}) deleted successfully"}


@app.delete('/delete-all-products')
def remove_all_products(db: Session = Depends(database.get_db)):
    """
    Delete all products and reset primary key sequence
    """
    success = crud.delete_all_products(db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete all products")
    
    return {"message": "All products deleted and primary key reset successfully"}