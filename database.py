import sqlite3
import datetime

DB_NAME = "vspo_cosplay.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 既存のテーブル
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, event_name TEXT, user_id INTEGER, char_name TEXT, costume TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS cosplay_refs
                 (id INTEGER PRIMARY KEY, char_name TEXT, url TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS photos
                 (id INTEGER PRIMARY KEY, user_id INTEGER, url TEXT, char_name TEXT, likes INTEGER)''')
    
    # 【追加】イベントスケジュール用テーブル
    c.execute('''CREATE TABLE IF NOT EXISTS event_schedule
                 (id INTEGER PRIMARY KEY, name TEXT, date TEXT, region TEXT, place TEXT)''')
                 
    conn.commit()
    conn.close()

# --- (既存の関数はそのまま) ---
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

def save_photo(user_id, url, char_name="未設定"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO photos (user_id, url, char_name, likes) VALUES (?, ?, ?, 0)", 
              (user_id, url, char_name))
    conn.commit()
    conn.close()

def search_reference(keyword):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT char_name, url FROM cosplay_refs WHERE char_name LIKE ?", (f'%{keyword}%',))
    data = c.fetchone()
    conn.close()
    return data

def add_reference(char_name, url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO cosplay_refs (char_name, url) VALUES (?, ?)", (char_name, url))
    conn.commit()
    conn.close()

# --- 【以下、カレンダー機能用の新機能を追加】 ---

# イベントスケジュールの登録
def add_schedule_item(name, date, region, place):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO event_schedule (name, date, region, place) VALUES (?, ?, ?, ?)",
              (name, date, region, place))
    conn.commit()
    conn.close()

# 地域別のイベント取得（日付順）
def get_schedule_by_region(region):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 今日の日付を取得して、終わったイベントは表示しないようにする（>= date('now')）
    # もし過去も含めたいなら WHERE region = ? だけにする
    c.execute("SELECT date, name, place FROM event_schedule WHERE region = ? AND date >= date('now') ORDER BY date ASC", (region,))
    data = c.fetchall()
    conn.close()
    return data
