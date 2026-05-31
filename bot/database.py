import sqlite3

def init_db():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            ip TEXT,
            ssh_user TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_server(user_id, name, ip, ssh_user, password):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO servers (user_id, name, ip, ssh_user, password) VALUES (?, ?, ?, ?, ?)', 
        (user_id, name, ip, ssh_user, password)
    )
    conn.commit()
    conn.close()

def get_servers(user_id):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    # Возвращаем все поля, включая пароль
    cursor.execute('SELECT id, name, ip, ssh_user, password FROM servers WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_server(server_id, user_id):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM servers WHERE id = ? AND user_id = ?', (server_id, user_id))
    conn.commit()
    conn.close()
