from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="SaaS API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True

class DashboardStats(BaseModel):
    total_users: int
    active_projects: int
    revenue: float

@app.get("/")
async def root():
    return {"message": "Welcome to your SaaS API"}

@app.get("/api/stats", response_model=DashboardStats)
async def get_stats():
    return {
        "total_users": 1250,
        "active_projects": 42,
        "revenue": 15400.50
    }

@app.get("/api/users", response_model=List[User])
async def get_users():
    return [
        {"id": 1, "username": "admin", "email": "admin@example.com"},
        {"id": 2, "username": "user1", "email": "user1@example.com"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
