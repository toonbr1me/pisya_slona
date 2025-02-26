from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QMessageBox, QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QDialog, QFormLayout, QDialogButtonBox, QCalendarWidget, QDateEdit, QSpinBox, QTabWidget, QComboBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QDate
from PyQt5 import uic
import pymysql
import sys
import os
import pandas as pd

class BaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load UI file
        uic.loadUi("main.ui", self)
        self.setWindowTitle("Суп - Система управления партнерами")  # Fixed title
        self.setWindowIcon(QIcon("Ресурсы/Мастер пол.png"))
        
        # Apply color scheme
        self.setStyleSheet("""
            QMainWindow, QScrollArea, QWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QLabel#label_page {
                background-color: #F4E8D3;
                color: #000000;
                padding: 5px;
                border: 1px solid #000000;
            }
            QPushButton {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
            }
            QPushButton:hover {
                background-color: #E8D8BA;
            }
        """)
        
        # Database connection string
        self.host = "t1brime-dev.ru"
        self.port = 3306
        self.user = "toonbrime"
        self.password = "Bebra228"
        self.db = "CBO"
        
        # Data variables
        self.data_db = []
        self.current_number_page = 0
        self.number_page_elements = 10
        
        # Connect widgets
        self.connect_widgets()
        
        # Show data
        self.show_data()
    
    def connect_widgets(self):
        """Connect signals to slots"""
        self.button_add.clicked.connect(lambda: self.call_form('add'))
        self.button_delete.clicked.connect(lambda: self.call_form('delete'))
        self.button_back.clicked.connect(lambda: self.browsing('back'))
        self.button_next.clicked.connect(lambda: self.browsing('next'))
        self.listWidget.itemDoubleClicked.connect(lambda: self.call_form('edit'))
        
        # Добавим новую кнопку для отображения продуктов
        self.button_products = QPushButton("Продукты")
        self.button_products.setMinimumSize(120, 40)
        self.button_products.setFont(QFont("Arial", 12, QFont.Bold))
        self.button_products.setStyleSheet("""
            background-color: #F4E8D3; 
            color: #000000;
            border: 1px solid #000000;
        """)
        self.button_products.clicked.connect(self.show_partner_products)
        
        # Добавим кнопку для отображения истории продаж
        self.button_sales_history = QPushButton("История продаж")
        self.button_sales_history.setMinimumSize(140, 40)
        self.button_sales_history.setFont(QFont("Arial", 12, QFont.Bold))
        self.button_sales_history.setStyleSheet("""
            background-color: #F4E8D3; 
            color: #000000;
            border: 1px solid #000000;
        """)
        self.button_sales_history.clicked.connect(self.show_sales_history)
        
        # Добавим кнопку для аналитики продаж
        self.button_sales_analytics = QPushButton("Аналитика")
        self.button_sales_analytics.setMinimumSize(140, 40)
        self.button_sales_analytics.setFont(QFont("Arial", 12, QFont.Bold))
        self.button_sales_analytics.setStyleSheet("""
            background-color: #F4E8D3; 
            color: #000000;
            border: 1px solid #000000;
        """)
        self.button_sales_analytics.clicked.connect(self.show_sales_analytics)
        
        # Добавим кнопки в горизонтальный layout
        layout = self.findChild(QHBoxLayout, "horizontalLayout_2")
        if layout:
            # Вставляем после 2-ой позиции (после кнопки удаления)
            layout.insertWidget(2, self.button_products)
            layout.insertWidget(3, self.button_sales_history)
            layout.insertWidget(4, self.button_sales_analytics)
    
    def call_form(self, act):
        """Open form window with specified action"""
        data_row = None
        if act == 'edit' or act == 'delete':
            selected_items = self.listWidget.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Предупреждение", "Выберите партнера из списка!")
                return
            index = self.listWidget.row(selected_items[0])
            real_index = index + self.current_number_page * self.number_page_elements
            if real_index < len(self.data_db):
                data_row = self.data_db[real_index]
                
        self.form_window = Form(self, act, data_row)
        self.form_window.show()
        
    def show_partner_products(self):
        """Открыть окно со списком продуктов выбранного партнера"""
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите партнера из списка!")
            return
            
        index = self.listWidget.row(selected_items[0])
        real_index = index + self.current_number_page * self.number_page_elements
        if real_index < len(self.data_db):
            partner_data = self.data_db[real_index]
            self.products_window = ProductsWindow(self, partner_data)
            self.products_window.show()
    
    def show_sales_history(self):
        """Open sales history window"""
        selected_items = self.listWidget.selectedItems()
        partner_id = None
        partner_name = None
        
        if selected_items:
            index = self.listWidget.row(selected_items[0])
            real_index = index + self.current_number_page * self.number_page_elements
            if real_index < len(self.data_db):
                partner_data = self.data_db[real_index]
                partner_id = partner_data[0]
                partner_name = partner_data[1]
        
        self.sales_window = SalesHistoryWindow(self, partner_id, partner_name)
        self.sales_window.show()
    
    def show_sales_analytics(self):
        """Show sales analytics window"""
        self.analytics_window = SalesAnalyticsWindow(self)
        self.analytics_window.show()
    
    def browsing(self, direction):
        """Handle pagination"""
        if direction == 'back' and self.current_number_page > 0:
            self.current_number_page -= 1
        elif direction == 'next' and (self.current_number_page + 1) * self.number_page_elements < len(self.data_db):
            self.current_number_page += 1
        
        # Update page number label
        self.label_page.setText(f"Страница {self.current_number_page + 1}")
        
        # Update displayed data
        self.draw_frames()
    
    def get_data_from_table(self):
        """Fetch data from database"""
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db
            )
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Partners")
            self.data_db = cursor.fetchall()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении данных: {str(e)}")
    
    def draw_frames(self):
        """Display data in the list widget"""
        self.listWidget.clear()
        
        start_index = self.current_number_page * self.number_page_elements
        end_index = min(start_index + self.number_page_elements, len(self.data_db))
        
        for i in range(start_index, end_index):
            row = self.data_db[i]
            # Format display text (ID, Name, Type, City, INN)
            item_text = f"{row[0]}: {row[1]} ({row[2]}) - {row[3]}, ИНН: {row[11]}"
            item = QListWidgetItem(item_text)
            self.listWidget.addItem(item)
        
        # Set styles for list items according to the color scheme
        self.listWidget.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #000000;
            }
            QListWidget::item { 
                padding: 5px; 
                border-bottom: 1px solid #000000;
                color: #000000;
            }
            QListWidget::item:selected { 
                background-color: #F4E8D3; 
                color: #000000; 
            }
            QListWidget::item:hover { 
                background-color: #F9F2E3; 
            }
        """)
    
    def show_data(self):
        """Update and display data"""
        self.get_data_from_table()
        self.draw_frames()
        self.label_page.setText(f"Страница {self.current_number_page + 1}")

class Form(QMainWindow):
    def __init__(self, base_window, act, data_row=None):
        super().__init__()
        # Load UI file
        uic.loadUi("form.ui", self)
        self.setWindowTitle("Форма партнера")
        self.setWindowIcon(QIcon("Ресурсы/Мастер пол.png"))
        self.setWindowModality(2)  # Application modal
        
        # Apply color scheme
        self.setStyleSheet("""
            QMainWindow, QWidget, QLineEdit, QComboBox {
                background-color: #FFFFFF;
                color: #000000;
            }
            QLineEdit, QComboBox {
                border: 1px solid #000000;
                padding: 3px;
            }
            QLabel {
                color: #000000;
            }
            QPushButton {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
            }
            QPushButton:hover {
                background-color: #E8D8BA;
            }
        """)
        
        # Store references
        self.base_window = base_window
        self.act = act
        self.data_row = data_row
        
        # If editing or deleting, fill form with data
        if act != 'add':
            self.changing_lines_edit()
        
        # Connect widgets
        self.connect_widget()
    
    def changing_lines_edit(self):
        """Fill form fields with data"""
        if not self.data_row:
            return
        
        # Set field values from data_row
        self.lineEdit_name.setText(str(self.data_row[1]))
        self.comboBox_type.setCurrentText(str(self.data_row[2]))
        
        # Address fields
        self.lineEdit_city.setText(str(self.data_row[3] or ""))
        self.lineEdit_street.setText(str(self.data_row[4] or ""))
        self.lineEdit_building.setText(str(self.data_row[5] or ""))
        
        # Director name fields
        self.lineEdit_lastname.setText(str(self.data_row[6] or ""))
        self.lineEdit_firstname.setText(str(self.data_row[7] or ""))
        self.lineEdit_middlename.setText(str(self.data_row[8] or ""))
        
        # Other fields
        self.lineEdit_phone.setText(str(self.data_row[9] or ""))
        self.lineEdit_email.setText(str(self.data_row[10] or ""))
        self.lineEdit_inn.setText(str(self.data_row[11] or ""))
        self.lineEdit_rating.setText(str(self.data_row[12] or ""))
        
        # Disable editing if deleting
        if self.act == 'delete':
            for widget in self.findChildren(QLineEdit):
                widget.setEnabled(False)
            self.comboBox_type.setEnabled(False)
    
    def connect_widget(self):
        """Set up button text and connect signals"""
        # Set button text based on action
        if self.act == 'add':
            self.button_submit.setText("Добавить")
        elif self.act == 'edit':
            self.button_submit.setText("Изменить")
        elif self.act == 'delete':
            self.button_submit.setText("Удалить")
        
        # Connect button click to action
        self.button_submit.clicked.connect(self.execution_operation)
    
    def execution_operation(self):
        """Execute database operation based on action type"""
        query = ""
        if self.act == 'add':
            query = self.create_query_add()
        elif self.act == 'edit':
            query = self.create_query_edit()
        elif self.act == 'delete':
            query = self.create_query_delete()
        
        if query:
            self.request(query)
        
        self.close()
    
    def request(self, query):
        """Execute SQL query"""
        try:
            conn = pymysql.connect(
                host=self.base_window.host,
                port=self.base_window.port,
                user=self.base_window.user,
                password=self.base_window.password,
                database=self.base_window.db
            )
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Операция выполнена успешно!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при выполнении запроса: {str(e)}")
    
    def get_input_data(self):
        """Get data from form fields"""
        return {
            'name': self.lineEdit_name.text(),
            'type': self.comboBox_type.currentText(),
            'city': self.lineEdit_city.text(),
            'street': self.lineEdit_street.text(),
            'building': self.lineEdit_building.text(),
            'lastname': self.lineEdit_lastname.text(),
            'firstname': self.lineEdit_firstname.text(),
            'middlename': self.lineEdit_middlename.text(),
            'phone': self.lineEdit_phone.text(),
            'email': self.lineEdit_email.text(),
            'inn': self.lineEdit_inn.text(),
            'rating': self.lineEdit_rating.text() or '0'
        }
    
    def create_query_add(self):
        """Create SQL query for INSERT operation"""
        data = self.get_input_data()
        query = f"""
        INSERT INTO Partners (
            name, type, city, street, building, 
            director_lastname, director_firstname, director_middlename, 
            phone, email, inn, rating
        ) VALUES (
            '{data['name']}', '{data['type']}', '{data['city']}', '{data['street']}', '{data['building']}',
            '{data['lastname']}', '{data['firstname']}', '{data['middlename']}',
            '{data['phone']}', '{data['email']}', '{data['inn']}', {data['rating']}
        )
        """
        return query
    
    def create_query_edit(self):
        """Create SQL query for UPDATE operation"""
        data = self.get_input_data()
        query = f"""
        UPDATE Partners SET
            name = '{data['name']}',
            type = '{data['type']}',
            city = '{data['city']}',
            street = '{data['street']}',
            building = '{data['building']}',
            director_lastname = '{data['lastname']}',
            director_firstname = '{data['firstname']}',
            director_middlename = '{data['middlename']}',
            phone = '{data['phone']}',
            email = '{data['email']}',
            inn = '{data['inn']}',
            rating = {data['rating']}
        WHERE id = {self.data_row[0]}
        """
        return query
    
    def create_query_delete(self):
        """Create SQL query for DELETE operation"""
        return f"DELETE FROM Partners WHERE id = {self.data_row[0]}"
    
    def closeEvent(self, event):
        """Update main window data when form is closed"""
        self.base_window.show_data()
        event.accept()

class ProductsWindow(QMainWindow):
    """Окно для отображения и управления продуктами партнера"""
    def __init__(self, base_window, partner_data):
        super().__init__()
        self.setWindowTitle(f"Продукты партнера: {partner_data[1]}")
        self.setWindowIcon(QIcon("Ресурсы/Мастер пол.png"))
        self.setWindowModality(2)  # Application modal
        self.resize(800, 500)
        
        # Apply color scheme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #000000;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #000000;
            }
            QTableWidget::item:selected {
                background-color: #F4E8D3;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
                padding: 5px;
            }
            QPushButton {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
            }
            QPushButton:hover {
                background-color: #E8D8BA;
            }
        """)
        
        self.base_window = base_window
        self.partner_id = partner_data[0]
        self.partner_name = partner_data[1]
        
        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Заголовок
        self.label_title = QLabel(f"Продукты партнера: {self.partner_name}")
        self.label_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.label_title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.label_title)
        
        # Таблица продуктов
        self.table_products = QTableWidget()
        self.table_products.setColumnCount(4)
        self.table_products.setHorizontalHeaderLabels(["ID", "Наименование", "Код", "Цена"])
        self.table_products.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_products.setSelectionBehavior(QTableWidget.SelectRows)
        self.main_layout.addWidget(self.table_products)
        
        # Кнопки управления
        self.buttons_layout = QHBoxLayout()
        
        self.btn_add_product = QPushButton("Добавить продукт")
        self.btn_add_product.setMinimumSize(150, 40)
        self.btn_add_product.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_add_product.clicked.connect(self.add_product)
        
        self.btn_edit_product = QPushButton("Изменить продукт")
        self.btn_edit_product.setMinimumSize(150, 40)
        self.btn_edit_product.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_edit_product.clicked.connect(self.edit_product)
        
        self.btn_delete_product = QPushButton("Удалить продукт")
        self.btn_delete_product.setMinimumSize(150, 40)
        self.btn_delete_product.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_delete_product.clicked.connect(self.delete_product)
        
        self.buttons_layout.addWidget(self.btn_add_product)
        self.buttons_layout.addWidget(self.btn_edit_product)
        self.buttons_layout.addWidget(self.btn_delete_product)
        
        self.main_layout.addLayout(self.buttons_layout)
        
        # Загрузить данные
        self.load_products()
    
    def load_products(self):
        """Загрузить продукты из базы данных"""
        try:
            conn = pymysql.connect(
                host=self.base_window.host,
                port=self.base_window.port,
                user=self.base_window.user,
                password=self.base_window.password,
                database=self.base_window.db
            )
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM Partner_products WHERE partner_id = {self.partner_id}")
            products = cursor.fetchall()
            conn.close()
            
            # Заполнить таблицу
            self.table_products.setRowCount(0)
            for row_idx, product in enumerate(products):
                self.table_products.insertRow(row_idx)
                self.table_products.setItem(row_idx, 0, QTableWidgetItem(str(product[0])))
                self.table_products.setItem(row_idx, 1, QTableWidgetItem(product[2]))
                self.table_products.setItem(row_idx, 2, QTableWidgetItem(product[3]))
                self.table_products.setItem(row_idx, 3, QTableWidgetItem(str(product[4])))
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке продуктов: {str(e)}")
    
    def add_product(self):
        """Открыть диалог добавления продукта"""
        dialog = ProductDialog(self, self.partner_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_products()
    
    def edit_product(self):
        """Редактировать выбранный продукт"""
        selected_row = self.table_products.currentRow()
        if selected_row >= 0:
            product_id = int(self.table_products.item(selected_row, 0).text())
            dialog = ProductDialog(self, self.partner_id, product_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_products()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите продукт для редактирования")
    
    def delete_product(self):
        """Удалить выбранный продукт"""
        selected_row = self.table_products.currentRow()
        if selected_row >= 0:
            product_id = int(self.table_products.item(selected_row, 0).text())
            product_name = self.table_products.item(selected_row, 1).text()
            
            reply = QMessageBox.question(
                self, 
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить продукт '{product_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    conn = pymysql.connect(
                        host=self.base_window.host,
                        port=self.base_window.port,
                        user=self.base_window.user,
                        password=self.base_window.password,
                        database=self.base_window.db
                    )
                    cursor = conn.cursor()
                    cursor.execute(f"DELETE FROM Partner_products WHERE id = {product_id}")
                    conn.commit()
                    conn.close()
                    
                    # Обновить таблицу
                    self.load_products()
                    QMessageBox.information(self, "Успех", "Продукт успешно удален")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении продукта: {str(e)}")
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите продукт для удаления")


class ProductDialog(QDialog):
    """Диалог для добавления/редактирования продукта"""
    def __init__(self, parent, partner_id, product_id=None):
        super().__init__(parent)
        
        # Apply color scheme
        self.setStyleSheet("""
            QDialog, QWidget, QLineEdit {
                background-color: #FFFFFF;
                color: #000000;
            }
            QLineEdit {
                border: 1px solid #000000;
                padding: 3px;
            }
            QLabel {
                color: #000000;
            }
            QPushButton {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #E8D8BA;
            }
        """)
        
        self.parent = parent
        self.partner_id = partner_id
        self.product_id = product_id  # None при добавлении, int при редактировании
        
        self.setWindowTitle("Продукт" if product_id else "Новый продукт")
        self.resize(400, 250)
        
        # Главный layout
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        self.txt_name = QLineEdit()
        self.txt_code = QLineEdit()
        self.txt_price = QLineEdit()
        
        form_layout.addRow("Наименование:", self.txt_name)
        form_layout.addRow("Код продукта:", self.txt_code)
        form_layout.addRow("Цена:", self.txt_price)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Если редактируем, загрузить данные продукта
        if self.product_id:
            self.load_product_data()
    
    def load_product_data(self):
        """Загрузить данные продукта для редактирования"""
        try:
            conn = pymysql.connect(
                host=self.parent.base_window.host,
                port=self.parent.base_window.port,
                user=self.parent.base_window.user,
                password=self.parent.base_window.password,
                database=self.parent.base_window.db
            )
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM Partner_products WHERE id = {self.product_id}")
            product = cursor.fetchone()
            conn.close()
            
            if product:
                self.txt_name.setText(product[2])
                self.txt_code.setText(product[3])
                self.txt_price.setText(str(product[4]))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных продукта: {str(e)}")
    
    def accept(self):
        """Сохранить продукт"""
        name = self.txt_name.text().strip()
        code = self.txt_code.text().strip()
        price_str = self.txt_price.text().strip()
        
        # Проверка заполнения полей
        if not name:
            QMessageBox.warning(self, "Предупреждение", "Укажите наименование продукта")
            return
        if not code:
            QMessageBox.warning(self, "Предупреждение", "Укажите код продукта")
            return
        if not price_str:
            QMessageBox.warning(self, "Предупреждение", "Укажите цену продукта")
            return
        
        # Проверка правильности ввода цены
        try:
            price = float(price_str)
        except ValueError:
            QMessageBox.warning(self, "Предупреждение", "Некорректный формат цены")
            return
        
        try:
            conn = pymysql.connect(
                host=self.parent.base_window.host,
                port=self.parent.base_window.port,
                user=self.parent.base_window.user,
                password=self.parent.base_window.password,
                database=self.parent.base_window.db
            )
            cursor = conn.cursor()
            
            if self.product_id:
                # Редактирование
                query = f"""
                UPDATE Partner_products 
                SET product_name = '{name}', product_code = '{code}', price = {price} 
                WHERE id = {self.product_id}
                """
            else:
                # Добавление
                query = f"""
                INSERT INTO Partner_products (partner_id, product_name, product_code, price)
                VALUES ({self.partner_id}, '{name}', '{code}', {price})
                """
                
            cursor.execute(query)
            conn.commit()
            conn.close()
            
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении продукта: {str(e)}")

class SalesHistoryWindow(QMainWindow):
    """Окно для отображения и управления историей продаж"""
    def __init__(self, base_window, partner_id=None, partner_name=None):
        super().__init__()
        self.setWindowTitle("История продаж")
        self.setWindowIcon(QIcon("Ресурсы/Мастер пол.png"))
        self.setWindowModality(2)  # Application modal
        self.resize(900, 500)
        
        # Apply color scheme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #000000;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px солид #000000;
            }
            QTableWidget::item:selected {
                background-color: #F4E8D3;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
                padding: 5px;
            }
            QPushButton {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
            }
            QPushButton:hover {
                background-color: #E8D8BA;
            }
            QComboBox, QLineEdit, QSpinBox, QDateEdit {
                background-color: #FFFFFF;
                border: 1px solid #000000;
                padding: 5px;
            }
        """)
        
        self.base_window = base_window
        self.partner_id = partner_id
        self.partner_name = partner_name
        
        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Заголовок
        title_text = "История продаж"
        if self.partner_name:
            title_text += f" - Партнер: {self.partner_name}"
            
        self.label_title = QLabel(title_text)
        self.label_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.label_title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.label_title)
        
        # Таблица истории продаж
        self.table_sales = QTableWidget()
        self.table_sales.setColumnCount(6)
        self.table_sales.setHorizontalHeaderLabels([
            "ID", "Партнер", "Продукт", "Количество", "Дата продажи", "Сумма"
        ])
        self.table_sales.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_sales.setSelectionBehavior(QTableWidget.SelectRows)
        self.main_layout.addWidget(self.table_sales)
        
        # Кнопки управления
        self.buttons_layout = QHBoxLayout()
        
        self.btn_add_sale = QPushButton("Добавить продажу")
        self.btn_add_sale.setMinimumSize(150, 40)
        self.btn_add_sale.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_add_sale.clicked.connect(self.add_sale)
        
        self.btn_edit_sale = QPushButton("Изменить продажу")
        self.btn_edit_sale.setMinimumSize(150, 40)
        self.btn_edit_sale.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_edit_sale.clicked.connect(self.edit_sale)
        
        self.btn_delete_sale = QPushButton("Удалить продажу")
        self.btn_delete_sale.setMinimumSize(150, 40)
        self.btn_delete_sale.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_delete_sale.clicked.connect(self.delete_sale)
        
        self.buttons_layout.addWidget(self.btn_add_sale)
        self.buttons_layout.addWidget(self.btn_edit_sale)
        self.buttons_layout.addWidget(self.btn_delete_sale)
        
        self.main_layout.addLayout(self.buttons_layout)
        
        # Загрузить данные
        self.load_sales()
    
    def load_sales(self):
        """Загрузить историю продаж из базы данных"""
        try:
            conn = pymysql.connect(
                host=self.base_window.host,
                port=self.base_window.port,
                user=self.base_window.user,
                password=self.base_window.password,
                database=self.base_window.db
            )
            cursor = conn.cursor()
            
            if self.partner_id:
                # Загрузить историю продаж для конкретного партнера
                query = """
                SELECT pp.id, p.name, pp.product_name, pp.count_product, pp.date_sale, 
                       (pp.count_product * pp.price) as total
                FROM Partner_products pp
                JOIN Partners p ON pp.partner_id = p.id
                WHERE pp.partner_id = %s
                ORDER BY pp.date_sale DESC
                """
                cursor.execute(query, (self.partner_id,))
            else:
                # Загрузить всю историю продаж
                query = """
                SELECT pp.id, p.name, pp.product_name, pp.count_product, pp.date_sale, 
                       (pp.count_product * pp.price) as total
                FROM Partner_products pp
                JOIN Partners p ON pp.partner_id = p.id
                ORDER BY pp.date_sale DESC
                """
                cursor.execute(query)
                
            sales = cursor.fetchall()
            conn.close()
            
            # Заполнить таблицу
            self.table_sales.setRowCount(0)
            for row_idx, sale in enumerate(sales):
                self.table_sales.insertRow(row_idx)
                self.table_sales.setItem(row_idx, 0, QTableWidgetItem(str(sale[0])))
                self.table_sales.setItem(row_idx, 1, QTableWidgetItem(sale[1]))
                self.table_sales.setItem(row_idx, 2, QTableWidgetItem(sale[2]))
                self.table_sales.setItem(row_idx, 3, QTableWidgetItem(str(sale[3])))
                
                # Форматирование даты
                date_str = str(sale[4]) if sale[4] else "Нет даты"
                self.table_sales.setItem(row_idx, 4, QTableWidgetItem(date_str))
                
                # Форматирование суммы
                total_str = f"{sale[5]:.2f} руб." if sale[5] else "0.00 руб."
                self.table_sales.setItem(row_idx, 5, QTableWidgetItem(total_str))
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке истории продаж: {str(e)}")
    
    def add_sale(self):
        """Открыть диалог добавления продажи"""
        dialog = SaleDialog(self, self.partner_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_sales()
    
    def edit_sale(self):
        """Редактировать выбранную продажу"""
        selected_row = self.table_sales.currentRow()
        if selected_row >= 0:
            sale_id = int(self.table_sales.item(selected_row, 0).text())
            dialog = SaleDialog(self, None, sale_id)
            if dialog.exec_() == QDialog.Accepted:
                self.load_sales()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите продажу для редактирования")
    
    def delete_sale(self):
        """Удалить выбранную продажу"""
        selected_row = self.table_sales.currentRow()
        if selected_row >= 0:
            sale_id = int(self.table_sales.item(selected_row, 0).text())
            product_name = self.table_sales.item(selected_row, 2).text()
            
            reply = QMessageBox.question(
                self, 
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить продажу '{product_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    conn = pymysql.connect(
                        host=self.base_window.host,
                        port=self.base_window.port,
                        user=self.base_window.user,
                        password=self.base_window.password,
                        database=self.base_window.db
                    )
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Partner_products WHERE id = %s", (sale_id,))
                    conn.commit()
                    conn.close()
                    
                    # Обновить таблицу
                    self.load_sales()
                    QMessageBox.information(self, "Успех", "Продажа успешно удалена")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении продажи: {str(e)}")
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите продажу для удаления")

class SaleDialog(QDialog):
    """Диалог для добавления/редактирования продажи"""
    def __init__(self, parent, partner_id=None, sale_id=None):
        super().__init__(parent)
        
        # Apply color scheme
        self.setStyleSheet("""
            QDialog, QWidget, QLineEdit, QDateEdit, QSpinBox, QComboBox {
                background-color: #FFFFFF;
                color: #000000;
            }
            QLineEdit, QDateEdit, QSpinBox, QComboBox {
                border: 1px solid #000000;
                padding: 5px;
            }
            QLabel {
                color: #000000;
            }
            QPushButton {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #E8D8BA;
            }
        """)
        
        self.parent = parent
        self.partner_id = partner_id
        self.sale_id = sale_id  # None при добавлении, int при редактировании
        
        self.setWindowTitle("Добавить продажу" if not sale_id else "Изменить продажу")
        self.resize(450, 300)
        
        # Главный layout
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        # Список партнеров
        self.combo_partners = QComboBox()
        self.load_partners()
        
        # Список продуктов
        self.combo_products = QComboBox()
        self.load_products()
        
        # Количество
        self.spin_count = QSpinBox()
        self.spin_count.setMinimum(1)
        self.spin_count.setMaximum(1000000)
        self.spin_count.setValue(1)
        
        # Цена
        self.spin_price = QSpinBox()
        self.spin_price.setMinimum(0)
        self.spin_price.setMaximum(10000000)
        self.spin_price.setSuffix(" руб.")
        self.spin_price.setValue(0)
        
        # Дата продажи
        self.date_sale = QDateEdit()
        self.date_sale.setCalendarPopup(True)
        self.date_sale.setDate(QDate.currentDate())
        
        form_layout.addRow("Партнер:", self.combo_partners)
        form_layout.addRow("Продукт:", self.combo_products)
        form_layout.addRow("Количество:", self.spin_count)
        form_layout.addRow("Цена за единицу:", self.spin_price)
        form_layout.addRow("Дата продажи:", self.date_sale)
        
        layout.addLayout(form_layout)
        
        # Итоговая сумма
        self.label_total = QLabel("Итоговая сумма: 0 руб.")
        self.label_total.setFont(QFont("Arial", 12, QFont.Bold))
        self.label_total.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_total)
        
        # Подключение сигналов для обновления итоговой суммы
        self.spin_count.valueChanged.connect(self.update_total)
        self.spin_price.valueChanged.connect(self.update_total)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Если редактируем, загрузить данные продажи
        if self.sale_id:
            self.load_sale_data()
            # При редактировании блокируем изменение партнера
            self.combo_partners.setEnabled(False)
        elif self.partner_id:
            # Если указан конкретный партнер, выбираем его и блокируем
            self.select_partner(self.partner_id)
            self.combo_partners.setEnabled(False)
    
    def load_partners(self):
        """Загрузить список партнеров"""
        try:
            conn = pymysql.connect(
                host=self.parent.base_window.host,
                port=self.parent.base_window.port,
                user=self.parent.base_window.user,
                password=self.parent.base_window.password,
                database=self.parent.base_window.db
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM Partners ORDER BY name")
            partners = cursor.fetchall()
            conn.close()
            
            self.combo_partners.clear()
            for partner in partners:
                self.combo_partners.addItem(partner[1], partner[0])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке списка партнеров: {str(e)}")
    
    def load_products(self):
        """Загрузить список уникальных продуктов"""
        try:
            conn = pymysql.connect(
                host=self.parent.base_window.host,
                port=self.parent.base_window.port,
                user=self.parent.base_window.user,
                password=self.parent.base_window.password,
                database=self.parent.base_window.db
            )
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT product_name, AVG(price) FROM Partner_products GROUP BY product_name ORDER BY product_name")
            products = cursor.fetchall()
            conn.close()
            
            self.combo_products.clear()
            for product in products:
                self.combo_products.addItem(product[0])
                
            # Добавим возможность ввода своего значения
            self.combo_products.setEditable(True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке списка продуктов: {str(e)}")
    
    def select_partner(self, partner_id):
        """Выбрать партнера по ID"""
        for i in range(self.combo_partners.count()):
            if self.combo_partners.itemData(i) == partner_id:
                self.combo_partners.setCurrentIndex(i)
                return
    
    def update_total(self):
        """Обновить итоговую сумму"""
        count = self.spin_count.value()
        price = self.spin_price.value()
        total = count * price
        self.label_total.setText(f"Итоговая сумма: {total} руб.")
    
    def load_sale_data(self):
        """Загрузить данные продажи для редактирования"""
        try:
            conn = pymysql.connect(
                host=self.parent.base_window.host,
                port=self.parent.base_window.port,
                user=self.parent.base_window.user,
                password=self.parent.base_window.password,
                database=self.parent.base_window.db
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT partner_id, product_name, count_product, price, date_sale 
                FROM Partner_products 
                WHERE id = %s
            """, (self.sale_id,))
            sale = cursor.fetchone()
            conn.close()
            
            if sale:
                # Выбрать партнера
                self.select_partner(sale[0])
                
                # Установить продукт
                index = self.combo_products.findText(sale[1])
                if index >= 0:
                    self.combo_products.setCurrentIndex(index)
                else:
                    self.combo_products.setCurrentText(sale[1])
                
                # Установить количество и цену
                self.spin_count.setValue(sale[2])
                self.spin_price.setValue(int(sale[3]))
                
                # Установить дату
                if sale[4]:
                    date_parts = str(sale[4]).split('-')
                    if len(date_parts) == 3:
                        self.date_sale.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                
                # Обновить итоговую сумму
                self.update_total()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных продажи: {str(e)}")
    
    def accept(self):
        """Сохранить продажу"""
        # Получить выбранного партнера
        partner_id = self.combo_partners.currentData()
        if partner_id is None and self.partner_id:
            partner_id = self.partner_id
        
        if not partner_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите партнера")
            return
        
        product_name = self.combo_products.currentText().strip()
        if not product_name:
            QMessageBox.warning(self, "Предупреждение", "Укажите название продукта")
            return
        
        count = self.spin_count.value()
        price = self.spin_price.value()
        date_sale = self.date_sale.date().toString("yyyy-MM-dd")
        
        try:
            conn = pymysql.connect(
                host=self.parent.base_window.host,
                port=self.parent.base_window.port,
                user=self.parent.base_window.user,
                password=self.parent.base_window.password,
                database=self.parent.base_window.db
            )
            cursor = conn.cursor()
            
            if self.sale_id:
                # Редактирование
                query = """
                UPDATE Partner_products 
                SET product_name = %s, count_product = %s, price = %s, date_sale = %s 
                WHERE id = %s
                """
                cursor.execute(query, (product_name, count, price, date_sale, self.sale_id))
            else:
                # Добавление
                # Генерируем код продукта, если его нет
                product_code = product_name[:10].upper().replace(' ', '_')
                
                query = """
                INSERT INTO Partner_products (partner_id, product_name, product_code, count_product, price, date_sale)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (partner_id, product_name, product_code, count, price, date_sale))
                
            conn.commit()
            conn.close()
            
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении продажи: {str(e)}")

class SalesAnalyticsWindow(QMainWindow):
    """Окно аналитики продаж"""
    def __init__(self, base_window):
        super().__init__()
        self.setWindowTitle("Аналитика продаж")
        self.setWindowIcon(QIcon("Ресурсы/Мастер пол.png"))
        self.setWindowModality(2)  # Application modal
        self.resize(1000, 600)
        
        # Apply color scheme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #FFFFFF;
                color: #000000;
            }
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #000000;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #000000;
            }
            QTableWidget::item:selected {
                background-color: #F4E8D3;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
                padding: 5px;
            }
            QPushButton, QTabBar::tab {
                background-color: #F4E8D3;
                color: #000000;
                border: 1px solid #000000;
                padding: 8px;
            }
            QPushButton:hover, QTabBar::tab:hover {
                background-color: #E8D8BA;
            }
            QTabBar::tab:selected {
                background-color: #D8C8AA;
                font-weight: bold;
            }
        """)
        
        self.base_window = base_window
        
        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Заголовок
        self.label_title = QLabel("Аналитика продаж")
        self.label_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.label_title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.label_title)
        
        # Вкладки для разных видов аналитики
        self.tabs = QTabWidget()
        
        # Вкладка с общей статистикой
        self.tab_summary = QWidget()
        self.tabs.addTab(self.tab_summary, "Общая статистика")
        self.setup_summary_tab()
        
        # Вкладка с топ продаж по партнерам
        self.tab_partners = QWidget()
        self.tabs.addTab(self.tab_partners, "По партнерам")
        self.setup_partners_tab()
        
        # Вкладка с топ продуктов
        self.tab_products = QWidget()
        self.tabs.addTab(self.tab_products, "По продуктам")
        self.setup_products_tab()
        
        # Вкладка с динамикой продаж по месяцам
        self.tab_months = QWidget()
        self.tabs.addTab(self.tab_months, "По месяцам")
        self.setup_months_tab()
        
        self.main_layout.addWidget(self.tabs)
        
        # Загрузить данные
        self.load_analytics_data()
    
    def setup_summary_tab(self):
        """Настройка вкладки с общей статистикой"""
        layout = QVBoxLayout(self.tab_summary)
        
        # Таблица с общими показателями
        self.table_summary = QTableWidget()
        self.table_summary.setColumnCount(2)
        self.table_summary.setHorizontalHeaderLabels(["Показатель", "Значение"])
        self.table_summary.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table_summary)
    
    def setup_partners_tab(self):
        """Настройка вкладки с топом партнеров"""
        layout = QVBoxLayout(self.tab_partners)
        
        # Таблица с топом партнеров
        self.table_partners = QTableWidget()
        self.table_partners.setColumnCount(4)
        self.table_partners.setHorizontalHeaderLabels(["Партнер", "Количество продаж", "Сумма продаж", "Средний чек"])
        self.table_partners.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table_partners)
    
    def setup_products_tab(self):
        """Настройка вкладки с топом продуктов"""
        layout = QVBoxLayout(self.tab_products)
        
        # Таблица с топом продуктов
        self.table_products = QTableWidget()
        self.table_products.setColumnCount(4)
        self.table_products.setHorizontalHeaderLabels(["Продукт", "Количество продаж", "Сумма продаж", "Средняя цена"])
        self.table_products.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table_products)
    
    def setup_months_tab(self):
        """Настройка вкладки с динамикой по месяцам"""
        layout = QVBoxLayout(self.tab_months)
        
        # Таблица с динамикой по месяцам
        self.table_months = QTableWidget()
        self.table_months.setColumnCount(4)
        self.table_months.setHorizontalHeaderLabels(["Месяц", "Количество продаж", "Сумма продаж", "Средний чек"])
        self.table_months.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table_months)
    
    def load_analytics_data(self):
        """Загрузить данные для аналитики"""
        try:
            conn = pymysql.connect(
                host=self.base_window.host,
                port=self.base_window.port,
                user=self.base_window.user,
                password=self.base_window.password,
                database=self.base_window.db
            )
            cursor = conn.cursor()
            
            # Загружаем общую статистику
            self.load_summary_data(cursor)
            
            # Загружаем топ по партнерам
            self.load_partners_data(cursor)
            
            # Загружаем топ по продуктам
            self.load_products_data(cursor)
            
            # Загружаем динамику по месяцам
            self.load_months_data(cursor)
            
            conn.close()
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных аналитики: {str(e)}")
    
    def load_summary_data(self, cursor):
        """Загрузить общую статистику"""
        try:
            # Общее количество продаж
            cursor.execute("""
                SELECT COUNT(*) FROM Partner_products
            """)
            total_sales = cursor.fetchone()[0]
            
            # Общая сумма продаж
            cursor.execute("""
                SELECT SUM(count_product * price) FROM Partner_products
            """)
            total_amount = cursor.fetchone()[0]
            total_amount = total_amount if total_amount else 0
            
            # Средняя сумма продажи
            cursor.execute("""
                SELECT AVG(count_product * price) FROM Partner_products
            """)
            avg_sale = cursor.fetchone()[0]
            avg_sale = avg_sale if avg_sale else 0
            
            # Количество партнеров
            cursor.execute("""
                SELECT COUNT(DISTINCT partner_id) FROM Partner_products
            """)
            partners_count = cursor.fetchone()[0]
            
            # Количество различных продуктов
            cursor.execute("""
                SELECT COUNT(DISTINCT product_name) FROM Partner_products
            """)
            products_count = cursor.fetchone()[0]
            
            # Максимальная продажа
            cursor.execute("""
                SELECT MAX(count_product * price) FROM Partner_products
            """)
            max_sale = cursor.fetchone()[0]
            max_sale = max_sale if max_sale else 0
            
            # Заполняем таблицу
            self.table_summary.setRowCount(6)
            
            # Общее количество продаж
            self.table_summary.setItem(0, 0, QTableWidgetItem("Общее количество продаж"))
            self.table_summary.setItem(0, 1, QTableWidgetItem(str(total_sales)))
            
            # Общая сумма продаж
            self.table_summary.setItem(1, 0, QTableWidgetItem("Общая сумма продаж"))
            self.table_summary.setItem(1, 1, QTableWidgetItem(f"{total_amount:.2f} руб."))
            
            # Средняя сумма продажи
            self.table_summary.setItem(2, 0, QTableWidgetItem("Средняя сумма продажи"))
            self.table_summary.setItem(2, 1, QTableWidgetItem(f"{avg_sale:.2f} руб."))
            
            # Количество партнеров с продажами
            self.table_summary.setItem(3, 0, QTableWidgetItem("Количество партнеров с продажами"))
            self.table_summary.setItem(3, 1, QTableWidgetItem(str(partners_count)))
            
            # Количество различных продуктов
            self.table_summary.setItem(4, 0, QTableWidgetItem("Количество различных продуктов"))
            self.table_summary.setItem(4, 1, QTableWidgetItem(str(products_count)))
            
            # Максимальная продажа
            self.table_summary.setItem(5, 0, QTableWidgetItem("Максимальная сумма продажи"))
            self.table_summary.setItem(5, 1, QTableWidgetItem(f"{max_sale:.2f} руб."))
        
        except Exception as e:
            print(f"Ошибка при загрузке общей статистики: {str(e)}")
    
    def load_partners_data(self, cursor):
        """Загрузить данные по топу партнеров"""
        try:
            # Топ партнеров по сумме продаж
            cursor.execute("""
                SELECT 
                    p.name, 
                    COUNT(*) as sales_count,
                    SUM(pp.count_product * pp.price) as total_amount,
                    AVG(pp.count_product * pp.price) as avg_sale
                FROM Partner_products pp
                JOIN Partners p ON pp.partner_id = p.id
                GROUP BY pp.partner_id, p.name
                ORDER BY total_amount DESC
                LIMIT 10
            """)
            partners = cursor.fetchall()
            
            # Заполняем таблицу
            self.table_partners.setRowCount(len(partners))
            
            for row_idx, partner in enumerate(partners):
                self.table_partners.setItem(row_idx, 0, QTableWidgetItem(partner[0]))
                self.table_partners.setItem(row_idx, 1, QTableWidgetItem(str(partner[1])))
                self.table_partners.setItem(row_idx, 2, QTableWidgetItem(f"{partner[2]:.2f} руб."))
                self.table_partners.setItem(row_idx, 3, QTableWidgetItem(f"{partner[3]:.2f} руб."))
        
        except Exception as e:
            print(f"Ошибка при загрузке данных по топу партнеров: {str(e)}")
    
    def load_products_data(self, cursor):
        """Загрузить данные по топу продуктов"""
        try:
            # Топ продуктов по количеству продаж
            cursor.execute("""
                SELECT 
                    product_name, 
                    SUM(count_product) as total_count,
                    SUM(count_product * price) as total_amount,
                    AVG(price) as avg_price
                FROM Partner_products
                GROUP BY product_name
                ORDER BY total_count DESC
                LIMIT 10
            """)
            products = cursor.fetchall()
            
            # Заполняем таблицу
            self.table_products.setRowCount(len(products))
            
            for row_idx, product in enumerate(products):
                self.table_products.setItem(row_idx, 0, QTableWidgetItem(product[0]))
                self.table_products.setItem(row_idx, 1, QTableWidgetItem(str(product[1])))
                self.table_products.setItem(row_idx, 2, QTableWidgetItem(f"{product[2]:.2f} руб."))
                self.table_products.setItem(row_idx, 3, QTableWidgetItem(f"{product[3]:.2f} руб."))
        
        except Exception as e:
            print(f"Ошибка при загрузке данных по топу продуктов: {str(e)}")
    
    def load_months_data(self, cursor):
        """Загрузить данные по месяцам"""
        try:
            # Продажи по месяцам
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(date_sale, '%Y-%m') as month,
                    COUNT(*) as sales_count,
                    SUM(count_product * price) as total_amount,
                    AVG(count_product * price) as avg_sale
                FROM Partner_products
                WHERE date_sale IS NOT NULL
                GROUP BY month
                ORDER BY month
            """)
            months = cursor.fetchall()
            
            # Заполняем таблицу
            self.table_months.setRowCount(len(months))
            
            for row_idx, month in enumerate(months):
                self.table_months.setItem(row_idx, 0, QTableWidgetItem(month[0]))
                self.table_months.setItem(row_idx, 1, QTableWidgetItem(str(month[1])))
                self.table_months.setItem(row_idx, 2, QTableWidgetItem(f"{month[2]:.2f} руб."))
                self.table_months.setItem(row_idx, 3, QTableWidgetItem(f"{month[3]:.2f} руб."))
        
        except Exception as e:
            print(f"Ошибка при загрузке данных по месяцам: {str(e)}")

def import_data_from_excel():
    """Import data from Excel files to database"""
    try:
        conn = pymysql.connect(
            host="t1brime-dev.ru",
            port=3306,
            user="toonbrime",
            password="Bebra228",
            database="CBO"
        )
        cursor = conn.cursor()
        
        # Import Partners data
        partners_df = pd.read_excel("Ресурсы/Partners_import.xlsx")
        for _, row in partners_df.iterrows():
            # Split address and director name if necessary
            # This is a simplified example, adjust according to actual Excel format
            query = f"""
            INSERT INTO Partners (
                name, type, city, street, building, 
                director_lastname, director_firstname, director_middlename, 
                phone, email, inn, rating
            ) VALUES (
                '{row['name']}', '{row['type']}', '{row['city']}', '{row['street']}', '{row['building']}',
                '{row['director_lastname']}', '{row['director_firstname']}', '{row['director_middlename']}',
                '{row['phone']}', '{row['email']}', '{row['inn']}', {row['rating']}
            )
            """
            cursor.execute(query)
        
        # Import Partner_products data
        products_df = pd.read_excel("Ресурсы/Partner_products_import.xlsx")
        for _, row in products_df.iterrows():
            query = f"""
            INSERT INTO Partner_products (
                partner_id, product_name, product_code, price
            ) VALUES (
                {row['partner_id']}, '{row['product_name']}', '{row['product_code']}', {row['price']}
            )
            """
            cursor.execute(query)
        
        conn.commit()
        conn.close()
        print("Data imported successfully")
    except Exception as e:
        print(f"Error importing data: {str(e)}")

if __name__ == "__main__":
    # Uncomment to import data from Excel files
    # import_data_from_excel()
    
    app = QApplication(sys.argv)
    base_window = BaseWindow()
    base_window.show()
    sys.exit(app.exec_())
