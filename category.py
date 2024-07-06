from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from decorators import admin_required
from models import Category, db

category_bp = Blueprint("category", __name__)


@category_bp.route("/category_list", methods=["GET", "POST"])
@login_required
@admin_required
def category_list():
    if request.method == "POST":
        search_keyword = request.form.get("search_keyword")
        if search_keyword:
            categories = (
                Category.query.filter(
                    (Category.name.ilike(f"%{search_keyword}%")) | 
                    (Category.description.ilike(f"%{search_keyword}%")),
                    Category.del_flg == False
                )
                .order_by(Category.id.asc())
                .all()
            )
            return render_template(
                "category-list.html", categories=categories, search_keyword=search_keyword
            )
        else:
            return redirect(url_for("category.category_list"), code=303)  # Redirect if no search term
    else:
        categories = Category.query.filter_by(del_flg=False).order_by(Category.id.asc()).all()
        return render_template("category-list.html", categories=categories)


@category_bp.route("/category_detail/<int:category_id>")
@login_required
@admin_required
def category_detail(category_id):
    category = get_category_by_id(category_id)
    return render_template("category-detail.html", category=category)


@category_bp.route("/category_add_edit", methods=["GET", "POST"])
@login_required
@admin_required
def category_add_edit():
    category_id = request.args.get("category_id")
    category = get_category_by_id(category_id) if category_id else None

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if category:
            category.name = name
            category.description = description
            category.update_user_id = current_user.id
        else:
            new_category = Category(
                name=name,
                description=description,
                create_user_id=current_user.id,
                update_user_id=current_user.id,
            )
            db.session.add(new_category)
            db.session.flush()  # Flush untuk mendapatkan id dari new_category

        db.session.commit()
        return redirect(url_for("category.category_list"))

    return render_template("category-add-edit.html", category=category)


@category_bp.route("/category_delete/<int:category_id>")
@login_required
@admin_required
def category_delete(category_id):
    category = get_category_by_id(category_id)
    if category:
        category.del_flg = True
        db.session.commit()
    return redirect("/category_list")


def get_category_by_id(category_id):
    category = Category.query.filter_by(id=category_id, del_flg=False).first()
    return category

def get_categories():
    categories = Category.query.filter_by(del_flg=False).all()
    return categories