from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sqlite3
import os
from datetime import datetime

app = FastAPI(title="Win Suggestion")

# Allow CORS since the script makes a fetch from solpump.io
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class SignalData(BaseModel):
    prev_crash: float
    players: int
    pool_sol: float
    signal: str
    actual_crash: float
    success: bool
    overall_cashout: float = 0.0

DB_FILE = "history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            prev_crash REAL,
            players INTEGER,
            pool_sol REAL,
            signal TEXT,
            actual_crash REAL,
            success BOOLEAN
        )
    ''')
    # Dynamic migration to add overall_cashout column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE signals ADD COLUMN overall_cashout REAL DEFAULT 0')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE signals ADD COLUMN system_pnl REAL DEFAULT 0')
        conn.commit()
    except sqlite3.OperationalError:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    # Insert defaults if not exists
    defaults = [
        ('req_prev', '1'),
        ('req_players', '1'),
        ('req_pool', '1'),
        ('skip_low_pool', '1'),
    ]
    for k, v in defaults:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (k, v))
    conn.commit()
    conn.close()

# Initialize Database on startup
init_db()

@app.post("/api/record")
async def record_signal(data: SignalData):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    system_pnl = data.pool_sol - data.overall_cashout
    
    cursor.execute('''
        INSERT INTO signals (timestamp, prev_crash, players, pool_sol, signal, actual_crash, success, overall_cashout, system_pnl)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp,
        data.prev_crash,
        data.players,
        data.pool_sol,
        data.signal,
        data.actual_crash,
        data.success,
        data.overall_cashout,
        system_pnl
    ))
    
    conn.commit()
    conn.close()
    
    return {"status": "recorded"}

@app.get("/api/history")
async def get_history():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM signals ORDER BY id DESC LIMIT 100000')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/history/clear")
async def clear_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM signals')
    conn.commit()
    conn.close()
    return {"status": "cleared"}

@app.get("/api/settings")
async def get_settings():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM settings')
    rows = cursor.fetchall()
    conn.close()
    return {row['key']: row['value'] for row in rows}

@app.post("/api/settings")
async def save_settings(data: dict):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for k, v in data.items():
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (k, str(v)))
    conn.commit()
    conn.close()
    return {"status": "saved"}

@app.get("/")
async def index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
