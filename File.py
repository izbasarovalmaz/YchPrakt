import sqlite3

# Единое соединение с базой данных
connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()

# 1. Создаем таблицу Users (с колонкой is_active)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 2. Создаем индекс для столбца "username"
cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON Users (username)')

# 3. Создаем представление для активных пользователей
cursor.execute('''
    CREATE VIEW IF NOT EXISTS ActiveUsers AS 
    SELECT * FROM Users WHERE is_active = 1
''')

# 4. Создаем триггер (исправленный)
cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_created_at 
    AFTER INSERT ON Users 
    BEGIN 
        UPDATE Users SET created_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.id AND NEW.created_at IS NULL; 
    END;
''')

# Сохраняем изменения
connection.commit()

# 5. Подготовленный запрос (после создания таблицы)
query = 'SELECT * FROM Users WHERE age > ?'
cursor.execute(query, (25,))
users = cursor.fetchall()
print("Пользователи старше 25 лет:")
for user in users:
    print(user)

# 6. Запрос через представление
cursor.execute('SELECT * FROM ActiveUsers')
active_users = cursor.fetchall()
print("\nАктивные пользователи:")
for user in active_users:
    print(user)

# Закрываем соединение
connection.close()
