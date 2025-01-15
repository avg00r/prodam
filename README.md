# ПроДам - Сайт объявлений

Веб-приложение для размещения и поиска объявлений о продаже товаров.

## Функциональность

- Регистрация и авторизация пользователей
- Создание, просмотр и редактирование объявлений
- Поиск товаров по названию и описанию
- Личный кабинет пользователя с возможностью редактирования профиля
- Просмотр своих объявлений
- Регистронезависимый поиск

## Технологии

- Python 3.x
- Flask
- SQLAlchemy
- SQLite
- HTML/CSS
- Jinja2 Templates

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/avg00r/prodam.git
```
2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
```
```bash
source venv/bin/activate # для Linux/Mac
```
```powershell
# In cmd.exe
venv\Scripts\activate.bat
```
```powershell
# In PowerShell
venv\Scripts\Activate.ps1
```
3. Установите зависимости:
```bash
pip install -r requirements.txt
```
4. Запустите приложение:
```bash
python app.py
```
5. Откройте в браузере:
- Локально: http://localhost:5000
- В локальной сети: http://<IP-адрес>:5000

## Структура проекта
README.md
project/
├── app.py # Основной файл приложения
├── requirements.txt # Зависимости проекта
├── static/ # Статические файлы
│ ├── styles.css # CSS стили
│ └── images/ # Изображения
│ └── logo.png # Логотип сайта
├── templates/ # HTML шаблоны
│ ├── base.html # Базовый шаблон
│ ├── index.html # Главная страница
│ ├── login.html # Страница входа
│ ├── register.html # Страница регистрации
│ ├── profile.html # Профиль пользователя
│ ├── my_products.html # Мои товары
│ ├── create_product.html # Создание товара
│ └── edit_product.html # Редактирование товара
└── users.db # База данных SQLite

## Тестовые данные

Тестовые пользователи:
- Логин: ivan, пароль: test123
- Логин: maria, пароль: test123
- Логин: alex, пароль: test123
- Логин: elena, пароль: test123
- Логин: dmitry, пароль: test123

Для заполнения базы тестовыми данными используйте скрипт:
```bash
python create_test_data.py
```

```python
from app import app, db, User, Product
from werkzeug.security import generate_password_hash
from datetime import datetime
import random

# Тестовые данные
test_users = [
    {"username": "ivan", "password": "test123", "firstname": "Иван", "lastname": "Иванов"},
    {"username": "maria", "password": "test123", "firstname": "Мария", "lastname": "Петрова"},
    {"username": "alex", "password": "test123", "firstname": "Александр", "lastname": "Сидоров"},
    {"username": "elena", "password": "test123", "firstname": "Елена", "lastname": "Козлова"},
    {"username": "dmitry", "password": "test123", "firstname": "Дмитрий", "lastname": "Смирнов"}
]

test_products = [
    {"name": "Велосипед", "description": "Горный велосипед в отличном состоянии", "price": 15000},
    {"name": "Ноутбук", "description": "MacBook Pro 2019, 16GB RAM", "price": 80000},
    {"name": "Смартфон", "description": "iPhone 12, 128GB, черный", "price": 45000},
    {"name": "Гитара", "description": "Акустическая гитара Yamaha", "price": 20000},
    {"name": "Книги", "description": "Коллекция классической литературы", "price": 5000},
    {"name": "Фотоаппарат", "description": "Canon EOS 250D + kit объектив", "price": 35000},
    {"name": "Планшет", "description": "iPad Air 2022, 256GB", "price": 55000},
    {"name": "Наушники", "description": "Sony WH-1000XM4, беспроводные", "price": 25000},
    {"name": "Монитор", "description": "27 дюймов, 4K, IPS", "price": 30000},
    {"name": "Кофемашина", "description": "Автоматическая, с капучинатором", "price": 40000}
]

with app.app_context():
    # Очищаем базу данных
    db.drop_all()
    db.create_all()
    
    # Создаем пользователей
    created_users = []
    for user_data in test_users:
        user = User(
            username=user_data["username"],
            password=generate_password_hash(user_data["password"]),
            firstname=user_data["firstname"],
            lastname=user_data["lastname"]
        )
        db.session.add(user)
        created_users.append(user)
    
    db.session.commit()
    
    # Создаем товары
    for user in created_users:
        # Случайное количество товаров (от 1 до 4) для каждого пользователя
        num_products = random.randint(1, 4)
        # Случайный выбор товаров из списка
        selected_products = random.sample(test_products, num_products)
        
        for product_data in selected_products:
            # Добавляем небольшую случайность в цену
            price_variation = random.uniform(0.9, 1.1)
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                price=round(product_data["price"] * price_variation, 2),
                user_id=user.id
            )
            db.session.add(product)
    
    db.session.commit()
    
    # Выводим созданные данные
    print("Созданные пользователи:")
    for user in User.query.all():
        print(f"- {user.username} ({user.firstname} {user.lastname})")
        products = Product.query.filter_by(user_id=user.id).all()
        print(f"  Товары ({len(products)}):")
        for product in products:
            print(f"  - {product.name}: {product.price} ₽")
        print()
```

## Разработка

- Для доступа к сайту из локальной сети используется параметр host='0.0.0.0'
- Все шаблоны наследуются от base.html
- Поиск работает регистронезависимо для русского и английского языков
- Логирование действий пользователей в консоль

## Автор

Vadim Yangunaev

## Лицензия

MIT

