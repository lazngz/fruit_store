import requests
from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_cors import CORS
import jwt
from functools import wraps

app = Flask(__name__, template_folder='templates')
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'

AUTH_SERVICE_URL = 'http://localhost:5001'
PRODUCTS_API_URL = 'http://localhost:5002'
ORDERS_API_URL = 'http://localhost:5003'


# Decorator để kiểm tra token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')  # Lấy token từ cookie
        if not token:
            return redirect(url_for('login_page'))
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login_page'))
        except jwt.InvalidTokenError:
            return redirect(url_for('login_page'))
        return f(decoded_token, *args, **kwargs)
    return decorated


# Giao diện đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        try:
            # Gửi yêu cầu tới auth_service
            response = requests.post(f'{AUTH_SERVICE_URL}/auth/login', json={
                'username': username,
                'password': password
            })
            if response.status_code == 200:
                token = response.json().get('token')
                resp = redirect(url_for('dashboard'))
                resp.set_cookie('token', token)  # Lưu token vào cookie
                return resp
            else:
                return render_template('login.html', error="Invalid credentials")
        except Exception as e:
            return render_template('login.html', error="Auth service not reachable")
    return render_template('login.html')


# Giao diện chính (dashboard)
@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard(user_data):
    return render_template('dashboard.html', user=user_data)


# Hiển thị danh sách sản phẩm
@app.route('/products/view', methods=['GET'])
@token_required
def products_view(user_data):
    try:
        response = requests.get(f'{PRODUCTS_API_URL}/products')
        products = response.json()
        return render_template('products.html', products=products)
    except Exception as e:
        return render_template('products.html', error=str(e), products=[])


# Thêm sản phẩm
@app.route('/products/add', methods=['POST'])
@token_required
def add_product(user_data):
    try:
        data = request.form
        name = data.get('name')
        price = data.get('price')

        response = requests.post(f'{PRODUCTS_API_URL}/products', json={'name': name, 'price': price})
        if response.status_code == 201:
            return redirect(url_for('products_view'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Cập nhật sản phẩm
@app.route('/products/update/<int:product_id>', methods=['POST'])
@token_required
def update_product(user_data, product_id):
    try:
        data = request.form
        name = data.get('name')
        price = data.get('price')

        response = requests.put(f'{PRODUCTS_API_URL}/products/{product_id}', json={'name': name, 'price': price})
        if response.status_code == 200:
            return redirect(url_for('products_view'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Xóa sản phẩm
@app.route('/products/delete/<int:product_id>', methods=['POST'])
@token_required
def delete_product(user_data, product_id):
    try:
        response = requests.delete(f'{PRODUCTS_API_URL}/products/{product_id}')
        if response.status_code == 200:
            return redirect(url_for('products_view'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Tìm kiếm sản phẩm theo tên
@app.route('/products/search', methods=['GET'])
@token_required
def search_products(user_data):
    try:
        query = request.args.get('query', '').strip()  # Lấy từ khóa tìm kiếm từ query string
        if not query:
            return redirect(url_for('products_view'))

        # Gửi yêu cầu đến Products API
        response = requests.get(f'{PRODUCTS_API_URL}/products?search={query}')
        if response.status_code == 200:
            products = response.json()
            return render_template('products.html', products=products, search_query=query)
        else:
            return render_template('products.html', error="Unable to fetch search results.", products=[])
    except Exception as e:
        app.logger.error(f"Error searching products: {e}")
        return render_template('products.html', error=str(e), products=[])

# Hiển thị danh sách đơn hàng
@app.route('/orders/view', methods=['GET'])
@token_required
def orders_view(user_data):
    try:
        response = requests.get(f'{ORDERS_API_URL}/orders')
        orders = response.json()
        return render_template('orders.html', orders=orders)
    except Exception as e:
        return render_template('orders.html', error=str(e), orders=[])


# Thêm đơn hàng
def is_product_exist(product_id):
    try:
        response = requests.get(f'{PRODUCTS_API_URL}/products/{product_id}')
        return response.status_code == 200
    except Exception as e:
        app.logger.error(f"Error checking Product ID {product_id}: {e}")
        return False


# Thêm đơn hàng
@app.route('/orders/add', methods=['POST'])
@token_required
def add_order(user_data):
    try:
        # Lấy dữ liệu từ form
        product_name = request.form.get('product_name')  # Tên sản phẩm
        quantity = request.form.get('quantity')  # Số lượng

        # Kiểm tra đầu vào
        if not product_name or not quantity:
            return jsonify({'error': 'Product name and Quantity are required'}), 400

        if not quantity.isdigit():
            return jsonify({'error': 'Quantity must be a valid integer'}), 400

        quantity = int(quantity)

        # Kiểm tra sản phẩm có tồn tại không
        product_response = requests.get(f'{PRODUCTS_API_URL}/products?search={product_name}')
        if product_response.status_code != 200 or not product_response.json():
            return jsonify({'error': f'Product "{product_name}" does not exist'}), 404

        # Lấy thông tin sản phẩm (giả sử lấy sản phẩm đầu tiên trong kết quả)
        product = product_response.json()[0]
        price_per_unit = product.get('price')

        if not price_per_unit:
            return jsonify({'error': 'Failed to retrieve product price'}), 500

        # Tính tổng giá
        total_price = price_per_unit * quantity

        # Gửi thông tin đến Orders API
        order_response = requests.post(f'{ORDERS_API_URL}/orders', json={
            'product_id': product_name,  # Lưu tên sản phẩm vào cột product_id
            'quantity': quantity,
            'total_price': total_price
        })

        if order_response.status_code == 201:
            return redirect(url_for('orders_view'))
        else:
            return jsonify(order_response.json()), order_response.status_code
    except Exception as e:
        app.logger.error(f"Error adding order: {e}")
        return jsonify({'error': str(e)}), 500

# Cập nhật đơn hàng
@app.route('/orders/update/<int:order_id>', methods=['POST'])
@token_required
def update_order(user_data, order_id):
    try:
        data = request.form
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        total_price = data.get('total_price')

        response = requests.put(f'{ORDERS_API_URL}/orders/{order_id}', json={
            'product_id': product_id,
            'quantity': quantity,
            'total_price': total_price
        })
        if response.status_code == 200:
            return redirect(url_for('orders_view'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Xóa đơn hàng
@app.route('/orders/delete/<int:order_id>', methods=['POST'])
@token_required
def delete_order(user_data, order_id):
    try:
        response = requests.delete(f'{ORDERS_API_URL}/orders/{order_id}')
        if response.status_code == 200:
            return redirect(url_for('orders_view'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Hiển thị danh sách tài khoản
@app.route('/users/view', methods=['GET'])
@token_required
def users_view(user_data):
    try:
        response = requests.get(f'{AUTH_SERVICE_URL}/auth/users')
        if response.status_code == 200:
            users = response.json()
            return render_template('users.html', users=users)
        else:
            return render_template('users.html', error="Unable to fetch users.", users=[])
    except Exception as e:
        app.logger.error(f"Error fetching users: {e}")
        return render_template('users.html', error=str(e), users=[])


# Thêm tài khoản mới
@app.route('/users/add', methods=['POST'])
@token_required
def add_user(user_data):
    try:
        data = request.form
        username = data.get('username')
        password = data.get('password')

        response = requests.post(f'{AUTH_SERVICE_URL}/auth/register', json={
            'username': username,
            'password': password
        })

        if response.status_code == 201:
            return redirect(url_for('users_view'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        app.logger.error(f"Error adding user: {e}")
        return jsonify({'error': str(e)}), 500


# Xóa tài khoản
@app.route('/users/delete/<int:user_id>', methods=['POST'])
@token_required
def delete_user(user_data, user_id):
    try:
        response = requests.delete(f'{AUTH_SERVICE_URL}/auth/delete/{user_id}')
        if response.status_code == 200:
            return redirect(url_for('users_view'))
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        app.logger.error(f"Error deleting user: {e}")
        return jsonify({'error': str(e)}), 500

# Home
@app.route('/')
def home():
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
