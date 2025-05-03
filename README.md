## Overview

This project is a FastAPI application that demonstrates progressive backend reasoning and problem-solving. It features in-memory and file-based persistence, PostgreSQL (NeonDB) integration, deduplication, and robust error handling.

---

## Features

- **Add Item**: Add an item to the collection, with deduplication logic.
- **Retrieve Snapshot**: Get a sorted snapshot of the current collection.
- **Remove Item**: Remove an item by its ID.
- **Clear Collection**: Remove all items.
- **Persistence**: Data is persisted to both a file and a PostgreSQL database (NeonDB).
- **Deduplication**: Prevents duplicate items based on a combination of fields.
- **CORS**: Configurable via `.env`.
- **Config**: All sensitive/configurable values are in `.env`.

---

## Endpoints

### 1. **Add Item**
- **Endpoint:** `/add`
- **Method:** POST
- **Request Body:**
  ```json
  {
    "id": int,
    "code": "string",
    "unit": int,
    "age": int,
    "cost": float
  }
  ```
- **Action:**  
  - Calls a PostgreSQL stored procedure (`add_call`) to insert the item.
  - If successful, adds the item to in-memory and file storage.
  - Returns a success or error message.

### 2. **Retrieve Snapshot**
- **Endpoint:** `/snapshot`
- **Method:** POST
- **Request Body:**
  ```json
  {
    "sort_by": "unit" | "age" | "cost"
  }
  ```
- **Action:**  
  Returns the current collection, sorted by the requested field.

### 3. **Remove Item**
- **Endpoint:** `/remove`
- **Method:** POST
- **Request Body:**
  ```json
  {
    "id": int
  }
  ```
- **Action:**  
  Removes the item with the given ID.

### 4. **Clear Collection**
- **Endpoint:** `/clear`
- **Method:** POST
- **Request Body:** _None_
- **Action:**  
  Clears all items from the collection.

---

## Persistence & Crash Recovery

- **File-based:**  
  All changes are immediately written to `data.json` (configurable in `.env`).
- **Database:**  
  All items are also stored in a PostgreSQL database (NeonDB).
- **Crash Recovery:**  
  On restart, the app loads items from `data.json`. If needed, you can re-sync from the database.

---

## Deduplication

- **Database Level:**  
  A unique constraint on `(code, unit, age, cost)` in the `items` table prevents exact duplicates.
- **Application Level:**  
  The app also checks for duplicates in memory before adding a new item.

---

## Setup & Running

1. **Clone the repository and navigate to the project directory.**
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure your `.env` file:**
   ```
   DATA_FILE=data.json
   CORS_ORIGINS=*
   DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@YOUR_NEON_ENDPOINT/neondb?sslmode=require
   ```
5. **Run the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```
6. **Access the interactive API docs:**  
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Database Setup (NeonDB)

> **Note:**  
> All database operations (table creation, unique constraint, and stored procedure) are executed in NeonDB using the provided connection string in `.env`. 

### **Table and Unique Constraint**
```sql
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    unit INTEGER NOT NULL,
    age INTEGER NOT NULL,
    cost DOUBLE PRECISION NOT NULL
);

ALTER TABLE items
ADD CONSTRAINT unique_item_fields UNIQUE (code, unit, age, cost);
```

### **Stored Procedure**
```sql
DROP FUNCTION IF EXISTS add_call(TEXT, INTEGER, INTEGER, DOUBLE PRECISION);

CREATE OR REPLACE FUNCTION add_call(
    code TEXT,
    unit INTEGER,
    age INTEGER,
    cost DOUBLE PRECISION
)
RETURNS TABLE(row_id INT, success INT, message TEXT) AS $$
DECLARE
    new_id INT;
BEGIN
    INSERT INTO items (code, unit, age, cost)
    VALUES (code, unit, age, cost)
    RETURNING id INTO new_id;
    RETURN QUERY SELECT new_id, 1, 'Insert successful';
EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT NULL::INT, 0::INT, 'Insert failed: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

---

## Testing

You can use [Swagger UI](http://127.0.0.1:8000/docs), Postman, or curl to test all endpoints.  
Example curl for `/add`:
```bash
curl -X POST "http://127.0.0.1:8000/add" \
  -H "Content-Type: application/json" \
  -d "{\"id\":1,\"code\":\"A123\",\"unit\":10,\"age\":5,\"cost\":99.99}"
```

---

## Notes

- **NeonDB** is used for all database operations.  
  All SQL (table creation, unique constraint, stored procedure) should be executed in the NeonDB SQL editor or any connected SQL client.
- **Deduplication** is enforced both in the database and in the application logic.
- **All configuration** (database URL, file path, CORS origins) is managed via `.env`.
- **data.json** For your reference i have even adding the data.json file which was tested by me in my system

---