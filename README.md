# CBO - Система управления партнерами

Приложение для управления базой партнеров, их продуктами и историей продаж с функцией аналитики.

## Функциональность

- Управление базой партнеров (добавление, редактирование, удаление)
- Управление продуктами партнеров
- Ведение истории продаж
- Аналитика продаж (статистика, топы, динамика по месяцам)

## Структура проекта

```
pisya_slona/
│
├── main.py                 # Основной файл программы
├── main.ui                 # UI файл главного окна (Qt Designer)
├── form.ui                 # UI файл формы партнера (Qt Designer)
├── queries.sql             # SQL запросы для создания БД и таблиц
├── import_excel.py         # Скрипт для импорта данных из Excel файлов
├── db_diagram.py           # Скрипт для создания диаграммы БД
├── resources.qrc           # Файл ресурсов Qt
├── README.md               # Этот файл
│
└── Ресурсы/                # Папка с ресурсами
    ├── Мастер пол.png      # Логотип
    ├── Partners_import.xlsx # Excel файл с партнерами
    └── Partner_products_import.xlsx # Excel файл с продуктами партнеров
```

## Требования

- Python 3.6 или выше
- PyQt5
- pymysql
- pandas
- graphviz (опционально, для создания диаграммы БД)

## Установка зависимостей

```bash
pip install PyQt5 pymysql pandas
pip install graphviz  # Опционально
```

## Настройка базы данных

1. Запустите SQL-скрипт для создания таблиц:

```bash
mysql -u toonbrime -p -h t1brime-dev.ru CBO < queries.sql
```

2. Импортируйте данные из Excel файлов:

```bash
python import_excel.py
```

## Запуск приложения

```bash
python main.py
```

## Компиляция ресурсов (при изменении resources.qrc)

```bash
pyrcc5 resources.qrc -o resources_rc.py
```

## Генерация диаграммы базы данных

```bash
python db_diagram.py
```

## Дополнительная информация

### Структура базы данных

#### Таблица Partners

- id: INT (Primary Key)
- name: VARCHAR(100) NOT NULL
- type: VARCHAR(20) NOT NULL
- city: VARCHAR(100)
- street: VARCHAR(100)
- building: VARCHAR(20)
- director_lastname: VARCHAR(50)
- director_firstname: VARCHAR(50)
- director_middlename: VARCHAR(50)
- phone: VARCHAR(20)
- email: VARCHAR(100)
- inn: VARCHAR(20) UNIQUE NOT NULL
- rating: INT

#### Таблица Partner_products

- id: INT (Primary Key)
- partner_id: INT NOT NULL (Foreign Key -> Partners.id)
- product_name: VARCHAR(100) NOT NULL
- product_code: VARCHAR(50) NOT NULL
- price: DECIMAL(10,2) NOT NULL
- count_product: INT DEFAULT 1
- date_sale: DATE

### Пользовательский интерфейс

Приложение имеет четыре основных окна:

1. **Главное окно** - отображает список партнеров с возможностью добавления, редактирования и удаления
2. **Окно формы партнера** - используется для добавления и редактирования данных о партнере
3. **Окно продуктов** - отображает список продуктов выбранного партнера
4. **Окно истории продаж** - отображает историю продаж с возможностью фильтрации по партнеру
5. **Окно аналитики** - предоставляет статистику и аналитические данные по продажам

### Цветовая схема

- Основной цвет фона: Белый (#FFFFFF)
- Дополнительный цвет фона: #F4E8D3
- Цвет текста: Черный (#000000)
- Цвет границ: Черный (#000000)
