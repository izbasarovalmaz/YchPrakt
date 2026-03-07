# dialogs.py
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPushButton, QMessageBox, QDateEdit, QFileDialog
from PyQt5.QtCore import QDate, Qt
import os
import shutil
from PyQt5.QtGui import QPixmap
class BaseDialog(QDialog):
    """Базовый класс для диалогов"""
    def __init__(self, parent=None, title="", data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(450, 500)
        self.data = data
        self.fields = {}
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout()
        
        # Форма
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setSpacing(10)
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        layout.addLayout(self.form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.cancel_button = QPushButton("Отмена")
        
        self.save_button.clicked.connect(self.save)
        self.cancel_button.clicked.connect(self.reject)
        
        # Стили для кнопок
        self.save_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.cancel_button.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def add_field(self, name, label, widget):
        """Добавление поля в форму"""
        self.fields[name] = widget
        self.form_layout.addRow(QLabel(label), widget)
    
    def load_data(self):
        """Загрузка данных в поля"""
        if self.data:
            for key, value in dict(self.data).items():
                if key in self.fields:
                    widget = self.fields[key]
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value) if value else "")
                    elif isinstance(widget, QComboBox):
                        index = widget.findText(str(value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    elif isinstance(widget, QSpinBox):
                        widget.setValue(int(value) if value else 0)
                    elif isinstance(widget, QDoubleSpinBox):
                        widget.setValue(float(value) if value else 0.0)
                    elif isinstance(widget, QDateEdit):
                        try:
                            date = QDate.fromString(str(value), "yyyy-MM-dd")
                            if date.isValid():
                                widget.setDate(date)
                        except:
                            widget.setDate(QDate.currentDate())
    
    def save(self):
        """Сохранение данных (должен быть переопределен)"""
        self.accept()

class TourDialog(BaseDialog):
    """Диалог для добавления/редактирования тура с выбором изображения"""
    def __init__(self, parent=None, tour_data=None, images_folder=None):
        self.images_folder = images_folder
        self.selected_image_path = None
        super().__init__(parent, "Редактирование тура" if tour_data else "Добавление тура", tour_data)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Поля для тура
        self.add_field('country', 'Страна:', QLineEdit())
        self.add_field('date', 'Дата первого дня:', QDateEdit())
        self.add_field('duration', 'Продолжительность (дней):', QSpinBox())
        self.add_field('transport', 'Транспорт:', QComboBox())
        self.add_field('food', 'Питание:', QComboBox())
        self.add_field('program', 'Программа:', QComboBox())
        self.add_field('price', 'Цена (₽):', QDoubleSpinBox())
        
        # Поле для фото с кнопкой выбора
        photo_layout = QHBoxLayout()
        self.photo_edit = QLineEdit()
        self.photo_edit.setReadOnly(True)
        self.photo_edit.setPlaceholderText("Выберите изображение...")
        self.photo_button = QPushButton("Обзор...")
        self.photo_button.clicked.connect(self.select_image)
        self.photo_button.setMaximumWidth(80)
        
        photo_layout.addWidget(self.photo_edit)
        photo_layout.addWidget(self.photo_button)
        
        photo_widget = QtWidgets.QWidget()
        photo_widget.setLayout(photo_layout)
        self.add_field('photo', 'Фото:', photo_widget)
        self.fields['photo'] = self.photo_edit
        
        # Предпросмотр изображения
        self.preview_label = QLabel()
        self.preview_label.setMinimumHeight(100)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.form_layout.addRow(QLabel("Предпросмотр:"), self.preview_label)
        
        # Настройка полей
        self.fields['date'].setDate(QDate.currentDate())
        self.fields['date'].setCalendarPopup(True)
        
        self.fields['duration'].setRange(1, 365)
        self.fields['duration'].setValue(7)
        
        transport_combo = self.fields['transport']
        transport_combo.addItems(['Самолет', 'Поезд', 'Корабль', 'Автобус', 'Автомобиль'])
        
        yes_no_combo1 = self.fields['food']
        yes_no_combo1.addItems(['Да', 'Нет'])
        
        yes_no_combo2 = self.fields['program']
        yes_no_combo2.addItems(['Да', 'Нет'])
        
        self.fields['price'].setRange(0, 1000000)
        self.fields['price'].setValue(50000)
        self.fields['price'].setSingleStep(1000)
    
    def select_image(self):
        """Выбор изображения для тура"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите изображение", 
            "", 
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.photo_edit.setText(os.path.basename(file_path))
            
            # Показываем предпросмотр
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(scaled_pixmap)
    
    def load_data(self):
        """Загрузка данных тура"""
        super().load_data()
        
        if self.data and self.data['Фото']:
            # Загружаем предпросмотр существующего изображения
            photo_path = os.path.join(self.images_folder, self.data['Фото'])
            if os.path.exists(photo_path):
                pixmap = QPixmap(photo_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.preview_label.setPixmap(scaled_pixmap)
    
    def save(self):
        """Сохранение тура"""
        data = {
            'country': self.fields['country'].text(),
            'date': self.fields['date'].date().toString("yyyy-MM-dd"),
            'duration': self.fields['duration'].value(),
            'transport': self.fields['transport'].currentText(),
            'food': self.fields['food'].currentText(),
            'program': self.fields['program'].currentText(),
            'price': self.fields['price'].value(),
            'photo': self.fields['photo'].text()
        }
        
        # Проверка заполнения
        if not data['country']:
            QMessageBox.warning(self, "Ошибка", "Введите страну")
            return
        
        # Если выбрано новое изображение, копируем его в папку images
        if self.selected_image_path and self.images_folder:
            # Генерируем уникальное имя файла
            import uuid
            file_ext = os.path.splitext(self.selected_image_path)[1]
            new_filename = f"{uuid.uuid4().hex}{file_ext}"
            new_path = os.path.join(self.images_folder, new_filename)
            
            try:
                shutil.copy2(self.selected_image_path, new_path)
                data['photo'] = new_filename
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось скопировать изображение: {str(e)}")
                return
        
        if not data['photo']:
            data['photo'] = "default.jpg"
        
        try:
            if self.data:
                # Обновление существующего тура
                self.parent().db.update_tour(self.data['Код путевки'], data)
            else:
                # Добавление нового тура
                self.parent().db.add_tour(data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить тур: {str(e)}")

class ClientDialog(BaseDialog):
    """Диалог для добавления/редактирования клиента"""
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent, "Редактирование клиента" if client_data else "Добавление клиента", client_data)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Поля для клиента
        self.add_field('lastname', 'Фамилия:', QLineEdit())
        self.add_field('firstname', 'Имя:', QLineEdit())
        self.add_field('middlename', 'Отчество:', QLineEdit())
        self.add_field('city', 'Город:', QLineEdit())
        self.add_field('address', 'Адрес:', QLineEdit())
        
        # Устанавливаем плейсхолдеры
        self.fields['lastname'].setPlaceholderText("Иванов")
        self.fields['firstname'].setPlaceholderText("Иван")
        self.fields['middlename'].setPlaceholderText("Иванович")
        self.fields['city'].setPlaceholderText("Москва")
        self.fields['address'].setPlaceholderText("ул. Пушкина д. 10")
    
    def save(self):
        """Сохранение клиента"""
        data = {
            'lastname': self.fields['lastname'].text().strip(),
            'firstname': self.fields['firstname'].text().strip(),
            'middlename': self.fields['middlename'].text().strip(),
            'city': self.fields['city'].text().strip(),
            'address': self.fields['address'].text().strip()
        }
        
        # Проверка заполнения
        if not data['lastname']:
            QMessageBox.warning(self, "Ошибка", "Фамилия обязательна для заполнения")
            return
        
        if not data['firstname']:
            QMessageBox.warning(self, "Ошибка", "Имя обязательно для заполнения")
            return
        
        try:
            if self.data:
                # Обновление существующего клиента
                self.parent().db.update_client(self.data['Код клиента'], data)
            else:
                # Добавление нового клиента
                self.parent().db.add_client(data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить клиента: {str(e)}")

class OrderDialog(BaseDialog):
    """Диалог для добавления заказа"""
    def __init__(self, parent=None, order_data=None):
        super().__init__(parent, "Добавление заказа", order_data)
    
    def setup_ui(self):
        super().setup_ui()
        
        # Загружаем туры и клиентов
        tours = self.parent().db.get_all_tours()
        clients = self.parent().db.get_all_clients()
        
        # Поля для заказа
        self.add_field('tour', 'Тур:', QComboBox())
        self.add_field('client', 'Клиент:', QComboBox())
        self.add_field('quantity', 'Количество:', QSpinBox())
        self.add_field('date', 'Дата заказа:', QDateEdit())
        self.add_field('discount', 'Скидка (%):', QSpinBox())
        
        # Заполнение комбобоксов
        tour_combo = self.fields['tour']
        for tour in tours:
            tour_combo.addItem(f"{tour['Страна']} - {tour['Дата первого дня']} - {tour['Цена']} ₽", tour['Код путевки'])
        
        client_combo = self.fields['client']
        for client in clients:
            client_combo.addItem(f"{client['Фамилия']} {client['Имя']} {client['Отчество'] or ''}", client['Код клиента'])
        
        # Настройка полей
        self.fields['quantity'].setRange(1, 10)
        self.fields['quantity'].setValue(1)
        
        self.fields['date'].setDate(QDate.currentDate())
        self.fields['date'].setCalendarPopup(True)
        
        self.fields['discount'].setRange(0, 100)
        self.fields['discount'].setValue(0)
        self.fields['discount'].setSuffix("%")
    
    def save(self):
        """Сохранение заказа"""
        data = {
            'tour_id': self.fields['tour'].currentData(),
            'client_id': self.fields['client'].currentData(),
            'quantity': self.fields['quantity'].value(),
            'date': self.fields['date'].date().toString("yyyy-MM-dd"),
            'discount': self.fields['discount'].value()
        }
        
        # Проверка
        if data['tour_id'] is None:
            QMessageBox.warning(self, "Ошибка", "Выберите тур")
            return
        
        if data['client_id'] is None:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента")
            return
        
        try:
            # Добавление заказа
            self.parent().db.add_order(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать заказ: {str(e)}")
