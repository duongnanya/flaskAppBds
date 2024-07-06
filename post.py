from datetime import datetime
from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, text
from config import Config
from decorators import *
from models import Post, Category, User, db
from common import get_categories, get_statuses

post_bp = Blueprint("post", __name__)


@post_bp.route("/post_list", methods=["GET", "POST"])
def post_list():
    if user_is_auth():
        if user_is_admin_editor():
            if request.method == "POST":
                search_keyword = request.form.get("search_keyword")
                exact_search = request.form.get("exact_search") is not None

                query = Post.query.filter_by(del_flg=False)  # Use Post.query instead of Bds.query

                if search_keyword:
                    if exact_search:
                        query = query.filter(
                            Post.title.ilike(f"%{search_keyword}%")
                            | Post.content.ilike(f"%{search_keyword}%")
                        )
                        post_data = get_post_data(query)  # Use get_post_data instead of get_bds_data
                    else:
                        post_data = []
                        sub_keywords = search_keyword.split()
                        for i in range(len(sub_keywords), 0, -1):
                            for j in range(0, len(sub_keywords) - i + 1):
                                sub_keyword = " ".join(sub_keywords[j : j + i])
                                query = Post.query.filter_by(del_flg=False).filter(
                                    Post.title.ilike(f"%{sub_keyword}%")
                                    | Post.content.ilike(f"%{sub_keyword}%")
                                )
                                post_data.extend(get_post_data(query))  # Use get_post_data

                        # Lọc ra những Post không bị trùng
                        post_data = list({post["post"].id: post for post in post_data}.values())

                        # Sắp xếp kết quả theo độ chính xác giảm dần
                        post_data = sorted(
                            post_data,
                            key=lambda x: -len(x["post"].title.split())
                            + -len(x["post"].content.split()),
                        )

                else:
                    post_data = get_post_data(query)  # Use get_post_data

                return render_template(
                    "post-list.html",
                    post_data=post_data,
                    search_keyword=search_keyword,
                    exact_search=exact_search,
                )
            else:
                # Xử lý logic hiển thị danh sách bài viết
                posts = Post.query.filter_by(del_flg=False).order_by(Post.id.asc()).all()
                post_data = get_post_data(posts)
                return render_template("post-list.html", post_data=post_data)
        else:
            # Hiển thị trang outside nếu Role = User
            return redirect(url_for("post.os_post_list"))  # Use post.os_post_list
    else:
        flash(Config.MSG_LOGIN_REQUIRED)
        return redirect(url_for("login"))


@post_bp.route("/post_detail/<int:post_id>")
def post_detail(post_id):
    post = get_post_by_id(post_id)

    if user_is_auth():
        if user_is_admin_editor():
            # Hiển thị trang post-detail.html cho admin/editor
            return render_template("post-detail.html", post=post)
    
    # Hiển thị trang os-post-detail.html cho người dùng có Role = 3 hoặc chưa đăng nhập
    return render_template("outside/os-post-detail.html", post=post)


@post_bp.route("/post_add_edit", methods=["GET", "POST"])
@login_required
@admin_editor_required
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
@admin_editor_required
def post_delete(post_id):
    post = get_post_by_id(post_id)
    if post:
        post.del_flg = True
        db.session.commit()
    return redirect("/post_list")


@post_bp.route("/os_post_list", methods=["GET", "POST"])
def os_post_list():
    # Xử lý logic hiển thị danh sách bài viết
    posts = Post.query.filter_by(
        status_id=Config.STATUS_PUBLISHED, 
        del_flg=False
    ).order_by(Post.id.asc()).all()
    post_data = get_post_data(posts)

    return render_template("outside/os-post-list.html", post_data=post_data)


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