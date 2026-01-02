# Productivity Tool API

A Flask backend API that provides full user authentication and a user-owned productivity resource (notes). Users can sign up, log in, and manage their own notes securely.

## Features
- Session-based authentication
- Secure password hashing with bcrypt
- User-owned notes resource
- Full CRUD for notes
- Pagination on notes index
- Route protection (users can only access their own data)

## Installation

```bash
pipenv install
pipenv shell
cd server
flask db init
flask db migrate
flask db upgrade
python seed.py
