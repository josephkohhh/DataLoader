# main.py - FastAPI app and routes

# myenv\Scripts\Activate.ps1 source myenv/bin/activate
# uvicorn main:app --reload

from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv
from . import models, database, crud
from sqlalchemy.orm import Session
import os
import requests # pip install requests

load_dotenv() # Load .env file
app = FastAPI(title="DataLoader API", description="Fetch & load data into db") # Instantiate FastAPI class

models.Base.metadata.create_all(bind=database.engine) # Create tables in db defined in models.py

@app.get("/")
def root(): 
    return {"message": "Welcome to DataLoader API\nGo to /docs to test out the API"}


@app.post('/load-products')
def load_products(db: Session = Depends(database.get_db)):
    """
    Fetch products from DummyJSON and load into the database
    """
    url = os.getenv('EXTERNAL_API_URL')
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {e}")


    data = response.json()
    products = data.get('products',[]) 
    if not products:
        raise HTTPException(status_code=404, detail=f"No products found in DummyJSON API: {e}")

    # Use CRUD to insert
    inserted_count = crud.bulk_create_products(db, products)
    return {"message": f"Loaded {inserted_count} new products into the database"}





# @app.get("/products", response_model=list[schemas.ProductResponse])
# def get_all_products(db: Session = Depends(database.get_db)):
#     """
#     Retrieve all products currently stored in the database.
#     """
#     products = db.query(models.Product).all()
#     return products


# @app.get("/products/{product_id}", response_model=schemas.ProductResponse)
# def get_product(product_id: int, db: Session = Depends(database.get_db)):
#     """
#     Retrieve a single product by its ID.
#     """
#     product = db.query(models.Product).filter(models.Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail=f"Product ID {product_id} not found")
#     return product