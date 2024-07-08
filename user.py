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
from models import Bds, BdsUserRelation, Role, User, db

user_bp = Blueprint("user", __name__)


@user_bp.route("/user_list", methods=["GET", "POST"])
@login_required
@admin_required
def user_list():
    if request.method == "POST":
        search_keyword = request.form.get("search_keyword")
        if search_keyword:
            users = (
                User.query.filter(
                    (User.name.ilike(f"%{search_keyword}%"))
                    | (User.username.ilike(f"%{search_keyword}%"))
                    | (User.email.ilike(f"%{search_keyword}%"))
                    | (User.need.ilike(f"%{search_keyword}%"))
                    | (User.phone.ilike(f"%{search_keyword}%")),
                    User.del_flg == False,
                )
                .order_by(User.id.asc())
                .all()
            )
            return render_template(
                "user-list.html", users=users, search_keyword=search_keyword
            )
        else:
            return redirect(url_for("user.user_list"), code=303)  # Redirect if no search term
    else:
        users = User.query.filter_by(del_flg=False).order_by(User.id.asc()).all()
        return render_template("user-list.html", users=users)


@user_bp.route("/user_detail/<int:user_id>")
@login_required
def user_detail(user_id):
    user = get_user_by_id(user_id)

    # Fetch saved properties for the user (include the title)
    saved_bds = (
        BdsUserRelation.query.filter_by(user_id=user.id, del_flg=False)
        .join(Bds)
        .with_entities(Bds.id, Bds.title)  # Include the title in the query
        .all()
    )

    if user_is_admin_editor():
        return render_template("user-detail.html", user=user)
    else:
        return render_template("outside/os-user-detail.html", user=user, saved_bds=saved_bds)


@user_bp.route("/user_add_edit", methods=["GET", "POST"])
@login_required
def user_add_edit():
    user_id = request.args.get("user_id")
    user = get_user_by_id(user_id) if user_id else None
    roles = Role.query.all()

    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        phone = request.form.get("phone")
        # TODOdnn: password xử lý phức tạp (cần xác nhận), nên mục này để sau
        # password = request.form.get("password")   
        # khởi tạo giá trị mặc định, gán giá trị bên dưới, tùy quyền User
        role_id = 0
        need = ''

        if not user_is_admin_editor():
            need = request.form.get("need")

        if user_is_admin_editor():
            role_id = request.form.get("role")

        if user:
            user.name = name
            user.username = username
            # user.password = password
            user.role_id = role_id
            user.need = need
            user.phone = phone
            user.update_user_id = current_user.id
        else:
            new_user = User(
                name=name,
                username=username,
                # password=password,
                role_id=role_id,
                need = need,
                phone = phone,
                create_user_id=current_user.id,
                update_user_id=current_user.id,
            )
            db.session.add(new_user)
            db.session.flush()  # Flush để lấy id của new_user

        db.session.commit()

        if user_is_admin_editor():
            return redirect(url_for("user.user_list"))
        else:
            # Return the detail of the newly created or updated user
            return redirect(url_for("user.user_detail", user_id=user.id if user else new_user.id))
        
    if user_is_admin_editor():
        return render_template("user-add-edit.html", user=user, roles=roles)
    else:
        return render_template("outside/os-user-add-edit.html", user=user)


@user_bp.route("/user_delete/<int:user_id>")
@login_required
@admin_required
def user_delete(user_id):
    user = get_user_by_id(user_id)
    if user:
        user.del_flg = True
        db.session.commit()
    return redirect("/user_list")


def get_user_by_id(user_id):
    user = User.query.filter_by(id=user_id, del_flg=False).first()
    return user
