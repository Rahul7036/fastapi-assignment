from pydantic import BaseModel, Field
from typing import Literal

class Item(BaseModel):
    id: int
    code: str
    unit: int
    age: int
    cost: float

class AddItemRequest(Item):
    pass

class SnapshotRequest(BaseModel):
    sort_by: Literal['unit', 'age', 'cost']

class RemoveItemRequest(BaseModel):
    id: int
