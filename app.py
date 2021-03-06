from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, ValidationError, Length
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 2

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False, unique = True)
    password = db.Column(db.String(80), nullable = False)

class Todo(db.Model) :
    id_todo = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    body = db.Column(db.Boolean)
    texte = db.Column(db.String(100))
    date_todo = db.Column(db.DateTime)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min = 4, max = 20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username = username.data).first()

        if existing_user_username:
            raise ValidationError(
                "That Username Already exists. Please Choose a Different One.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min = 4, max = 20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min = 4, max = 20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'post'])
@login_required
def dashboard():
    todo_list = Todo.query.all()
    return render_template('dashboard.html', todo_list = todo_list)



@app.route("/add", methods =  ["POST"])
def add():
    # add new todo
    title = request.form.get("title")
    texte = request.form.get("texte")
    date_todo = request.form.get("date_todo")
    new_todo = Todo(title = title , body = False, texte = texte, date_todo = date_todo )
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/update/<int:todo_id_todo>")
def update(todo_id_todo):
    # update todo
    todo = Todo.query.filter_by(id_todo=todo_id_todo).first()
    todo.body = not todo.body
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/delete/<int:todo_id_todo>")
def delete(todo_id_todo):
    # delete todo
    todo = Todo.query.filter_by(id_todo=todo_id_todo).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route('/logout', methods = ['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username = form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form= form)


if __name__ == '__main__':
    db.create_all()   #2
    app.run(debug=True)
