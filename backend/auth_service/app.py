import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'your_secret_key'

DATABASE = os.path.join(os.path.dirname(__file__), 'db.sqlite')


# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
@app.route('/auth/users', methods=['GET'])
def get_users():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users')
        users = cursor.fetchall()
        conn.close()
        return jsonify([{'id': user[0], 'username': user[1]} for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Register a new user
@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        hashed_password = hash_password(password)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        return jsonify({'message': 'User registered successfully!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Login and return a JWT token
@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        hashed_password = hash_password(password)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        user = cursor.fetchone()
        conn.close()

        if user:
            payload = {
                'user_id': user[0],
                'username': username,
                'exp': datetime.now(timezone.utc) + timedelta(hours=1)  # Token hết hạn sau 1 giờ
            }
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({'message': 'Login successful!', 'token': token}), 200
        else:
            return jsonify({'error': 'Invalid credentials!'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404

        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'User deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return jsonify({'message': 'Auth Service is running!'}), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
