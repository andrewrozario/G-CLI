from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="REST API")

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# Mock database
items = {
    1: {"id": 1, "name": "Item 1", "price": 10.0},
    2: {"id": 2, "name": "Item 2", "price": 20.0}
}

@app.get("/items/", response_model=List[Item])
async def read_items():
    return list(items.values())

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    if item.id in items:
        raise HTTPException(status_code=400, detail="Item already exists")
    items[item.id] = item.dict()
    return item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
