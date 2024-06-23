from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from decorators import *
from models import Role, User, db

user_bp = Blueprint("user", __name__)


@user_bp.route("/user_list")
@login_required
@admin_required
def user_list():
    users = User.query.filter_by(del_flg=False).order_by(User.id.asc()).all()
    return render_template("user-list.html", users=users)


@user_bp.route("/user_detail/<int:user_id>")
@login_required
def user_detail(user_id):
    user = get_user_by_id(user_id)
    return render_template("user-detail.html", user=user)


@user_bp.route("/user_add_edit", methods=["GET", "POST"])
@login_required
def user_add_edit():
    user_id = request.args.get("user_id")
    user = get_user_by_id(user_id) if user_id else None
    roles = Role.query.all()

    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        role_id = request.form.get("role")

        if user:
            user.name = name
            user.username = username
            user.password = password
            user.role_id = role_id
            user.update_user_id = current_user.id
        else:
            new_user = User(
                name=name,
                username=username,
                password=password,
                role_id=role_id,
                created_user_id=current_user.id,
                update_user_id=current_user.id,
            )
            db.session.add(new_user)
            db.session.flush()  # Flush để lấy id của new_user

        db.session.commit()
        return redirect(url_for("user.user_list"))

    return render_template("user-add-edit.html", user=user, roles=roles)


@user_bp.route("/user_delete/<int:user_id>")
@login_required
def user_delete(user_id):
    user = get_user_by_id(user_id)
    if user:
        user.del_flg = True
        db.session.commit()
    return redirect("/user_list")


@user_bp.route("/user_search", methods=["GET", "POST"])
@login_required
def user_search():
    if request.method == "POST":
        search_keyword = request.form.get("search_keyword")
        users = (
            User.query.filter(
                User.name.ilike(f"%{search_keyword}%"), User.del_flg == False
            )
            .order_by(User.id.asc())
            .all()
        )
        return render_template(
            "user-list.html", users=users, search_keyword=search_keyword
        )

    return redirect(url_for("user.user_list"), code=303)


def get_user_by_id(user_id):
    user = User.query.filter_by(id=user_id, del_flg=False).first()
    return user
