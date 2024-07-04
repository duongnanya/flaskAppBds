import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import User, db
from config import Config

# Blueprint
from user import user_bp
from bds import bds_bp
from common import common_bp
from contact import contact_bp
from category import category_bp
from post import post_bp
from status import status_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    flash("Bạn cần đăng nhập để truy cập trang này.")
    return redirect(url_for("login"))


# Blueprint
app.register_blueprint(user_bp)
app.register_blueprint(bds_bp)
app.register_blueprint(common_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(category_bp)
app.register_blueprint(post_bp)
app.register_blueprint(status_bp)

# Đường dẫn thư mục gốc của ứng dụng
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Tạo đường dẫn cho thư mục lưu trữ các file ảnh tải lên
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
# Thiết lập đường dẫn thư mục lưu trữ
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".gif"]


@app.route("/home")
def home():
    return render_template("home.html", Config=Config)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()
        if user is None:
            return redirect(url_for("login"))
        else:
            session["logged_in"] = True
            login_user(user)
            if user.role_id == Config.ROLE_ADMIN:
                return redirect(url_for("user.user_list"))
            else:
                return redirect(url_for("bds.bds_list"))
    else:
        return render_template("login.html", Config=Config)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    session.pop("logged_in", None)
    return redirect(url_for("home"))


# Tạo context processor
# 参考サイト：https://poe.com/s/mCo17QrfEpbwclU6tWUx
@app.context_processor
def inject_config():
    return dict(Config=Config)


# format datetime để sử dụng ở html
# 参考サイト：https://poe.com/s/qqL5P2Br39OZfU2J83gC
def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    if value is None:
        return ""
    return value.strftime(format)


app.jinja_env.filters["datetime"] = format_datetime


if __name__ == "__main__":
    app.run()
