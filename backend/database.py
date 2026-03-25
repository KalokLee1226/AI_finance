import sqlite3


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # 用户基础表（包含邮箱，用于告警推送）
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            salt TEXT,
            email TEXT
        )
    ''')

    # 迁移老库：如果历史 users 表中还没有 email 列，这里尝试补一列
    try:
        c.execute("PRAGMA table_info(users)")
        cols = [row[1] for row in c.fetchall()]
        if 'email' not in cols:
            c.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except Exception:
        # 迁移失败不影响服务启动，只是无法记录邮箱
        pass

    # 用户个性化设置（如自选品种）
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            commodities TEXT
        )
    ''')

    # AI 研报历史
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            commodity TEXT,
            report TEXT,
            created_at TEXT
        )
    ''')

    conn.commit()
    conn.close()