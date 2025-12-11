from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

from src.api import models, schemas

logger = logging.getLogger("cloud-devops-api.crud")

class ProductAlreadyExistsError(Exception):
    """Raised when attempting to create a product with a name that already exists."""
    pass

def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    """
    Create a new product in the database.

    Args:
        db (Session): SQLAlchemy session.
        product (ProductCreate): Product creation schema.

    Returns:
        Product: The created Product model instance.

    Raises:
        ProductAlreadyExistsError: If a product with the same name already exists.
        SQLAlchemyError: For other database errors.
    """
    # Check for existing product with the same name
    existing = db.query(models.Product).filter(models.Product.name == product.name).first()
    if existing:
        logger.warning(f"Product creation failed: name '{product.name}' already exists.")
        raise ProductAlreadyExistsError(f"Product with name '{product.name}' already exists.")

    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price
    )
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Product created: {db_product}")
        return db_product
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during product creation: {e}")
        raise ProductAlreadyExistsError(f"Product with name '{product.name}' already exists.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during product creation: {e}")
        raise

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    """
    Retrieve a list of products from the database.

    Args:
        db (Session): SQLAlchemy session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.

    Returns:
        List[Product]: List of Product model instances.
    """
    products = db.query(models.Product).order_by(models.Product.id).offset(skip).limit(limit).all()
    logger.debug(f"Fetched {len(products)} products (skip={skip}, limit={limit})")
    return products

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    """
    Retrieve a product by its ID.

    Args:
        db (Session): SQLAlchemy session.
        product_id (int): Product ID.

    Returns:
        Product or None: Product model instance if found, else None.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        logger.debug(f"Product found: {product}")
    else:
        logger.debug(f"Product not found: id={product_id}")
    return product

def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate) -> Optional[models.Product]:
    """
    Update an existing product by its ID.

    Args:
        db (Session): SQLAlchemy session.
        product_id (int): Product ID.
        product_update (ProductUpdate): Product update schema.

    Returns:
        Product or None: Updated Product model instance if found, else None.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        logger.warning(f"Product not found for update: id={product_id}")
        return None

    # Update fields if provided
    if product_update.name is not None:
        # Check for name uniqueness
        existing = db.query(models.Product).filter(
            models.Product.name == product_update.name,
            models.Product.id != product_id
        ).first()
        if existing:
            logger.warning(f"Product update failed: name '{product_update.name}' already exists.")
            raise ProductAlreadyExistsError(f"Product with name '{product_update.name}' already exists.")
        product.name = product_update.name
    if product_update.description is not None:
        product.description = product_update.description
    if product_update.price is not None:
        product.price = product_update.price

    try:
        db.commit()
        db.refresh(product)
        logger.info(f"Product updated: {product}")
        return product
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during product update: {e}")
        raise ProductAlreadyExistsError(f"Product with name '{product_update.name}' already exists.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during product update: {e}")
        raise

def delete_product(db: Session, product_id: int) -> bool:
    """
    Delete a product by its ID.

    Args:
        db (Session): SQLAlchemy session.
        product_id (int): Product ID.

    Returns:
        bool: True if deleted, False if not found.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        logger.warning(f"Product not found for deletion: id={product_id}")
        return False

    try:
        db.delete(product)
        db.commit()
        logger.info(f"Product deleted: id={product_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during product deletion: {e}")
        raise

# Exported: create_product, get_products, get_product, update_product, delete_product, ProductAlreadyExistsError