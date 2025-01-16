from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'your_secret_key'

# Thêm CORS
CORS(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )''')
    conn.commit()
    conn.close()

# Helper function to execute queries
def execute_query(query, params=()):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

# Helper function to fetch data
def fetch_data(query, params=()):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products', methods=['GET'])
def get_products():
    try:
        search_query = request.args.get('search', '').strip()
        if search_query:
            products = fetch_data("SELECT * FROM products WHERE name LIKE ?", (f'%{search_query}%',))
        else:
            products = fetch_data("SELECT * FROM products")
        return jsonify([{
            'id': p[0],
            'name': p[1],
            'price': p[2]
        } for p in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    try:
        product = fetch_data('SELECT * FROM products WHERE id = ?', (product_id,))
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        product = product[0]
        return jsonify({
            'id': product[0],
            'name': product[1],
            'price': product[2]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')

        if not name or not price:
            return jsonify({'error': 'Name and price are required'}), 400

        execute_query('INSERT INTO products (name, price) VALUES (?, ?)', (name, price))
        return jsonify({'message': 'Product added successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')

        if not name or not price:
            return jsonify({'error': 'Name and price are required'}), 400

        product = fetch_data('SELECT * FROM products WHERE id = ?', (product_id,))
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        execute_query('UPDATE products SET name = ?, price = ? WHERE id = ?', (name, price, product_id))
        return jsonify({'message': 'Product updated successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = fetch_data('SELECT * FROM products WHERE id = ?', (product_id,))
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        execute_query('DELETE FROM products WHERE id = ?', (product_id,))
        return jsonify({'message': 'Product deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(port=5002, debug=True)
