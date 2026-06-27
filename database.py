import sqlite3
from datetime import datetime

DB_NAME = "elonchi.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_conn()
    c = conn.cursor()

    # Foydalanuvchilar
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE,
        username TEXT,
        full_name TEXT,
        referral_by INTEGER DEFAULT NULL,
        joylar INTEGER DEFAULT 0,
        daraja TEXT DEFAULT 'standart',
        kunlik_harf INTEGER DEFAULT 0,
        oxirgi_kun TEXT DEFAULT NULL,
        blocked INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # E'lonlar
    c.execute('''CREATE TABLE IF NOT EXISTS elonlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matn TEXT,
        media_id TEXT DEFAULT NULL,
        media_type TEXT DEFAULT NULL,
        limit_son INTEGER DEFAULT 0,
        kirganlar INTEGER DEFAULT 0,
        boshlanish TEXT DEFAULT NULL,
        tugash TEXT DEFAULT NULL,
        menga_yozsin INTEGER DEFAULT 0,
        faol INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # E'longa kirganlar
    c.execute('''CREATE TABLE IF NOT EXISTS elon_kirganlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elon_id INTEGER,
        user_id INTEGER,
        joy_ishlatildi INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # Rejalashtirilgan e'lonlar
    c.execute('''CREATE TABLE IF NOT EXISTS rejalashtirilgan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        elon_id INTEGER,
        yuborish_vaqti TEXT,
        yuborildi INTEGER DEFAULT 0
    )''')

    conn.commit()
    conn.close()

# ─── USERS ───────────────────────────────────────────

def add_user(user_id, username, full_name, referral_by=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users 
                 (user_id, username, full_name, referral_by)
                 VALUES (?, ?, ?, ?)''',
              (user_id, username, full_name, referral_by))
    # Referral bonus
    if referral_by:
        c.execute('UPDATE users SET joylar = joylar + 1 WHERE user_id = ?', (referral_by,))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE blocked = 0')
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def update_daraja(user_id, daraja, joy_minus):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET daraja = ?, joylar = joylar - ? WHERE user_id = ?',
              (daraja, joy_minus, user_id))
    conn.commit()
    conn.close()

def get_joylar(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT joylar FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def minus_joy(user_id, son=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET joylar = joylar - ? WHERE user_id = ?', (son, user_id))
    conn.commit()
    conn.close()

def sovga_joy(from_id, to_id, son):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET joylar = joylar - ? WHERE user_id = ?', (son, from_id))
    c.execute('UPDATE users SET joylar = joylar + ? WHERE user_id = ?', (son, to_id))
    conn.commit()
    conn.close()

def block_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET blocked = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def unblock_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET blocked = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_kunlik_harf(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT kunlik_harf, oxirgi_kun, daraja FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return 0, 'standart'
    harf, kun, daraja = row
    bugun = datetime.now().strftime('%Y-%m-%d')
    if kun != bugun:
        # Yangi kun - reset
        reset_kunlik_harf(user_id)
        return 0, daraja
    return harf, daraja

def reset_kunlik_harf(user_id):
    conn = get_conn()
    c = conn.cursor()
    bugun = datetime.now().strftime('%Y-%m-%d')
    c.execute('UPDATE users SET kunlik_harf = 0, oxirgi_kun = ? WHERE user_id = ?', (bugun, user_id))
    conn.commit()
    conn.close()

def add_kunlik_harf(user_id, son):
    conn = get_conn()
    c = conn.cursor()
    bugun = datetime.now().strftime('%Y-%m-%d')
    c.execute('UPDATE users SET kunlik_harf = kunlik_harf + ?, oxirgi_kun = ? WHERE user_id = ?',
              (son, bugun, user_id))
    conn.commit()
    conn.close()

# ─── ELONLAR ─────────────────────────────────────────

def add_elon(matn, media_id, media_type, limit_son, boshlanish, tugash, menga_yozsin):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''INSERT INTO elonlar 
                 (matn, media_id, media_type, limit_son, boshlanish, tugash, menga_yozsin)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (matn, media_id, media_type, limit_son, boshlanish, tugash, menga_yozsin))
    elon_id = c.lastrowid
    conn.commit()
    conn.close()
    return elon_id

def get_elon(elon_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM elonlar WHERE id = ?', (elon_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_elonlar():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM elonlar ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_faol_elonlar():
    conn = get_conn()
    c = conn.cursor()
    bugun = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''SELECT * FROM elonlar WHERE faol = 1 
                 AND (tugash IS NULL OR tugash >= ?)
                 ORDER BY id DESC''', (bugun,))
    rows = c.fetchall()
    conn.close()
    return rows

def toggle_elon(elon_id, faol):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE elonlar SET faol = ? WHERE id = ?', (faol, elon_id))
    conn.commit()
    conn.close()

def kirgan_user(elon_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id FROM elon_kirganlar WHERE elon_id = ? AND user_id = ?', (elon_id, user_id))
    row = c.fetchone()
    conn.close()
    return row is not None

def add_kirgan(elon_id, user_id, joy_ishlatildi=0):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO elon_kirganlar (elon_id, user_id, joy_ishlatildi) VALUES (?, ?, ?)',
              (elon_id, user_id, joy_ishlatildi))
    c.execute('UPDATE elonlar SET kirganlar = kirganlar + 1 WHERE id = ?', (elon_id,))
    conn.commit()
    conn.close()
