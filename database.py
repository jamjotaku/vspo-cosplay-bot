import sqlite3
import datetime

DB_NAME = "vspo_cosplay.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. イベント参加表明用
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, event_name TEXT, user_id INTEGER, char_name TEXT, costume TEXT)''')
    
    # 2. 三面図共有用（衣装名を追加済み）
    c.execute('''CREATE TABLE IF NOT EXISTS cosplay_refs
                 (id INTEGER PRIMARY KEY, char_name TEXT, costume_name TEXT, url TEXT)''')
    
    # 3. 写真共有用
    c.execute('''CREATE TABLE IF NOT EXISTS photos
                 (id INTEGER PRIMARY KEY, user_id INTEGER, url TEXT, char_name TEXT, likes INTEGER)''')
    
    # 4. イベントカレンダー用
    c.execute('''CREATE TABLE IF NOT EXISTS event_schedule
                 (id INTEGER PRIMARY KEY, name TEXT, date TEXT, region TEXT, place TEXT)''')
                 
    conn.commit()
    conn.close()

# --- 参加表明機能 ---
def add_event_entry(event_name, user_id, char_name, costume):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO events (event_name, user_id, char_name, costume) VALUES (?, ?, ?, ?)",
              (event_name, user_id, char_name, costume))
    conn.commit()
    conn.close()

def get_event_participants(event_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id, char_name, costume FROM events WHERE event_name = ?", (event_name,))
    data = c.fetchall()
    conn.close()
    return data

# --- 写真共有機能 ---
def save_photo(user_id, url, char_name="未設定"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO photos (user_id, url, char_name, likes) VALUES (?, ?, ?, 0)", 
              (user_id, url, char_name))
    conn.commit()
    conn.close()

# --- 三面図機能（アップグレード版） ---
def search_reference(keyword):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 複数ヒットに対応するため fetchall を使用
    c.execute("SELECT char_name, costume_name, url FROM cosplay_refs WHERE char_name LIKE ?", (f'%{keyword}%',))
    data = c.fetchall()
    conn.close()
    return data

def add_reference(char_name, costume_name, url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO cosplay_refs (char_name, costume_name, url) VALUES (?, ?, ?)", (char_name, costume_name, url))
    conn.commit()
    conn.close()

# --- カレンダー機能 ---
def add_schedule_item(name, date, region, place):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO event_schedule (name, date, region, place) VALUES (?, ?, ?, ?)",
              (name, date, region, place))
    conn.commit()
    conn.close()

def get_schedule_by_region(region):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 今日の日付以降のみ取得
    c.execute("SELECT date, name, place FROM event_schedule WHERE region = ? AND date >= date('now') ORDER BY date ASC", (region,))
    data = c.fetchall()
    conn.close()
    return data
