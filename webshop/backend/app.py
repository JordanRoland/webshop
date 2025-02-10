from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Adatbázis modellek
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    telep = db.Column(db.String(50), nullable=False)
    unique_code = db.Column(db.String(10), unique=True, nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Alapadatok inicializálása
@app.before_first_request
def create_tables():
    db.create_all()
    if not User.query.filter_by(unique_code='001').first():
        user = User(username='Palotabozsoki Zrt', telep='I. telep', unique_code='001')
        db.session.add(user)
        db.session.commit()
    
    products = [
        'UBM indító gr. morzs.', 'UBM nevelő I. gr. s.',
        'UBM nevelő II. gr. s.', 'UBM befejező gr. s.'
    ]
    for p in products:
        if not Product.query.filter_by(name=p).first():
            db.session.add(Product(name=p))
    db.session.commit()

# Bejelentkezés egyedi kóddal
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(unique_code=data.get('unique_code')).first()
    if user:
        session['user_id'] = user.id
        return jsonify({'message': 'Sikeres belépés!', 'username': user.username})
    return jsonify({'error': 'Érvénytelen kód!'}), 401

# Termékek listázása
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name} for p in products])

# Rendelés leadása
@app.route('/order', methods=['POST'])
def place_order():
    data = request.json
    if 'user_id' not in session:
        return jsonify({'error': 'Nincs bejelentkezve!'}), 401
    
    new_order = Order(
        user_id=session['user_id'],
        product_id=data['product_id'],
        quantity=data['quantity'],
        delivery_date=datetime.strptime(data['delivery_date'], '%Y-%m-%d').date(),
        note=data.get('note')
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Köszönjük, megrendelését rögzítettük!'})

# Korábbi rendelések listázása
@app.route('/orders', methods=['GET'])
def get_orders():
    if 'user_id' not in session:
        return jsonify({'error': 'Nincs bejelentkezve!'}), 401
    
    orders = Order.query.filter_by(user_id=session['user_id']).all()
    return jsonify([
        {
            'product': Product.query.get(o.product_id).name,
            'quantity': o.quantity,
            'delivery_date': o.delivery_date.strftime('%Y-%m-%d'),
            'note': o.note,
            'created_at': o.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for o in orders
    ])

if __name__ == '__main__':
    app.run(debug=True)
