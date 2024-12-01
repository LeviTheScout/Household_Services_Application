from app import app
app.config['SECRET_KEY'] = "this-is-my-seceret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
