from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, constr, condecimal, validator

class ProductBase(BaseModel):
    """
    Shared properties for Product.
    """
    name: constr(strip_whitespace=True, min_length=1, max_length=255) = Field(
        ..., description="Unique name of the product"
    )
    description: Optional[str] = Field(
        None, description="Optional description of the product"
    )
    price: condecimal(gt=0, max_digits=10, decimal_places=2) = Field(
        ..., description="Price of the product (must be positive)"
    )

    @validator("description")
    def description_length(cls, v):
        if v is not None and len(v) > 10000:
            raise ValueError("Description is too long (max 10000 characters).")
        return v

class ProductCreate(ProductBase):
    """
    Schema for creating a new Product.
    """
    pass

class ProductUpdate(BaseModel):
    """
    Schema for updating an existing Product.
    All fields are optional.
    """
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = Field(
        None, description="Unique name of the product"
    )
    description: Optional[str] = Field(
        None, description="Optional description of the product"
    )
    price: Optional[condecimal(gt=0, max_digits=10, decimal_places=2)] = Field(
        None, description="Price of the product (must be positive)"
    )

    @validator("description")
    def description_length(cls, v):
        if v is not None and len(v) > 10000:
            raise ValueError("Description is too long (max 10000 characters).")
        return v

class Product(ProductBase):
    """
    Schema for returning a Product from the API.
    """
    id: int = Field(..., description="Unique identifier of the product")
    created_at: datetime = Field(..., description="Timestamp when the product was created")
    updated_at: datetime = Field(..., description="Timestamp when the product was last updated")

    class Config:
        orm_mode = True

# Exported: ProductBase, ProductCreate, ProductUpdate, Product