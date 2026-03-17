"""Router de Produtos e Serviços."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut

router = APIRouter()


@router.get("", response_model=list[ProductOut])
def list_products(clinic_id: str, active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(Product).filter(Product.clinic_id == clinic_id)
    if active_only:
        q = q.filter(Product.is_active == True)
    return q.order_by(Product.name).all()


@router.post("", response_model=ProductOut, status_code=201)
def create_product(clinic_id: str, payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(id=str(uuid.uuid4()), clinic_id=clinic_id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, clinic_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == product_id, Product.clinic_id == clinic_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: str, clinic_id: str, payload: ProductUpdate, db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id, Product.clinic_id == clinic_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: str, clinic_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        Product.id == product_id, Product.clinic_id == clinic_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    product.is_active = False  # soft delete
    db.commit()
