from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AddItemRequest, SnapshotRequest, RemoveItemRequest, Item
from app.persistence import load_items, save_items
from app.services import ItemService
from app.db import db
import os
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = os.getenv("DATA_FILE", "data.json")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load items from disk at startup
items = load_items(DATA_FILE)
service = ItemService(items)

@app.post("/add")
def add_item(request: AddItemRequest):
    # Call the stored procedure first
    try:
        db_result = db.call_add_call(
            request.code, request.unit, request.age, request.cost
        )
        if not db_result:
            raise HTTPException(status_code=500, detail="No response from DB stored procedure.")
        row_id, success, message = db_result
        if not success:
            raise HTTPException(status_code=400, detail=f"DB Error: {message}")

        # If DB call is successful, add to in-memory and file
        try:
            service.add_item(Item(**request.dict()))
            save_items(service.get_items(), DATA_FILE)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {"message": f"Item added successfully. DB: {message}", "row_id": row_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/snapshot")
def snapshot(request: SnapshotRequest):
    items = service.get_items()
    sorted_items = sorted(items, key=lambda x: getattr(x, request.sort_by))
    return sorted_items

@app.post("/remove")
def remove_item(request: RemoveItemRequest):
    try:
        service.remove_item(request.id)
        save_items(service.get_items(), DATA_FILE)
        return {"message": "Item removed successfully."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/clear")
def clear():
    service.clear_items()
    save_items(service.get_items(), DATA_FILE)
    return {"message": "All items cleared."}

@app.on_event("shutdown")
def shutdown():
    db.close()
