import json
from typing import List
from app.schemas import Item

def load_items(data_file: str) -> List[Item]:
    try:
        with open(data_file, "r") as f:
            data = json.load(f)
            return [Item(**item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_items(items: List[Item], data_file: str):
    with open(data_file, "w") as f:
        json.dump([item.dict() for item in items], f)
