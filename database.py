# database.py (дополненный)
import sqlite3
import os

class Database:
    def __init__(self, db_name='Kruiz.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        
    
    def connect(self):
        """Подключение к базе данных"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """Отключение от базы данных"""
        if self.conn:
            self.conn.close()
    
    
    
    def check_user(self, login, password):
        """Проверка пользователя при авторизации"""
        self.connect()
        self.cursor.execute('SELECT * FROM Users WHERE login=? AND parol=?', (login, password))
        user = self.cursor.fetchone()
        self.disconnect()
        return user
    
    def get_all_tours(self):
        """Получение всех туров"""
        self.connect()
        self.cursor.execute('SELECT * FROM Turputevka ORDER BY "Код путевки"')
        tours = self.cursor.fetchall()
        self.disconnect()
        return tours
    
    def get_tour_by_id(self, tour_id):
        """Получение тура по ID"""
        self.connect()
        self.cursor.execute('SELECT * FROM Turputevka WHERE "Код путевки"=?', (tour_id,))
        tour = self.cursor.fetchone()
        self.disconnect()
        return tour
    
    def add_tour(self, data):
        """Добавление нового тура"""
        self.connect()
        self.cursor.execute('''
            INSERT INTO Turputevka (Страна, "Дата первого дня", Продолжительность, Транспорт, Питание, Программа, Цена, Фото)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['country'], data['date'], data['duration'], data['transport'], 
              data['food'], data['program'], data['price'], data['photo']))
        self.conn.commit()
        new_id = self.cursor.lastrowid
        self.disconnect()
        return new_id
    
    def update_tour(self, tour_id, data):
        """Обновление данных тура"""
        self.connect()
        self.cursor.execute('''
            UPDATE Turputevka 
            SET Страна=?, "Дата первого дня"=?, Продолжительность=?, Транспорт=?, 
                Питание=?, Программа=?, Цена=?, Фото=?
            WHERE "Код путевки"=?
        ''', (data['country'], data['date'], data['duration'], data['transport'],
              data['food'], data['program'], data['price'], data['photo'], tour_id))
        self.conn.commit()
        self.disconnect()
    
    def delete_tour(self, tour_id):
        """Удаление тура"""
        self.connect()
        self.cursor.execute('DELETE FROM Turputevka WHERE "Код путевки"=?', (tour_id,))
        self.conn.commit()
        self.disconnect()
    
    def get_all_clients(self):
        """Получение всех клиентов"""
        self.connect()
        self.cursor.execute('SELECT * FROM Klients ORDER BY "Код клиента"')
        clients = self.cursor.fetchall()
        self.disconnect()
        return clients
    
    def get_client_by_id(self, client_id):
        """Получение клиента по ID"""
        self.connect()
        self.cursor.execute('SELECT * FROM Klients WHERE "Код клиента"=?', (client_id,))
        client = self.cursor.fetchone()
        self.disconnect()
        return client
    
    def add_client(self, data):
        """Добавление нового клиента"""
        self.connect()
        self.cursor.execute('''
            INSERT INTO Klients (Фамилия, Имя, Отчество, Город, Адрес)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['lastname'], data['firstname'], data['middlename'], data['city'], data['address']))
        self.conn.commit()
        new_id = self.cursor.lastrowid
        self.disconnect()
        return new_id
    
    def update_client(self, client_id, data):
        """Обновление данных клиента"""
        self.connect()
        self.cursor.execute('''
            UPDATE Klients 
            SET Фамилия=?, Имя=?, Отчество=?, Город=?, Адрес=?
            WHERE "Код клиента"=?
        ''', (data['lastname'], data['firstname'], data['middlename'], data['city'], data['address'], client_id))
        self.conn.commit()
        self.disconnect()
    
    def delete_client(self, client_id):
        """Удаление клиента"""
        self.connect()
        self.cursor.execute('DELETE FROM Klients WHERE "Код клиента"=?', (client_id,))
        self.conn.commit()
        self.disconnect()
    
    def get_all_orders(self):
        """Получение всех заказов"""
        self.connect()
        self.cursor.execute('''
            SELECT z.*, t.Страна, t.Цена, k.Фамилия || ' ' || k.Имя as Клиент
            FROM Zakaz z
            LEFT JOIN Turputevka t ON z."Код путевки" = t."Код путевки"
            LEFT JOIN Klients k ON z."Код клиента" = k."Код клиента"
            ORDER BY z."Код заказа"
        ''')
        orders = self.cursor.fetchall()
        self.disconnect()
        return orders
    
    def add_order(self, data):
        """Добавление нового заказа"""
        self.connect()
        self.cursor.execute('''
            INSERT INTO Zakaz ("Код путевки", "Код клиента", Количество, "Дата заказа", Скидка)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['tour_id'], data['client_id'], data['quantity'], data['date'], data['discount']))
        self.conn.commit()
        new_id = self.cursor.lastrowid
        self.disconnect()
        return new_id
    
    def delete_order(self, order_id):
        """Удаление заказа"""
        self.connect()
        self.cursor.execute('DELETE FROM Zakaz WHERE "Код заказа"=?', (order_id,))
        self.conn.commit()
        self.disconnect()
