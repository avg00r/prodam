from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
from sqlalchemy import or_, func

app = Flask(__name__)
app.secret_key = 'ваш_секретный_ключ'  # Замените на случайную строку
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(80))
    firstname = db.Column(db.String(80))
    middlename = db.Column(db.String(80))
    birthdate = db.Column(db.Date)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100, collation='NOCASE'))
    description = db.Column(db.Text(collation='NOCASE'))
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('products', lazy=True))

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    current_user = User.query.get(session['user_id']) if 'user_id' in session else None
    
    if search_query:
        # Используем простой LIKE с параметрами
        search_pattern = f"%{search_query}%"
        products = Product.query.filter(
            or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern)
            )
        ).order_by(Product.created_at.desc()).all()
        
        logger.info(f'Поиск по запросу: "{search_query}". Найдено товаров: {len(products)}')
    else:
        products = Product.query.order_by(Product.created_at.desc()).all()
    
    return render_template('index.html', 
                         products=products, 
                         current_user=current_user, 
                         search_query=search_query)

@app.route('/product/create', methods=['GET', 'POST'])
def create_product():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        
        product = Product(
            name=name,
            description=description,
            price=price,
            user_id=session['user_id']
        )
        
        db.session.add(product)
        db.session.commit()
        logger.info(f'Пользователь {current_user.username} создал новый товар: {name}')
        flash('Товар успешно создан!')
        return redirect(url_for('index'))
    
    return render_template('create_product.html', current_user=current_user)

@app.route('/my-products')
def my_products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    user_products = Product.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_products.html', products=user_products, current_user=current_user)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            logger.info(f'Пользователь {username} вошел в систему')
            return redirect(url_for('index'))
        
        logger.warning(f'Неудачная попытка входа для пользователя {username}')
        flash('Неверное имя пользователя или пароль')
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    current_user = user
    
    if request.method == 'POST':
        user.lastname = request.form['lastname']
        user.firstname = request.form['firstname']
        user.middlename = request.form['middlename']
        if request.form['birthdate']:
            user.birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d')
        db.session.commit()
        flash('Профиль обновлен')
    
    return render_template('profile.html', user=user, current_user=current_user)

@app.route('/logout')
def logout():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        logger.info(f'Пользователь {user.username} вышел из системы')
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            logger.warning(f'Попытка регистрации существующего пользователя {username}')
            flash('Пользователь с таким именем уже существует')
            return redirect(url_for('register'))

        if password != confirm_password:
            logger.warning(f'Пароли не совпадают при регистрации пользователя {username}')
            flash('Пароли не совпадают')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f'Зарегистрирован новый пользователь {username}')
        flash('Регистрация успешна! Теперь вы можете войти.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    product = Product.query.get_or_404(product_id)
    
    # Проверяем, принадлежит ли товар текущему пользователю
    if product.user_id != current_user.id:
        logger.warning(f'Пользователь {current_user.username} попытался редактировать чужой товар {product_id}')
        flash('У вас нет прав на редактирование этого товара')
        return redirect(url_for('my_products'))
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        
        db.session.commit()
        logger.info(f'Пользователь {current_user.username} отредактировал товар: {product.name}')
        flash('Товар успешно обновлен!')
        return redirect(url_for('my_products'))
    
    return render_template('edit_product.html', product=product, current_user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)