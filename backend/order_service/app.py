from flask import Flask, jsonify, request, render_template
from flask_cors import CORS  # Import thư viện CORS
import sqlite3
import logging

app = Flask(__name__, template_folder='templates')
CORS(app)  # Bật CORS cho toàn bộ ứng dụng
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize database
def init_db():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        total_price REAL
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

@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        orders = fetch_data('SELECT * FROM orders')
        return jsonify([{
            'id': o[0],
            'product_id': o[1],
            'quantity': o[2],
            'total_price': o[3]
        } for o in orders]), 200
    except Exception as e:
        logging.error(f"Error fetching orders: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    try:
        order = fetch_data('SELECT * FROM orders WHERE id = ?', (order_id,))
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        order = order[0]
        return jsonify({
            'id': order[0],
            'product_id': order[1],
            'quantity': order[2],
            'total_price': order[3]
        }), 200
    except Exception as e:
        logging.error(f"Error occurred while fetching order ID {order_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        total_price = data.get('total_price')

        if not product_id or not quantity or not total_price:
            return jsonify({'error': 'product_id, quantity, and total_price are required'}), 400

        execute_query(
            'INSERT INTO orders (product_id, quantity, total_price) VALUES (?, ?, ?)',
            (product_id, quantity, total_price)
        )
        return jsonify({'message': 'Order created successfully!'}), 201
    except Exception as e:
        logging.error(f"Error occurred while creating order: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        total_price = data.get('total_price')

        if not product_id or not quantity or not total_price:
            return jsonify({'error': 'product_id, quantity, and total_price are required'}), 400

        order = fetch_data('SELECT * FROM orders WHERE id = ?', (order_id,))
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        execute_query(
            'UPDATE orders SET product_id = ?, quantity = ?, total_price = ? WHERE id = ?',
            (product_id, quantity, total_price, order_id)
        )
        return jsonify({'message': 'Order updated successfully!'}), 200
    except Exception as e:
        logging.error(f"Error occurred while updating order ID {order_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        order = fetch_data('SELECT * FROM orders WHERE id = ?', (order_id,))
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        execute_query('DELETE FROM orders WHERE id = ?', (order_id,))
        return jsonify({'message': 'Order deleted successfully!'}), 200
    except Exception as e:
        logging.error(f"Error occurred while deleting order ID {order_id}: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    init_db()
    app.run(port=5003, debug=True)
  