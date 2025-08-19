from app import app, db

if __name__ == "__main__":
    # Ensure the app context is active for database initialization
    with app.app_context():
        db.create_all()
    app.run(debug=True)
