import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List

from src.api import models, schemas, crud, database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("cloud-devops-api")

# Initialize FastAPI app
app = FastAPI(
    title="Cloud DevOps Automation Platform - Product API",
    description="RESTful API for managing products as part of the Cloud DevOps Automation Platform.",
    version="1.0.0"
)

# CORS configuration (adjust origins as needed for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db() -> Session:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Exception handler for SQLAlchemy errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal database error."}
    )

# Health check endpoint
@app.get("/health", tags=["Health"], summary="Health check endpoint")
def health_check():
    """
    Returns API health status.
    """
    return {"status": "ok"}

# Product CRUD endpoints

@app.post(
    "/products/",
    response_model=schemas.Product,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Create a new product"
)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product with validated data.
    """
    try:
        db_product = crud.create_product(db=db, product=product)
        logger.info(f"Product created: {db_product.id}")
        return db_product
    except crud.ProductAlreadyExistsError as e:
        logger.warning(f"Product creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during product creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product."
        )

@app.get(
    "/products/",
    response_model=List[schemas.Product],
    status_code=status.HTTP_200_OK,
    tags=["Products"],
    summary="List all products"
)
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of products with pagination.
    """
    try:
        products = crud.get_products(db=db, skip=skip, limit=limit)
        logger.info(f"Retrieved {len(products)} products.")
        return products
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products."
        )

@app.get(
    "/products/{product_id}",
    response_model=schemas.Product,
    status_code=status.HTTP_200_OK,
    tags=["Products"],
    summary="Get a product by ID"
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a product by its unique ID.
    """
    product = crud.get_product(db=db, product_id=product_id)
    if not product:
        logger.warning(f"Product not found: {product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    logger.info(f"Product retrieved: {product_id}")
    return product

@app.put(
    "/products/{product_id}",
    response_model=schemas.Product,
    status_code=status.HTTP_200_OK,
    tags=["Products"],
    summary="Update a product by ID"
)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing product by its ID.
    """
    try:
        updated_product = crud.update_product(db=db, product_id=product_id, product_update=product_update)
        if not updated_product:
            logger.warning(f"Product not found for update: {product_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found."
            )
        logger.info(f"Product updated: {product_id}")
        return updated_product
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product."
        )

@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Products"],
    summary="Delete a product by ID"
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a product by its unique ID.
    """
    try:
        deleted = crud.delete_product(db=db, product_id=product_id)
        if not deleted:
            logger.warning(f"Product not found for deletion: {product_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found."
            )
        logger.info(f"Product deleted: {product_id}")
        return
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product."
        )

# Exported: FastAPI app instance
# Usage: uvicorn src.api.main:app --host 0.0.0.0 --port 8000