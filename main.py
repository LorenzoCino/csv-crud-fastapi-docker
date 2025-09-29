from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import os

app = FastAPI()

CSV_FILE = "data.csv"

# Modello dei dati-
class Item(BaseModel):
    id: int
    nome: str
    cognome: str
    codice_fiscale: str


# Funzioni di supporto CSV
def read_csv():
    items = []
    if not os.path.exists(CSV_FILE):
        return items
    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            items.append(row)
    return items


def write_csv(items):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["id", "nome", "cognome", "codice_fiscale"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)


# Endpoint CRUD

# Create (POST)
@app.post("/items/")
def create_item(item: Item):
    items = read_csv()
    # controlla se l'id esiste già
    if any(str(existing["id"]) == str(item.id) for existing in items):
        raise HTTPException(status_code=400, detail="ID already exists")
    items.append(item.dict())
    write_csv(items)
    return item


# Read all (GET per ottenere tutti i record)
@app.get("/items/")
def get_items():
    return read_csv()


# Read one (GET per ottenere un singolo record basato sull'ID)
@app.get("/items/{item_id}")
def get_item(item_id: int):
    items = read_csv()
    for item in items:
        if int(item["id"]) == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


# Update (PUT)
@app.put("/items/{item_id}")
def update_item(item_id: int, updated_item: Item):
    items = read_csv()
    for i, item in enumerate(items):
        if int(item["id"]) == item_id:
            items[i] = updated_item.dict()
            write_csv(items)
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")


# Delete 
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    items = read_csv()
    new_items = [item for item in items if int(item["id"]) != item_id]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    write_csv(new_items)
    return {"message": "Item deleted successfully"}


# Count (GET per ottenere il numero di righe nel CSV)
@app.get("/items/count")
def get_count():
    items = read_csv()
    return {"count": len(items)}
