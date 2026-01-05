import sqlite3

DB_NAME = "vspo_cosplay.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 1. イベント参加テーブル
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, event_name TEXT, user_id INTEGER, char_name TEXT, costume TEXT)''')
    # 2. 資料リファレンス
    c.execute('''CREATE TABLE IF NOT EXISTS references
                 (id INTEGER PRIMARY KEY, char_name TEXT, url TEXT)''')
    # 3. 写真アーカイブ
    c.execute('''CREATE TABLE IF NOT EXISTS photos
                 (id INTEGER PRIMARY KEY, user_id INTEGER, url TEXT, char_name TEXT, likes INTEGER)''')
    conn.commit()
    conn.close()

# イベント参加登録
def add_event_entry(event_name, user_id, char_name, costume):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO events (event_name, user_id, char_name, costume) VALUES (?, ?, ?, ?)",
              (event_name, user_id, char_name, costume))
    conn.commit()
    conn.close()

# イベント参加者リスト取得
def get_event_participants(event_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id, char_name, costume FROM events WHERE event_name = ?", (event_name,))
    data = c.fetchall()
    conn.close()
    return data

# 写真保存
def save_photo(user_id, url, char_name="未設定"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO photos (user_id, url, char_name, likes) VALUES (?, ?, ?, 0)", 
              (user_id, url, char_name))
    conn.commit()
    conn.close()

# 資料検索
def search_reference(keyword):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT char_name, url FROM references WHERE char_name LIKE ?", (f'%{keyword}%',))
    data = c.fetchone()
    conn.close()
    return data

# 資料登録（管理者用）
def add_reference(char_name, url):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO references (char_name, url) VALUES (?, ?)", (char_name, url))
    conn.commit()
    conn.close()
