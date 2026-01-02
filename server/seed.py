from config import create_app, db
from models import User, Note

app = create_app()

with app.app_context():
    print("Seeding...")

    Note.query.delete()
    User.query.delete()

    u1 = User(username="steven")
    u1.password_hash = "password123"

    u2 = User(username="jenn")
    u2.password_hash = "password123"

    db.session.add_all([u1, u2])
    db.session.commit()

    notes = [
        Note(title="Groceries", content="Eggs, milk, coffee", user_id=u1.id),
        Note(title="Workout plan", content="Squats, bench, row", user_id=u1.id),
        Note(title="Ideas", content="Build a notes app", user_id=u2.id),
    ]
    db.session.add_all(notes)
    db.session.commit()