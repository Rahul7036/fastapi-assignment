from typing import List, Optional
from app.schemas import Item

class ItemService:
    def __init__(self, items: List[Item]):
        self.items = items

    def add_item(self, item: Item):
        # Prevent duplicate IDs
        if any(existing.id == item.id for existing in self.items):
            raise ValueError("Item with this ID already exists.")
        self.items.append(item)

    def get_items(self):
        return self.items

    def remove_item(self, item_id: int):
        for i, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[i]
                return
        raise ValueError("Item with this ID does not exist.")

    def clear_items(self):
        self.items.clear()
