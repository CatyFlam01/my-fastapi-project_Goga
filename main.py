'''

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title='To-Do-Serv')

class Task(BaseModel):
    title: str
    completed: bool = False
    deleted: bool = False

# Имитация БД
tasks = {} # Пустой словарб с текстами
# 'task1' : ['Сделать ДЗ по ПИ', True]
task_id_counter = 1

# POST /task - создание новой задачи
@app.post("/task")
def create_task(task: Task):
    global task_id_counter
    tasks[task_id_counter] = task
    task_id_counter += 1
    # task = {1: Task()}
    return {"id": task_id_counter - 1, "task": task}

# GET /tasks - получение списка всех задач
@app.get("/tasks")
def get_all_tasks():
    active = {
        task_id: task for task_id, task in tasks.items()
        if not tasks.deleted
    }
    return {"tasks": active}
# GET /tasks/{id} - получении информауии о конкрентной задаче
@app.get("/tasks/{task_id}") # GET / task/3/ => get_task(task_id=5) 
def get_task(task_id: int):
    if task_id not in tasks: # Есть ли задача с таким ID?
        return HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

# Метод PUT Отвечает за обновление какой либо задачи
# PUT /Tasks/{id} - обновление задачи (изменение текста или статуса)
@app.put("/task/{task_id}")
# PUT/tasks/1
# {'title': "Купить хлеб и КЕФИР", 'completed: true'}
def update_task(task_id: int, update_task: Task):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[task_id] = update_task
    return {"id": task_id - 1, "task": update_task}

# DELETE /tasks/{id} - удаление задачи
@app.delete("/task/{task_id}")
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    # del tasks[task_id]
    tasks[task_id].deleted = True
    return {"id": task_id - 1, "status": "deleted"}

# GET
@app.get("/tasks/deleted")
def get_delete_tasks():
    deleted = {
        task_id: task for task_id, task in tasks.item()
        if tasks.deleted
    }
    return {"deleted_tasks": deleted}

'''



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



