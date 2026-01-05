import sqlite3
import datetime

DB_NAME = "vspo_cosplay.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 既存のイベントテーブル
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, event_name TEXT, user_id INTEGER, char_name TEXT, costume TEXT)''')
    
    # 【変更】三面図テーブルに costume_name を追加
    c.execute('''CREATE TABLE IF NOT EXISTS cosplay_refs
                 (id INTEGER PRIMARY KEY, char_name TEXT, costume_name TEXT, url TEXT)''')
                 
    # 写真テーブル
    c.execute('''CREATE TABLE IF NOT EXISTS photos
                 (id INTEGER PRIMARY KEY, user_id INTEGER, url TEXT, char_name TEXT, likes INTEGER)''')
    
    # カレンダーテーブル
    c.execute('''CREATE TABLE IF NOT EXISTS event_schedule
                 (id INTEGER PRIMARY KEY, name TEXT, date TEXT, region TEXT, place TEXT)''')
                 
    conn.commit()
    conn.close()

# --- イベント系（変更なし） ---
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
    c.execute("SELECT date, name, place FROM event_schedule WHERE region = ? AND date >= date('now') ORDER BY date ASC", (region,))
    data = c.fetchall()
    conn.close()
    return data

# --- 【ここを変更】三面図機能 ---

# 検索時に「全て」取得するように変更 (fetchall)
def search_reference(keyword):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # キャラ名にキーワードが含まれるものを全件取得
    c.execute("SELECT char_name, costume_name, url FROM cosplay_refs WHERE char_name LIKE ?", (f'%{keyword}%',))
    data = c.fetchall()
    conn.close()
    return data

# 登録時に「衣装名」も保存するように変更
def add_reference(char_name, costume_name, url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO cosplay_refs (char_name, costume_name, url) VALUES (?, ?, ?)", (char_name, costume_name, url))
    conn.commit()
    conn.close()
