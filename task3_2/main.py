from fastapi import FastAPI, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI(title="Task 3.2 - Product Search")

sample_product_1 = {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99}
sample_product_2 = {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99}
sample_product_3 = {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99}
sample_product_4 = {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99}
sample_product_5 = {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}

sample_products = [sample_product_1, sample_product_2, sample_product_3, sample_product_4, sample_product_5]

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float

@app.get("/product/{product_id}", response_model=Product)
async def get_product(product_id: int):
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/products/search", response_model=List[Product])
async def search_products(
    keyword: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100)
):
    results = []
    for product in sample_products:
        if keyword.lower() in product["name"].lower():
            if category and product["category"].lower() != category.lower():
                continue
            results.append(product)
    return results[:limit]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)