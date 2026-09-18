from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

import mysql.connector


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

# For learning only.
# Later we will move this into a .env file.
app.config["JWT_SECRET_KEY"] = "imran123"

jwt = JWTManager(app)


# =========================================================
# DATABASE CONNECTION
# =========================================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="secure_user_api"
)


# =========================================================
# ADMIN AUTHORIZATION DECORATOR
# =========================================================

def admin_required(f):

    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):

        user_id = get_jwt_identity()

        try:
            cursor = db.cursor(dictionary=True)

            cursor.execute(
                "SELECT role FROM users WHERE id = %s",
                (user_id,)
            )

            user = cursor.fetchone()

            cursor.close()

            if not user:
                return jsonify({
                    "message": "User not found"
                }), 404

            if user["role"] != "admin":
                return jsonify({
                    "message": "Admin access required"
                }), 403

            return f(*args, **kwargs)

        except mysql.connector.Error:
            return jsonify({
                "message": "Database error"
            }), 500

    return decorated_function


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return jsonify({
        "message": "Welcome to the Secure User Management API"
    }), 200


# =========================================================
# API STATUS
# =========================================================

@app.route("/api/status", methods=["GET"])
def status():

    return jsonify({
        "message": "API is running successfully"
    }), 200


# =========================================================
# REGISTER
# =========================================================

@app.route("/api/auth/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    # Hash password before storing it
    password_hash = generate_password_hash(password)

    try:

        cursor = db.cursor()

        query = """
            INSERT INTO users
            (name, email, password_hash)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            query,
            (name, email, password_hash)
        )

        db.commit()

        user_id = cursor.lastrowid

        cursor.close()

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "role": "user"
            }
        }), 201

    except mysql.connector.Error as err:

        if err.errno == 1062:
            return jsonify({
                "message": "Email already exists"
            }), 409

        return jsonify({
            "message": "Database error"
        }), 500


# =========================================================
# LOGIN
# =========================================================

@app.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    try:

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, password_hash, role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()

        if not user:
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        # Check entered password against stored hash
        if not check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        # Create JWT
        access_token = create_access_token(
            identity=str(user["id"])
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        }), 200

    except mysql.connector.Error:
        return jsonify({
            "message": "Database error"
        }), 500


# =========================================================
# PROFILE
# =========================================================

@app.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    try:

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, role
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        cursor.close()

        if not user:
            return jsonify({
                "message": "User not found"
            }), 404

        return jsonify({
            "message": "Profile retrieved successfully",
            "user": user
        }), 200

    except mysql.connector.Error:
        return jsonify({
            "message": "Database error"
        }), 500


# =========================================================
# GET ALL USERS
# ADMIN ONLY
# =========================================================

@app.route("/api/users", methods=["GET"])
@admin_required
def get_users():

    try:

        cursor = db.cursor(dictionary=True)

        # Never return password_hash
        cursor.execute(
            """
            SELECT id, name, email, role
            FROM users
            """
        )

        users = cursor.fetchall()

        cursor.close()

        return jsonify(users), 200

    except mysql.connector.Error:
        return jsonify({
            "message": "Database error"
        }), 500


# =========================================================
# CREATE USER
# ADMIN ONLY
# =========================================================

@app.route("/api/users", methods=["POST"])
@admin_required
def create_users():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    if role not in ["user", "admin"]:
        return jsonify({
            "message": "Role must be user or admin"
        }), 400

    password_hash = generate_password_hash(password)

    try:

        cursor = db.cursor()

        query = """
            INSERT INTO users
            (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (name, email, password_hash, role)
        )

        db.commit()

        user_id = cursor.lastrowid

        cursor.close()

        return jsonify({
            "message": "User created successfully",
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "role": role
            }
        }), 201

    except mysql.connector.Error as err:

        if err.errno == 1062:
            return jsonify({
                "message": "Email already exists"
            }), 409

        return jsonify({
            "message": "Database error"
        }), 500


# =========================================================
# GET SINGLE USER
# ADMIN ONLY
# =========================================================

@app.route("/api/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):

    try:

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, role
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        cursor.close()

        if not user:
            return jsonify({
                "message": "User not found"
            }), 404

        return jsonify(user), 200

    except mysql.connector.Error:
        return jsonify({
            "message": "Database error"
        }), 500


# =========================================================
# UPDATE USER
# ADMIN ONLY
# =========================================================

@app.route("/api/users/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({
            "message": "Name and email are required"
        }), 400

    try:

        cursor = db.cursor(dictionary=True)

        # Check whether user exists
        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            cursor.close()

            return jsonify({
                "message": "User not found"
            }), 404

        # Update user
        cursor.execute(
            """
            UPDATE users
            SET name = %s, email = %s
            WHERE id = %s
            """,
            (name, email, user_id)
        )

        db.commit()

        cursor.close()

        return jsonify({
            "message": "User updated successfully",
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            }
        }), 200

    except mysql.connector.Error as err:

        if err.errno == 1062:
            return jsonify({
                "message": "Email already exists"
            }), 409

        return jsonify({
            "message": "Database error"
        }), 500


# =========================================================
# DELETE USER
# ADMIN ONLY
# =========================================================

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):

    try:

        cursor = db.cursor(dictionary=True)

        # Check whether user exists
        cursor.execute(
            """
            SELECT id, name, email, role
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:

            cursor.close()

            return jsonify({
                "message": "User not found"
            }), 404

        # Delete user
        cursor.execute(
            """
            DELETE FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        db.commit()

        cursor.close()

        return jsonify({
            "message": "User deleted successfully",
            "user": user
        }), 200

    except mysql.connector.Error:
        return jsonify({
            "message": "Database error"
        }), 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)