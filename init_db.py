from sqlite3 import connect

conn = connect('database.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS weekly_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    weekly_feedback TEXT,
    conflict TEXT,
    support TEXT,
    support_detail TEXT,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS daily_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    mood TEXT,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')


conn.commit()
conn.close()