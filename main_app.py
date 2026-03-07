# main_app.py
import sys
import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
import os

# Импортируем сгенерированные UI классы
from login import Ui_Form as LoginForm
from main import Ui_Form as MainForm


class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = LoginForm()
        self.ui.setupUi(self)
        
        # Подключаем кнопку входа
        self.ui.pushButton.clicked.connect(self.check_login)
        
        # Подключаем обработку нажатия Enter в полях ввода
        self.ui.lineEdit.returnPressed.connect(self.check_login)
        self.ui.lineEdit_2.returnPressed.connect(self.check_login)
        
        # Устанавливаем режим пароля для второго поля
        self.ui.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        
        # Переменная для хранения роли пользователя
        self.user_role = None
        
    def check_login(self):
        login = self.ui.lineEdit.text()
        password = self.ui.lineEdit_2.text()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        
        # Подключаемся к базе данных
        try:
            conn = sqlite3.connect('Kruiz.db')
            cursor = conn.cursor()
            
            # Проверяем пользователя
            cursor.execute('''
                SELECT role FROM Users 
                WHERE login = ? AND parol = ?
            ''', (login, password))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                self.user_role = result[0]
                self.open_main_window()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {str(e)}")
    
    def open_main_window(self):
        self.main_window = MainWindow(self.user_role)
        self.main_window.show()
        self.close()


class TourItemWidget(QtWidgets.QWidget):
    """Виджет для отображения одного тура в стиле предоставленного изображения"""
    
    def __init__(self, tour_data, parent=None):
        super().__init__(parent)
        self.tour_data = tour_data
        self.setup_ui()
        
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Создаем основной контейнер с рамкой
        main_frame = QtWidgets.QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background-color: rgb(240, 240, 240);
                border: 2px solid rgb(100, 100, 100);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        frame_layout = QtWidgets.QVBoxLayout(main_frame)
        
        # Заголовок - Страна и тип тура
        title_label = QtWidgets.QLabel(f"{self.tour_data[1]} | Тур")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: rgb(50, 50, 50);
            padding: 5px;
            background-color: rgb(200, 230, 255);
            border-radius: 3px;
        """)
        frame_layout.addWidget(title_label)
        
        # Информация о туре
        info_text = f"""
        Описание тура: {self.tour_data[6] if self.tour_data[6] else 'Нет описания'}
        Транспорт: {self.tour_data[4]}
        Питание: {'Включено' if self.tour_data[5] == 'Да' else 'Не включено'}
        Цена: {self.tour_data[7]:.2f} руб.
        Продолжительность: {self.tour_data[3]} дней
        Первый день: {self.tour_data[2]}
        """
        
        info_label = QtWidgets.QLabel(info_text)
        info_label.setStyleSheet("""
            font-size: 14px;
            color: rgb(0, 0, 0);
            padding: 5px;
            background-color: white;
            border: 1px solid rgb(150, 150, 150);
            border-radius: 3px;
        """)
        info_label.setWordWrap(True)
        frame_layout.addWidget(info_label)
        
        # Количество на складе (в данном случае - доступность тура)
        stock_text = f"Доступно мест: {self.tour_data[8] if len(self.tour_data) > 8 else 'Уточняйте'}"
        stock_label = QtWidgets.QLabel(stock_text)
        stock_label.setStyleSheet("""
            font-size: 14px;
            color: rgb(0, 100, 0);
            font-weight: bold;
            padding: 3px;
            background-color: rgb(200, 255, 200);
            border-radius: 3px;
        """)
        frame_layout.addWidget(stock_label)
        
        layout.addWidget(main_frame)
        
        # Устанавливаем фиксированную высоту для виджета
        self.setFixedHeight(250)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, user_role):
        super().__init__()
        self.ui = MainForm()
        self.ui.setupUi(self)
        self.user_role = user_role
        
        # Настраиваем таблицу для отображения туров
        self.setup_table()
        
        # Подключаем кнопки
        self.ui.pushButton_4.clicked.connect(self.close)  # Закрыть
        self.ui.pushButton.clicked.connect(self.add_tour)
        self.ui.pushButton_2.clicked.connect(self.edit_tour)
        self.ui.pushButton_3.clicked.connect(self.delete_tour)
        
        # Настраиваем комбобокс
        self.ui.comboBox.addItems(["Все туры", "По стране", "По цене", "По дате"])
        
        # Загружаем данные
        self.load_tours()
        
        # Настраиваем права доступа
        self.setup_permissions()
        
    def setup_table(self):
        """Настраиваем таблицу для отображения туров"""
        # Устанавливаем количество колонок
        self.ui.tableWidget.setColumnCount(1)
        
        # Настраиваем заголовки
        self.ui.tableWidget.horizontalHeader().setVisible(False)
        self.ui.tableWidget.verticalHeader().setVisible(False)
        
        # Растягиваем колонку на всю ширину
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Убираем сетку
        self.ui.tableWidget.setShowGrid(False)
        
        # Настраиваем выделение
        self.ui.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
    def setup_permissions(self):
        """Настраиваем права доступа в зависимости от роли"""
        if self.user_role == 'avtor':
            # Автор может только просматривать
            self.ui.pushButton.setEnabled(False)  # Добавить
            self.ui.pushButton_2.setEnabled(False)  # Редактировать
            self.ui.pushButton_3.setEnabled(False)  # Удалить
        elif self.user_role == 'manager':
            # Менеджер может добавлять и редактировать
            self.ui.pushButton.setEnabled(True)
            self.ui.pushButton_2.setEnabled(True)
            self.ui.pushButton_3.setEnabled(False)  # Но не удалять
        elif self.user_role == 'admin':
            # Администратор может всё
            self.ui.pushButton.setEnabled(True)
            self.ui.pushButton_2.setEnabled(True)
            self.ui.pushButton_3.setEnabled(True)
    
    def load_tours(self):
        """Загружает туры из базы данных"""
        try:
            conn = sqlite3.connect('Kruiz.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT "Код путевки", Страна, "Дата первого дня", 
                       Продолжительность, Транспорт, Питание, 
                       Программа, Цена, Фото 
                FROM Turputevka
                ORDER BY "Код путевки"
            ''')
            
            tours = cursor.fetchall()
            conn.close()
            
            # Очищаем таблицу
            self.ui.tableWidget.setRowCount(0)
            
            # Заполняем таблицу
            for i, tour in enumerate(tours):
                self.ui.tableWidget.insertRow(i)
                
                # Создаем виджет для тура
                tour_widget = TourItemWidget(tour)
                
                # Создаем контейнер для центрирования
                container = QtWidgets.QWidget()
                container_layout = QtWidgets.QHBoxLayout(container)
                container_layout.addWidget(tour_widget)
                container_layout.setAlignment(Qt.AlignCenter)
                
                # Устанавливаем виджет в ячейку
                self.ui.tableWidget.setCellWidget(i, 0, container)
                
                # Устанавливаем высоту строки
                self.ui.tableWidget.setRowHeight(i, 260)
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка загрузки данных: {str(e)}")
    
    def add_tour(self):
        """Добавление нового тура"""
        QMessageBox.information(self, "Добавление", "Функция добавления тура будет реализована")
        # Здесь будет код для открытия окна добавления тура
    
    def edit_tour(self):
        """Редактирование выбранного тура"""
        current_row = self.ui.tableWidget.currentRow()
        if current_row >= 0:
            # Получаем данные тура (можно сохранять код путевки в теге)
            QMessageBox.information(self, "Редактирование", "Функция редактирования тура будет реализована")
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите тур для редактирования")
    
    def delete_tour(self):
        """Удаление выбранного тура"""
        current_row = self.ui.tableWidget.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, 
                "Подтверждение", 
                "Вы уверены, что хотите удалить этот тур?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Здесь будет код удаления
                QMessageBox.information(self, "Удаление", "Тур удален")
                self.load_tours()  # Перезагружаем список
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите тур для удаления")


def create_database():
    """Создает базу данных и таблицы, если они не существуют"""
    try:
        conn = sqlite3.connect('Kruiz.db')
        cursor = conn.cursor()
        
        # Читаем SQL скрипт
        with open('script.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Выполняем скрипт
        cursor.executescript(sql_script)
        
        # Проверяем, есть ли данные в таблице Users
        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] == 0:
            # Добавляем тестовых пользователей
            users_data = [
                (1, 'Олег', '12345', 'admin'),
                (2, 'Маша', '23452', 'manager'),
                (3, 'Иван', '55555', 'avtor')
            ]
            cursor.executemany('INSERT OR REPLACE INTO Users (id, login, parol, role) VALUES (?,?,?,?)', users_data)
            
            # Добавляем тестовые туры
            tours_data = [
                (1, 'Япония', '2024-06-03', 7, 'Самолет', 'Да', 'Экскурсионный тур по Токио и Киото', 65000.0, '1.jpg', 10),
                (2, 'Беларусь', '2024-06-06', 10, 'Поезд', 'Да', 'Обзорная экскурсия по Минску', 50000.0, '2.jpg', 15),
                (3, 'Корея', '2024-06-09', 11, 'Корабль', 'Нет', 'Тур в Сеул с посещением достопримечательностей', 70000.0, '3.jpg', 8),
            ]
            cursor.executemany('''
                INSERT OR REPLACE INTO Turputevka 
                ("Код путевки", Страна, "Дата первого дня", Продолжительность, Транспорт, Питание, Программа, Цена, Фото) 
                VALUES (?,?,?,?,?,?,?,?,?)
            ''', tours_data)
        
        conn.commit()
        conn.close()
        print("База данных успешно создана/обновлена")
        
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Создаем базу данных при первом запуске
    if not os.path.exists('Kruiz.db'):
        create_database()
    
    # Запускаем окно авторизации
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())