from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QMessageBox, QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QDialog, QFormLayout, QDialogButtonBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
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
        
        # Добавим кнопку в горизонтальный layout после кнопки удаления
        layout = self.findChild(QHBoxLayout, "horizontalLayout_2")
        if layout:
            # Вставляем после 2-ой позиции (после кнопки удаления)
            layout.insertWidget(2, self.button_products)
    
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
