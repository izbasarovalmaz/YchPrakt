# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QFormLayout
import sqlite3

class AddRecordDialog(QDialog):
    """Диалог для добавления новой записи"""
    def __init__(self, table_name, columns, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.columns = columns
        self.inputs = {}
        self.setupUI()
        
    def setupUI(self):
        self.setWindowTitle(f"Добавление записи в {self.table_name}")
        layout = QFormLayout(self)
        
        # Создаем поля ввода для каждой колонки (кроме id)
        for col in self.columns:
            if col[1] != 'id':  # Пропускаем ID, он автоинкрементный
                self.inputs[col[1]] = QLineEdit()
                self.inputs[col[1]].setPlaceholderText(f"Введите {col[1]}")
                layout.addRow(f"{col[1]}:", self.inputs[col[1]])
        
        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def getData(self):
        """Возвращает введенные данные"""
        data = {}
        for col_name, input_field in self.inputs.items():
            data[col_name] = input_field.text()
        return data


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1104, 854)
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Таблица для отображения данных
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 90, 1071, 611))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        self.tableWidget.setFont(font)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setObjectName("tableWidget")
        
        # Кнопка "Закрыть"
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(900, 20, 161, 51))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("background-color: rgb(255, 0, 0); color: rgb(255, 255, 255);")
        self.pushButton.setObjectName("pushButton")
        
        # Кнопки управления
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)  # Добавить
        self.pushButton_2.setGeometry(QtCore.QRect(20, 710, 191, 61))
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.pushButton_2.setObjectName("pushButton_2")
        
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)  # Удалить
        self.pushButton_3.setGeometry(QtCore.QRect(230, 710, 191, 61))
        self.pushButton_3.setFont(font)
        self.pushButton_3.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.pushButton_3.setObjectName("pushButton_3")
        
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)  # Изменить
        self.pushButton_5.setGeometry(QtCore.QRect(440, 710, 191, 61))
        self.pushButton_5.setFont(font)
        self.pushButton_5.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.pushButton_5.setObjectName("pushButton_5")
        
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)  # Обновить
        self.pushButton_6.setGeometry(QtCore.QRect(640, 710, 191, 61))
        self.pushButton_6.setFont(font)
        self.pushButton_6.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.pushButton_6.setObjectName("pushButton_6")
        
        # Выпадающий список для выбора таблицы
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(60, 21, 171, 41))
        self.comboBox.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.comboBox.setObjectName("comboBox")
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Меню и статусбар
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1104, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        # Подключаем сигналы
        self.pushButton.clicked.connect(self.close)
        self.comboBox.currentTextChanged.connect(self.loadTable)
        self.pushButton_2.clicked.connect(self.add_record)
        self.pushButton_3.clicked.connect(self.delete_record)
        self.pushButton_5.clicked.connect(self.edit_record)
        self.pushButton_6.clicked.connect(self.refresh_table)
        
        self.retranslateUi(MainWindow)
        
        # Загружаем список таблиц
        self.loadTableNames()
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Управление базой данных"))
        self.pushButton.setText(_translate("MainWindow", "Закрыть"))
        self.pushButton_2.setText(_translate("MainWindow", "Добавить"))
        self.pushButton_3.setText(_translate("MainWindow", "Удалить"))
        self.pushButton_5.setText(_translate("MainWindow", "Изменить"))
        self.pushButton_6.setText(_translate("MainWindow", "Обновить"))

    def loadTableNames(self):
        """Загрузка списка таблиц из базы данных"""
        try:
            conn = sqlite3.connect('primer')
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.comboBox.clear()
            
            for table in tables:
                table_name = table[0]
                if not table_name.startswith('sqlite_'):
                    self.comboBox.addItem(table_name)
            
            conn.close()
            
            if self.comboBox.count() == 0:
                QMessageBox.information(self.MainWindow, "Информация", "В базе данных нет таблиц")
                
        except Exception as e:
            QMessageBox.critical(self.MainWindow, "Ошибка", f"Не удалось загрузить таблицы: {e}")

    def get_table_columns(self, table_name):
        """Получение информации о колонках таблицы"""
        try:
            conn = sqlite3.connect('primer')
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            conn.close()
            return columns
        except Exception as e:
            QMessageBox.critical(self.MainWindow, "Ошибка", f"Не удалось получить структуру таблицы: {e}")
            return []

    def loadTable(self, table_name):
        """Загрузка конкретной таблицы по имени"""
        if not table_name:
            return
            
        try:
            conn = sqlite3.connect('primer')
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if rows:
                self.tableWidget.setRowCount(len(rows))
                self.tableWidget.setColumnCount(len(rows[0]))
                
                cursor.execute(f"PRAGMA table_info({table_name})")
                headers = [column[1] for column in cursor.fetchall()]
                self.tableWidget.setHorizontalHeaderLabels(headers)
                
                for i, row in enumerate(rows):
                    for j, value in enumerate(row):
                        item = QtWidgets.QTableWidgetItem(str(value) if value is not None else "")
                        self.tableWidget.setItem(i, j, item)
                
                self.tableWidget.resizeColumnsToContents()
            else:
                self.tableWidget.setRowCount(0)
                self.tableWidget.setColumnCount(0)
            
            conn.close()
            self.statusbar.showMessage(f"Таблица '{table_name}' загружена")
            
        except Exception as e:
            QMessageBox.critical(self.MainWindow, "Ошибка", f"Не удалось загрузить таблицу: {e}")

    def add_record(self):
        """Добавление новой записи"""
        current_table = self.comboBox.currentText()
        if not current_table:
            QMessageBox.warning(self.MainWindow, "Предупреждение", "Выберите таблицу")
            return
        
        # Получаем структуру таблицы
        columns = self.get_table_columns(current_table)
        if not columns:
            return
        
        # Создаем диалог для ввода данных
        dialog = AddRecordDialog(current_table, columns, self.MainWindow)
        if dialog.exec_():
            data = dialog.getData()
            if not data:
                QMessageBox.warning(self.MainWindow, "Предупреждение", "Нет данных для добавления")
                return
            
            try:
                conn = sqlite3.connect('primer')
                cursor = conn.cursor()
                
                # Формируем SQL запрос
                columns_names = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                values = tuple(data.values())
                
                query = f"INSERT INTO {current_table} ({columns_names}) VALUES ({placeholders})"
                cursor.execute(query, values)
                conn.commit()
                conn.close()
                
                QMessageBox.information(self.MainWindow, "Успех", "Запись успешно добавлена")
                self.loadTable(current_table)  # Обновляем отображение
                
            except Exception as e:
                QMessageBox.critical(self.MainWindow, "Ошибка", f"Не удалось добавить запись: {e}")

    def delete_record(self):
        """Удаление выбранной записи"""
        current_table = self.comboBox.currentText()
        if not current_table:
            QMessageBox.warning(self.MainWindow, "Предупреждение", "Выберите таблицу")
            return
        
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self.MainWindow, "Предупреждение", "Выберите запись для удаления")
            return
        
        # Получаем ID записи (предполагаем, что первая колонка - ID)
        id_item = self.tableWidget.item(current_row, 0)
        if not id_item:
            QMessageBox.warning(self.MainWindow, "Предупреждение", "Не удалось определить ID записи")
            return
        
        record_id = id_item.text()
        
        # Подтверждение удаления
        reply = QMessageBox.question(self.MainWindow, "Подтверждение", 
                                      f"Удалить запись с ID {record_id}?",
                                      QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect('primer')
                cursor = conn.cursor()
                
                cursor.execute(f"DELETE FROM {current_table} WHERE id = ?", (record_id,))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self.MainWindow, "Успех", "Запись успешно удалена")
                self.loadTable(current_table)  # Обновляем отображение
                
            except Exception as e:
                QMessageBox.critical(self.MainWindow, "Ошибка", f"Не удалось удалить запись: {e}")

    def edit_record(self):
        """Редактирование выбранной записи"""
        current_table = self.comboBox.currentText()
        if not current_table:
            QMessageBox.warning(self.MainWindow, "Предупреждение", "Выберите таблицу")
            return
        
        current_row = self.tableWidget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self.MainWindow, "Предупреждение", "Выберите запись для редактирования")
            return
        
        # Получаем ID записи
        id_item = self.tableWidget.item(current_row, 0)
        if not id_item:
            QMessageBox.warning(self.MainWindow, "Предупреждение", "Не удалось определить ID записи")
            return
        
        record_id = id_item.text()
        
        # Получаем структуру таблицы
        columns = self.get_table_columns(current_table)
        if not columns:
            return
        
        # Получаем текущие значения
        current_values = {}
        for j, col in enumerate(columns):
            if col[1] != 'id':  # Пропускаем ID
                item = self.tableWidget.item(current_row, j)
                current_values[col[1]] = item.text() if item else ""
        
        # Диалог редактирования
        dialog = AddRecordDialog(current_table, columns, self.MainWindow)
        
        # Заполняем поля текущими значениями
        for col_name, input_field in dialog.inputs.items():
            if col_name in current_values:
                input_field.setText(current_values[col_name])
        
        if dialog.exec_():
            new_data = dialog.getData()
            
            try:
                conn = sqlite3.connect('primer')
                cursor = conn.cursor()
                
                # Формируем запрос на обновление
                set_clause = ', '.join([f"{col} = ?" for col in new_data.keys()])
                values = tuple(new_data.values()) + (record_id,)
                
                query = f"UPDATE {current_table} SET {set_clause} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                conn.close()
                
                QMessageBox.information(self.MainWindow, "Успех", "Запись успешно обновлена")
                self.loadTable(current_table)  # Обновляем отображение
                
            except Exception as e:
                QMessageBox.critical(self.MainWindow, "Ошибка", f"Не удалось обновить запись: {e}")

    def refresh_table(self):
        """Обновление текущей таблицы"""
        current_table = self.comboBox.currentText()
        if current_table:
            self.loadTable(current_table)
            self.statusbar.showMessage(f"Таблица '{current_table}' обновлена")

    def close(self):
        """Закрытие окна"""
        if self.MainWindow:
            self.MainWindow.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
