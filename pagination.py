from fastapi import FastAPI, Query
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI()

# Sample Data Store
items_db = [
    {"id": 1, "name": "Book", "price": 9.99, "category": "Books"},
    {"id": 2, "name": "Phone", "price": 499.99, "category": "Electronics"},
    {"id": 3, "name": "Pen", "price": 1.99, "category": "Stationery"},
    {"id": 4, "name": "Laptop", "price": 899.99, "category": "Electronics"},
    {"id": 5, "name": "Notebook", "price": 4.99, "category": "Stationery"},
    {"id": 6, "name": "Tablet", "price": 299.99, "category": "Electronics"},
]

class Item(BaseModel):
    id: int
    name: str
    price: float
    category: str

@app.get("/items/", response_model=List[Item])
def get_items(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    order: Optional[str] = Query("asc")
):
    results = items_db

    # Filtering
    if category:
        results = [item for item in results if item["category"] == category]

    # Sorting
    reverse = order == "desc"
    try:
        results.sort(key=lambda x: x[sort_by], reverse=reverse)
    except KeyError:
        return [{"error": f"Invalid sort field: {sort_by}"}]

    # Pagination
    return results[skip: skip + limit]
