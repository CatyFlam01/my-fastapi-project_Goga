from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import string, random
from fastapi.responses import RedirectResponse
import sqlite3

app = FastAPI(title='URL-Shorter')
# Модель для POST запроса
class URLItem(BaseModel):
    url: str


# Подключение к SQLLITE
conn = sqlite3.connect("urls.db", check_same_thread=False)
cur = conn.cursor()
print(">>> RUNNING FILE:", __file__)

cur.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        short_id TEXT PRIMARY KEY,
        full_url TEXT NOT NULL,
        clicks INTEGER DEFAULT 0
    )
""")
conn.commit()


# db = {}
# Генератор короткого ID
def generate_short_id(lenght=6):
    chars = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choice(chars) for _ in  lenght)
        cur.execute("SELECT 1 FROM urls WHERE short_id = ?", (short_id,))
        if cur.fetchone() is None:
            return short_id
        
#  ===== POST /SHORTEN =====
@app.post("/shorten")
def shorten_url(item: URLItem):
    short_id = generate_short_id()
    cur.execute(
        "INSERT INTO urls (short_id, full_url, clicks) VALUES (?,?,?)",
        (short_id, item.url, 0)
    )
    conn.commit()
    # db[short_id] = {"url": item.url, "clicks": 0} 
    return {"short_url": f"http://127.0.0.1:8000/{short_id}"}

@app.get("/{short_id}")
def redirected_to_url(short_id: str):
    cur.execute("SELECT full_url, clicks FROM urls WHERE short_id = ?", (short_id,))
    row = cur.fetchone()
    if short_id is None:
        raise HTTPException(status_code=404, detail="URL not found")
    
    full_url, clicks = row
    clicks += 1
    cur.execute("UPDATE urls SET clicks = ? WHERE short_id = ?", (clicks, short_id))
    conn.commit()
    # db[short_id]["clicks"] += 1
    return RedirectResponse(full_url)