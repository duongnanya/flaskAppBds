from datetime import datetime
from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, text
from config import Config
from decorators import admin_required
from models import Post, Category, User, db
from common import get_categories, get_statuses

post_bp = Blueprint("post", __name__)


@post_bp.route("/post_list")
@login_required
def post_list():
    # Xử lý logic hiển thị danh sách bài viết
    if current_user.role_id == Config.ROLE_ADMIN or current_user.role_id == Config.ROLE_EDITOR:
        # Hiển thị trang danh sách bài viết cho admin/editor
        posts = Post.query.filter_by(del_flg=False).order_by(Post.id.asc()).all()
        post_data = get_post_data(posts)
        return render_template("post-list.html", post_data=post_data)
    else:
        # Lấy danh sách bài viết có trạng thái đã đăng
        posts = Post.query.filter_by(status_id=Config.STATUS_PUBLISHED, del_flg=False).all()
        post_data = get_post_data(posts)
        return render_template("outside/os-post-list.html", post_data=post_data)


@post_bp.route("/post_detail/<int:post_id>")
@login_required
def post_detail(post_id):
    post = get_post_by_id(post_id)

    if current_user.role_id == Config.ROLE_ADMIN or current_user.role_id == Config.ROLE_EDITOR:
        # Hiển thị trang post-detail.html cho admin/editor
        return render_template("post-detail.html", post=post)
    else:
        # Hiển thị trang os-post-detail.html cho người dùng có Role = 3
        return render_template("outside/os-post-detail.html", post=post)


@post_bp.route("/post_add_edit", methods=["GET", "POST"])
@login_required
def post_add_edit():
    post_id = request.args.get("post_id")
    post = get_post_by_id(post_id) if post_id else None
    categories = get_categories()
    statuses = get_statuses()  # Lấy danh sách các trạng thái từ database

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category_id = request.form.get("category")
        status_id = request.form.get("status")

        if post:
            post.title = title
            post.content = content
            post.category_id = category_id
            post.status_id = status_id
            post.update_user_id = current_user.id

            # Kiểm tra trạng thái mới của bài viết
            if str(status_id) == str(Config.STATUS_PUBLISHED):
                post.published_dt = datetime.now()
            else:
                post.published_dt = None
        else:
            new_post = Post(
                title=title,
                content=content,
                category_id=category_id,
                status_id=status_id,
                create_user_id=current_user.id,
                update_user_id=current_user.id,
            )

            # Nếu trạng thái là PUBLISHED, thiết lập published_dt
            if str(status_id) == str(Config.STATUS_PUBLISHED):
                new_post.published_dt = datetime.now()

            db.session.add(new_post)
            db.session.flush()  # Flush để lấy id của new_post

        db.session.commit()
        return redirect(url_for("post.post_list"))

    return render_template("post-add-edit.html", post=post, categories=categories, statuses=statuses)


@post_bp.route("/post_delete/<int:post_id>")
@login_required
@admin_required
def post_delete(post_id):
    post = get_post_by_id(post_id)
    if post:
        post.del_flg = True
        db.session.commit()
    return redirect("/post_list")


@post_bp.route("/post_search", methods=["POST"])
@login_required
def post_search():
    search_keyword = request.form.get("search_keyword")
    posts = (
        Post.query.filter(
            Post.title.ilike(f"%{search_keyword}%") | Post.content.ilike(f"%{search_keyword}%"),
            Post.del_flg == False
        )
        .order_by(Post.id.asc())
        .all()
    )
    post_data = get_post_data(posts)
    return render_template("post-list.html", post_data=post_data, search_keyword=search_keyword)


def get_post_by_id(post_id):
    post = Post.query.filter_by(id=post_id, del_flg=False).first()
    return post


def get_post_data(posts):
    post_data = []
    for post in posts:
        post_data.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "category_id": post.category_id,
            "category_name": post.category.name,
            "status_id": post.status_id,
            "status_name": post.status.name,
            "published_dt": post.published_dt,
            "create_dt": post.create_dt,
            "create_user_name": post.create_user.name,
            "update_dt": post.update_dt,
            "update_user_name": post.update_user.name,
            "del_flg": post.del_flg
        })
    return post_data