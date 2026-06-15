from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import psycopg2
import psycopg2.extras
from datetime import datetime

app = FastAPI(title="Win Suggestion")

# Resolve paths relative to this file (works locally and on Vercel)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Allow CORS since the script makes a fetch from solpump.io
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class SignalData(BaseModel):
    prev_crash: float
    players: int
    pool_sol: float
    signal: str
    actual_crash: float
    success: bool
    overall_cashout: float = 0.0

# --- Database connection ---
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id SERIAL PRIMARY KEY,
            timestamp TEXT,
            prev_crash REAL,
            players INTEGER,
            pool_sol REAL,
            signal TEXT,
            actual_crash REAL,
            success BOOLEAN,
            overall_cashout REAL DEFAULT 0,
            system_pnl REAL DEFAULT 0
        )
    ''')

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
        cursor.execute(
            'INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO NOTHING',
            (k, v)
        )

    conn.commit()
    cursor.close()
    conn.close()

# Initialize Database on startup
init_db()

@app.post("/api/record")
async def record_signal(data: SignalData):
    conn = get_conn()
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_pnl = data.pool_sol - data.overall_cashout

    cursor.execute('''
        INSERT INTO signals (timestamp, prev_crash, players, pool_sol, signal, actual_crash, success, overall_cashout, system_pnl)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
    cursor.close()
    conn.close()

    return {"status": "recorded"}

@app.get("/api/history")
async def get_history():
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT * FROM signals ORDER BY id DESC LIMIT 100000')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/history/clear")
async def clear_history():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM signals')
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "cleared"}

@app.get("/api/settings")
async def get_settings():
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT key, value FROM settings')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row['key']: row['value'] for row in rows}

@app.post("/api/settings")
async def save_settings(data: dict):
    conn = get_conn()
    cursor = conn.cursor()
    for k, v in data.items():
        cursor.execute(
            'INSERT INTO settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value',
            (k, str(v))
        )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "saved"}

@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
