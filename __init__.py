from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'a3951e50d6e90d5f173e522e3e623731'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)
manager = LoginManager(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, title, intro, text):
        self.title = title
        self.intro = intro
        self.text = text

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

@manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route('/')
def index():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("index.html", articles=articles)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if not current_user.is_authenticated:
        flash("Войдите в аккаунт", 'danger')
        return redirect('/login')
    if not current_user.admin:
        flash("Данная функция доступна только администратору", 'danger')
        return redirect("/")
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        article = Article(title, intro, text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/')
        except:
            return "При добавлении произошла ошибка"
    return render_template("add.html")

@app.route('/post/<int:id>')
def post(id):
    article = db.session.get(Article, id)
    return render_template("post.html", article=article)

@app.route('/post/<int:id>/del')
def post_del(id):
    if not current_user.is_authenticated:
        flash("Войдите в аккаунт", 'danger')
        return redirect('/login')
    if not current_user.admin:
        flash("Данная функция доступна только администратору", 'danger')
        return redirect("/")
    article = db.session.get(Article, id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/')
    except:
        return "При удалении статьи произошла ошибка"

@app.route('/post/<int:id>/update', methods=['GET', 'POST'])
def post_update(id):
    if not current_user.is_authenticated:
        flash("Войдите в аккаунт", 'danger')
        return redirect('/login')
    if not current_user.admin:
        flash("Данная функция доступна только администратору", 'danger')
        return redirect("/")
    article = Article.query.get(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "При редактировании произошла ошибка"
    return render_template("post_update.html", article=article)

@app.route('/registration', methods=["POST", "GET"])
def registration():
    if request.method == "GET":
        return render_template("registration.html")
    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    user = User.query.filter_by(username=username).first()
    if user:
        flash('Имя пользователя занято!', 'danger')
        return redirect("/registration")
    if password2 != password:
        flash('Пароли не совпадают!', 'danger')
        return redirect("/registration")
    hash_pwd = generate_password_hash(password)
    new_user = User(username, hash_pwd)
    db.session.add(new_user)
    db.session.commit()
    flash("Регистрация прошла успешно!", 'success')
    return redirect("/")
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if current_user.is_authenticated:
            flash("Вы уже авторизованы", 'warning')
            return redirect("/")
        return render_template("login.html")
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Такого пользователя не существует', 'danger')
        return redirect("/login")
    if check_password_hash(user.password, password):
        login_user(user)
        return redirect('/')
    flash("Неверный логин или пароль!", 'danger')
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")

from api import init_api
# Подключаем REST API в отдельном модуле.
# Модели Article/User передаем параметрами, чтобы не было циклических импортов.
init_api(app, db, Article, User)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
