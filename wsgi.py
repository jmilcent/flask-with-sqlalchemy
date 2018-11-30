from flask import Flask, render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import Config
from flask import request
from flask import abort
from flask import jsonify

app = Flask(__name__)
app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

from models import Product
from schemas import products_schema,product_schema

admin = Admin(app, name='Back-office', template_mode='bootstrap3')
admin.add_view(ModelView(Product, db.session)) # `Product` needs to be imported before

@app.route('/hello')
def hello():
    return "Hello World!"


@app.route('/products')
def products():
    products = db.session.query(Product).all() # SQLAlchemy request => 'SELECT * FROM products'
    #return products_schema.jsonify(products)
    return render_template('home.html', products=products)


@app.route('/products', methods=['POST'])
def add_product():
    new_product = request.get_json()
    product = Product()
    product.name = new_product['name']
    db.session.add(product)
    db.session.commit()
    q = db.session.query(Product).filter(Product.name == new_product['name'])
    if not db.session.query(q.exists()):
        return jsonify(abort(422, "insert failed"))
    else:
        return jsonify(201)


@app.route('/products/<int:id>')
def get_products(id):
    product = db.session.query(Product).get(id)
    db.session.commit()
    #return product_schema.jsonify(product)
    return render_template('find.html', products=product)


@app.route('/products/<int:id>', methods=['DELETE'])
def del_product(id):
    product = db.session.query(Product).get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        check_product = db.session.query(Product).get(id)
        if check_product:
            return jsonify(abort(422, "delete failed"))
        else:
            return jsonify(201)
    else:
        return jsonify(abort(422, "id not exist"))


@app.route('/products/<int:id>', methods=['PATCH'])
def upd_product(id):
    new_product = request.get_json()
    product = db.session.query(Product).get(id)
    if product:
        product.name = new_product['name']
        db.session.commit()
        check_product = db.session.query(Product).get(id)
        if check_product.name == new_product['name']:
            return jsonify(201)
        else:
            return jsonify(abort(422, "update failed"))
    else:
        return jsonify(abort(422, "id not exist"))
