from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import joinedload

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
   
    categories = db.relationship("Category", secondary="item_category", back_populates="items")

    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return f'<Item {self.name}>'

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    items = db.relationship("Item", secondary="item_category", back_populates="categories")

class ItemCategory(db.Model):
    __tablename__ = "item_category"
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), primary_key=True)

# db.create_all()

@app.route('/')
def hello():
    return "Hello from Flask!"

@app.route('/items', methods=['GET'])
def get_items():
    # items = Item.query.all()
    # item_dict={}
    # for item in items:
        # item_dict[item.id] = str(item.name)
        # item_dict[item.id] = {'name':str(item.name), '':str(item.create_time)}
    items = Item.query.options(joinedload(Item.categories)).all()
    print(items)
    item_list = []
    for item in items:
        # print(item.id)
        categories = [category.name for category in item.categories]
        item_list.append({
            'id': item.id,
            'name': item.name,
            'categories': categories
        })
    print(item_list)
    return jsonify(item_list)

@app.route('/items', methods=['POST'])
def add_item():
    name = request.json['name']
    item = Item(name=name)
    db.session.add(item)
    db.session.commit()
    
    return jsonify({"message":"Item added successfully."}), 201

@app.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id):
    item = Item.query.get(id)
    if not item:
        return jsonify({"error": "Item not found"}), 402
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message":"Item deleted successfully."}), 201

@app.route('/items/<int:id>', methods=['PUT'])
def put_item(id):
    name = request.json['name']
    item = Item.query.get(id)
    if not item:
        return jsonify({"error": "Item not found"}), 402
    db.session.merge(item)

    item.name = name
    db.session.commit()
    return jsonify({"message":"Item updated successfully."}), 200

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    category_dict={}
    for category in categories:
        category_dict[category.id] = str(category.name)
    return jsonify(category_dict)

@app.route('/categories', methods=['POST'])
def add_category():
    name = request.json['name']
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify({"message":"Category added successfully."}), 200

@app.route('/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "category not found"}), 402
    db.session.delete(category)
    db.session.commit()

    return jsonify({"message":"Category deleted successfully."}), 201

@app.route('/itemcategory', methods=['POST'])
def add_itemcategory():
    item_id = request.json['item_id']
    category_id = request.json['category_id']
    newinstance = ItemCategory(item_id=item_id, category_id=category_id)
    db.session.add(newinstance)
    db.session.commit()
    return jsonify({"message":"tag added successfully."}), 200


if __name__ == '__main__':
    app.run(debug=True)