from flask import request, session, jsonify
from sqlalchemy import desc

from config import create_app, db
from models import User, Note

app = create_app()

# ---------- helpers ----------
def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)

def login_required():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    return user

# ---------- auth routes ----------
@app.post("/signup")
def signup():
    data = request.get_json() or {}

    try:
        user = User(username=data.get("username", ""))
        user.password_hash = data.get("password", "")
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 422

    session["user_id"] = user.id
    return jsonify(user.to_dict()), 201


@app.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")

    user = User.query.filter(User.username == username).first()
    if not user or not user.authenticate(password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user.id
    return jsonify(user.to_dict()), 200


@app.delete("/logout")
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"}), 204


@app.get("/check_session")
def check_session():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(user.to_dict()), 200


# ---------- notes routes (protected) ----------
@app.get("/notes")
def notes_index():
    user = login_required()
    if isinstance(user, tuple):
        return user  # unauthorized response

    # pagination
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    per_page = max(1, min(per_page, 50))  # clamp

    query = Note.query.filter_by(user_id=user.id).order_by(desc(Note.created_at))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "data": [n.to_dict() for n in pagination.items],
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }), 200


@app.post("/notes")
def notes_create():
    user = login_required()
    if isinstance(user, tuple):
        return user

    data = request.get_json() or {}
    try:
        note = Note(
            title=data.get("title", ""),
            content=data.get("content", ""),
            user_id=user.id
        )
        db.session.add(note)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 422

    return jsonify(note.to_dict()), 201


@app.patch("/notes/<int:id>")
def notes_update(id):
    user = login_required()
    if isinstance(user, tuple):
        return user

    note = db.session.get(Note, id)
    if not note or note.user_id != user.id:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json() or {}
    try:
        if "title" in data:
            note.title = data["title"]
        if "content" in data:
            note.content = data["content"]
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 422

    return jsonify(note.to_dict()), 200


@app.delete("/notes/<int:id>")
def notes_delete(id):
    user = login_required()
    if isinstance(user, tuple):
        return user

    note = db.session.get(Note, id)
    if not note or note.user_id != user.id:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 204


if __name__ == "__main__":
    app.run(port=5555, debug=True)
