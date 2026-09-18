# Secure User Management REST API

A secure RESTful backend API developed using Python Flask and MySQL.

## Project Overview

This project implements a secure User Management REST API using Flask and MySQL. It demonstrates REST principles, CRUD operations, JSON communication, authentication, authorization, input validation, password hashing, database integration, and appropriate HTTP status codes.

The API follows the Input → Process → Output (IPO) model.

## IPO Model

Input → Client sends HTTP request with JSON data

Process → Flask validates the request, authenticates the user, checks authorization, and communicates with MySQL

Output → JSON response + HTTP status code

## Features

- User registration
- User login
- JWT authentication
- Role-based authorization
- Admin and user roles
- Password hashing
- CRUD operations
- JSON request and response handling
- Input validation
- MySQL database integration
- Parameterized SQL queries
- Error handling
- Appropriate HTTP status codes
- Protected API endpoints

## Technologies

- Python
- Flask
- MySQL
- Flask-JWT-Extended
- mysql-connector-python
- Werkzeug
- Postman
- Visual Studio Code

## API Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/` | API welcome | None |
| GET | `/api/status` | Check API status | None |
| POST | `/api/auth/register` | Register a new user | None |
| POST | `/api/auth/login` | Login and receive JWT | None |
| GET | `/api/profile` | Get authenticated profile | JWT |
| GET | `/api/users` | Get all users | Admin |
| POST | `/api/users` | Create a user | Admin |
| GET | `/api/users/<id>` | Get a specific user | Admin |
| PUT | `/api/users/<id>` | Update a user | Admin |
| DELETE | `/api/users/<id>` | Delete a user | Admin |

## Authentication

The API uses JSON Web Tokens (JWT) for authentication.

After successful login, the API returns an access token.

The token is sent in the request header:

Authorization: Bearer <JWT_TOKEN>

Protected endpoints require a valid JWT.

## Authorization

The system implements role-based authorization.

### User

A normal authenticated user can access user-level protected functionality.

### Admin

An administrator can manage users through the admin-protected CRUD endpoints.

Unauthorized users are rejected from protected endpoints.

## Security

The project implements several security practices:

- Passwords are stored using secure password hashing.
- JWT is used for authentication.
- Role-based authorization protects administrative endpoints.
- User input is validated before processing.
- Parameterized SQL queries are used to reduce SQL injection risk.
- Password hashes are not returned in API responses.
- Protected endpoints require authentication.

## HTTP Status Codes

The API uses appropriate HTTP status codes:

| Status Code | Meaning |
|---|---|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 500 | Internal Server Error |

## Database

Database name:

secure_user_api

Main table:

users

The users table contains:

- id
- name
- email
- password_hash
- role

## Architecture

Client / Postman
        |
        | HTTP + JSON
        ↓
Flask REST API
        |
        | Validation
        | Authentication
        | Authorization
        | Business Logic
        ↓
MySQL Database

## REST Operations

### Create

POST /api/users

### Read

GET /api/users
GET /api/users/<id>

### Update

PUT /api/users/<id>

### Delete

DELETE /api/users/<id>

## Testing

The API was tested using Postman.

The following functionality was tested:

- User registration
- User login
- JWT token generation
- Authenticated profile access
- Create user
- Get all users
- Get individual user
- Update user
- Delete user
- Missing authentication → 401 Unauthorized
- Non-admin accessing admin endpoint → 403 Forbidden
- User not found → 404 Not Found
- Duplicate email → 409 Conflict

## Installation

Clone the repository:

git clone <YOUR_REPOSITORY_URL>

Enter the project directory:

cd SecureUserAPI

Create a virtual environment:

python -m venv env

Activate the environment on Windows:

env\Scripts\activate

Install dependencies:

pip install -r requirements.txt

## Database Setup

Create the database in MySQL:

CREATE DATABASE secure_user_api;

Select the database:

USE secure_user_api;

Create the users table:

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NULL,
    role ENUM('user', 'admin') NOT NULL DEFAULT 'user'
);

## Running the Application

Run the Flask application:

python app.py

The API will be available at:

http://127.0.0.1:5000

## Stateless Authentication

JWT authentication allows the server to authenticate requests using the token supplied by the client. The server does not need to maintain a traditional login session for each client.

## Resilience and Scalability

For a production environment, the API could be extended with:

- API Gateway
- Rate limiting
- Centralized error handling
- Logging and monitoring
- Database connection pooling
- Circuit breaker pattern
- Environment-based configuration
- Cloud deployment

These are identified as future production improvements and are not claimed as implemented components of the current academic project.

## Project Status

Functional Academic Project

The project successfully implements and demonstrates the core requirements of a secure RESTful API, including CRUD operations, JWT authentication, role-based authorization, MySQL database integration, input validation, password hashing, and error handling.

The implemented features have been tested using Postman.

## Author

Muhammad Imran