# app.py
import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from login import Ui_Form as LoginForm
from main import Ui_Form as MainForm
from database import Database
from dialogs import TourDialog, ClientDialog, OrderDialog

class ImageDelegate(QtWidgets.QStyledItemDelegate):
    """Делегат для отображения изображений в ячейке таблицы"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_cache = {}  # Кэш для загруженных изображений
    
    def paint(self, painter, option, index):
        if index.column() == 8:  # Колонка с фото
            image_path = index.data()
            if image_path and os.path.exists(image_path):
                # Загружаем изображение
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Масштабируем под размер ячейки
                    scaled_pixmap = pixmap.scaled(
                        option.rect.width() - 10, 
                        option.rect.height() - 10,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    
                    # Рисуем изображение по центру ячейки
                    x = option.rect.x() + (option.rect.width() - scaled_pixmap.width()) // 2
                    y = option.rect.y() + (option.rect.height() - scaled_pixmap.height()) // 2
                    painter.drawPixmap(x, y, scaled_pixmap)
                    return
        
        # Если изображения нет, рисуем стандартное содержимое
        super().paint(painter, option, index)

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = LoginForm()
        self.ui.setupUi(self)
        self.db = Database()
        
        # Подключение кнопки входа
        self.ui.pushButton.clicked.connect(self.login)
        
        # Добавляем обработку Enter
        self.ui.lineEdit.returnPressed.connect(self.login)
        self.ui.lineEdit_2.returnPressed.connect(self.login)
    
    def login(self):
        login = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        
        user = self.db.check_user(login, password)
        
        if user:
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")

class MainWindow(QtWidgets.QWidget):
    def __init__(self, user):
        super().__init__()
        self.ui = MainForm()
        self.ui.setupUi(self)
        self.db = Database()
        self.current_user = user
        self.current_table = 'tours'
        
        # Создаем папку для изображений, если её нет
        self.images_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
        
        # Настройка интерфейса
        self.setup_ui()
        
        # Загрузка данных
        self.load_data()
        
        # Подключение сигналов
        self.connect_signals()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Настройка comboBox
        self.ui.comboBox.addItem("Туры", "tours")
        self.ui.comboBox.addItem("Клиенты", "clients")
        self.ui.comboBox.addItem("Заказы", "orders")
        
        # Настройка таблицы
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget.setAlternatingRowColors(True)
        
        # Устанавливаем делегат для отображения изображений
        self.ui.tableWidget.setItemDelegate(ImageDelegate(self.ui.tableWidget))
        
        # Отображение роли пользователя
        self.setWindowTitle(f"Управление турами - {self.current_user['login']} ({self.current_user['role']})")
        
        # Ограничение прав для роли 'avtor'
        if self.current_user['role'] == 'avtor':
            self.ui.pushButton.setEnabled(False)  # Добавление
            self.ui.pushButton_2.setEnabled(False)  # Редактирование
            self.ui.pushButton_3.setEnabled(False)  # Удаление
    
    def connect_signals(self):
        """Подключение сигналов"""
        self.ui.comboBox.currentIndexChanged.connect(self.load_data)
        self.ui.pushButton.clicked.connect(self.add_record)
        self.ui.pushButton_2.clicked.connect(self.edit_record)
        self.ui.pushButton_3.clicked.connect(self.delete_record)
        self.ui.pushButton_4.clicked.connect(self.close)
        self.ui.tableWidget.doubleClicked.connect(self.edit_record)
    
    def load_data(self):
        """Загрузка данных в таблицу"""
        self.current_table = self.ui.comboBox.currentData()
        
        if self.current_table == 'tours':
            self.load_tours()
        elif self.current_table == 'clients':
            self.load_clients()
        elif self.current_table == 'orders':
            self.load_orders()
    
    def load_tours(self):
        """Загрузка туров"""
        tours = self.db.get_all_tours()
        
        # Настройка заголовков
        headers = ['Код', 'Страна', 'Дата', 'Дней', 'Транспорт', 'Питание', 'Программа', 'Цена', 'Фото']
        self.setup_table(len(tours), len(headers), headers)
        
        # Устанавливаем высоту строк для фото
        for row in range(len(tours)):
            self.ui.tableWidget.setRowHeight(row, 120)
        
        for row, tour in enumerate(tours):
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(tour['Код путевки'])))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(tour['Страна']))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(tour['Дата первого дня']))
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(str(tour['Продолжительность'])))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(tour['Транспорт']))
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(tour['Питание']))
            self.ui.tableWidget.setItem(row, 6, QTableWidgetItem(tour['Программа']))
            self.ui.tableWidget.setItem(row, 7, QTableWidgetItem(f"{tour['Цена']:.2f} ₽"))
            
            # Формируем путь к изображению
            photo_item = QTableWidgetItem()
            if tour['Фото']:
                photo_path = os.path.join(self.images_folder, tour['Фото'])
                if os.path.exists(photo_path):
                    photo_item.setData(Qt.DisplayRole, photo_path)
                else:
                    photo_item.setData(Qt.DisplayRole, "Нет фото")
                    photo_item.setBackground(QtGui.QColor(255, 200, 200))
            else:
                photo_item.setData(Qt.DisplayRole, "Нет фото")
                photo_item.setBackground(QtGui.QColor(255, 200, 200))
            
            self.ui.tableWidget.setItem(row, 8, photo_item)
    
    def load_clients(self):
        """Загрузка клиентов"""
        clients = self.db.get_all_clients()
        
        # Настройка заголовков
        headers = ['Код', 'Фамилия', 'Имя', 'Отчество', 'Город', 'Адрес']
        self.setup_table(len(clients), len(headers), headers)
        
        for row, client in enumerate(clients):
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(client['Код клиента'])))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(client['Фамилия']))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(client['Имя']))
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(client['Отчество']))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(client['Город']))
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(client['Адрес']))
    
    def load_orders(self):
        """Загрузка заказов"""
        orders = self.db.get_all_orders()
        
        # Настройка заголовков
        headers = ['Код', 'Тур', 'Клиент', 'Кол-во', 'Дата', 'Скидка', 'Сумма']
        self.setup_table(len(orders), len(headers), headers)
        
        for row, order in enumerate(orders):
            # Получаем данные для расчета суммы
            tour = self.db.get_tour_by_id(order['Код путевки'])
            price = tour['Цена'] if tour else 0
            quantity = order['Количество']
            discount = order['Скидка']
            
            # Расчет суммы со скидкой
            total = price * quantity * (1 - discount/100)
            
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(order['Код заказа'])))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(order['Страна']))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(order['Клиент']))
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(str(order['Количество'])))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(order['Дата заказа']))
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(f"{order['Скидка']}%"))
            self.ui.tableWidget.setItem(row, 6, QTableWidgetItem(f"{total:.2f} ₽"))
    
    def setup_table(self, row_count, col_count, headers):
        """Настройка таблицы"""
        self.ui.tableWidget.setRowCount(row_count)
        self.ui.tableWidget.setColumnCount(col_count)
        
        # Устанавливаем заголовки
        for col, header in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(header)
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(12)
            item.setFont(font)
            item.setBackground(QtGui.QColor(200, 200, 200))
            self.ui.tableWidget.setHorizontalHeaderItem(col, item)
    
    def add_record(self):
        """Добавление записи"""
        if self.current_table == 'tours':
            dialog = TourDialog(self, images_folder=self.images_folder)
            if dialog.exec_():
                self.load_tours()
                QMessageBox.information(self, "Успех", "Тур успешно добавлен")
        
        elif self.current_table == 'clients':
            dialog = ClientDialog(self)
            if dialog.exec_():
                self.load_clients()
                QMessageBox.information(self, "Успех", "Клиент успешно добавлен")
        
        elif self.current_table == 'orders':
            dialog = OrderDialog(self)
            if dialog.exec_():
                self.load_orders()
                QMessageBox.information(self, "Успех", "Заказ успешно добавлен")
    
    def edit_record(self):
        """Редактирование записи"""
        current_row = self.ui.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return
        
        record_id = self.ui.tableWidget.item(current_row, 0).text()
        
        if self.current_table == 'tours':
            tour = self.db.get_tour_by_id(record_id)
            if tour:
                dialog = TourDialog(self, tour, self.images_folder)
                if dialog.exec_():
                    self.load_tours()
                    QMessageBox.information(self, "Успех", "Тур успешно обновлен")
    
    def delete_record(self):
        """Удаление записи"""
        current_row = self.ui.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return
        
        reply = QMessageBox.question(self, "Подтверждение", 
                                     "Вы уверены, что хотите удалить запись?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            record_id = self.ui.tableWidget.item(current_row, 0).text()
            
            if self.current_table == 'tours':
                self.db.delete_tour(record_id)
                self.load_tours()
                QMessageBox.information(self, "Успех", "Тур успешно удален")

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Создание базы данных и заполнение тестовыми данными
    db = Database()
    init_test_data(db)
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())

def init_test_data(db):
    """Инициализация тестовых данных"""
    db.connect()
    
    # Проверяем, есть ли уже данные
    db.cursor.execute("SELECT COUNT(*) FROM Users")
    if db.cursor.fetchone()[0] == 0:
        # Добавляем тестовых пользователей
        users = [
            (1, 'Олег', '12345', 'admin'),
            (2, 'Маша', '23452', 'manager'),
            (3, 'Иван', '55555', 'avtor')
        ]
        db.cursor.executemany('INSERT INTO Users (id, login, parol, "role") VALUES (?, ?, ?, ?)', users)
        
        # Добавляем тестовых клиентов
        clients = [
            (1, 'Волков', 'Андрей', 'Валерьевич', 'Уфа', 'ул. Школьная д. 2'),
            (2, 'Петрова', 'Анна', 'Валерьевна', 'Москва', 'ул. Победы д. 4'),
            (3, 'Иванов', 'Иван', 'Васильевич', 'Самара', 'ул. Терешкова д. 10'),
        ]
        db.cursor.executemany('INSERT INTO Klients ("Код клиента", Фамилия, Имя, Отчество, Город, Адрес) VALUES (?, ?, ?, ?, ?, ?)', clients)
        
        # Добавляем тестовые туры
        tours = [
            (1, 'Япония', '2024-06-03', 7, 'Самолет', 'Да', 'Да', 65000.0, '1.jpg'),
            (2, 'Беларусь', '2024-06-06', 10, 'Поезд', 'Да', 'Нет', 50000.0, '2.jpg'),
            (3, 'Корея', '2024-06-09', 11, 'Корабль', 'Нет', 'Да', 70000.0, '3.jpg'),
        ]
        db.cursor.executemany('INSERT INTO Turputevka ("Код путевки", Страна, "Дата первого дня", Продолжительность, Транспорт, Питание, Программа, Цена, Фото) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', tours)
        
        db.conn.commit()
    
    db.disconnect()

if __name__ == "__main__":
    main()
