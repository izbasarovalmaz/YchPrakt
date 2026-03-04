import sqlite3

connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()

# Подсчет общего числа пользователей
cursor.execute('SELECT COUNT(*) FROM Users')
total_users = cursor.fetchone()[0]

print('Общее количество пользователей:', total_users)
connection.close()


connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()

# Вычисление суммы возрастов пользователей
cursor.execute('SELECT SUM(age) FROM Users')
total_age = cursor.fetchone()[0]

print('Общая сумма возрастов пользователей:', total_age)
connection.close()


connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()

# Вычисление среднего возраста пользователей
cursor.execute('SELECT AVG(age) FROM Users')
average_age = cursor.fetchone()[0]

print('Средний возраст пользователей:', average_age)
connection.close()


connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()

# Нахождение минимального возраста
cursor.execute('SELECT MIN(age) FROM Users')
min_age = cursor.fetchone()[0]

print('Минимальный возраст среди пользователей:', min_age)
connection.close()

connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()

# Нахождение максимального возраста
cursor.execute('SELECT MAX(age) FROM Users')
max_age = cursor.fetchone()[0]
print('Максимальный возраст среди пользователей:', max_age)
connection.close()
