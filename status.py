from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from decorators import admin_required
from models import Status, db

status_bp = Blueprint("status", __name__)


@status_bp.route("/status_list", methods=["GET", "POST"])
@login_required
@admin_required
def status_list():
    if request.method == "POST":
        search_keyword = request.form.get("search_keyword")
        if search_keyword:
            statuses = (
                Status.query.filter(
                    (Status.name.ilike(f"%{search_keyword}%")) | 
                    (Status.description.ilike(f"%{search_keyword}%")),
                    Status.del_flg == False
                )
                .order_by(Status.id.asc())
                .all()
            )
            return render_template(
                "status-list.html", statuses=statuses, search_keyword=search_keyword
            )
        else:
            return redirect(url_for("status.status_list"), code=303)  # Redirect if no search term
    else:
        statuses = Status.query.filter_by(del_flg=False).order_by(Status.id.asc()).all()
        return render_template("status-list.html", statuses=statuses)


@status_bp.route("/status_detail/<int:status_id>")
@login_required
@admin_required
def status_detail(status_id):
    status = get_status_by_id(status_id)
    return render_template("status-detail.html", status=status)


@status_bp.route("/status_add_edit", methods=["GET", "POST"])
@login_required
@admin_required
def status_add_edit():
    status_id = request.args.get("status_id")
    status = get_status_by_id(status_id) if status_id else None

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if status:
            status.name = name
            status.description = description
            status.update_user_id = current_user.id
        else:
            new_status = Status(
                name=name,
                description=description,
                create_user_id=current_user.id,
                update_user_id=current_user.id,
            )
            db.session.add(new_status)
            db.session.flush()  # Flush để lấy id của new_status

        db.session.commit()
        return redirect(url_for("status.status_list"))

    return render_template("status-add-edit.html", status=status)


@status_bp.route("/status_delete/<int:status_id>")
@login_required
@admin_required
def status_delete(status_id):
    status = get_status_by_id(status_id)
    if status:
        status.del_flg = True
        db.session.commit()
    return redirect("/status_list")


@status_bp.route("/status_search", methods=["GET", "POST"])
@login_required
@admin_required
def status_search():
    if request.method == "POST":
        search_keyword = request.form.get("search_keyword")
        statuses = (
            Status.query.filter(
                Status.name.ilike(f"%{search_keyword}%"), Status.del_flg == False
            )
            .order_by(Status.id.asc())
            .all()
        )
        return render_template(
            "status-list.html", statuses=statuses, search_keyword=search_keyword
        )

    return redirect(url_for("status.status_list"), code=303)


def get_status_by_id(status_id):
    status = Status.query.filter_by(id=status_id, del_flg=False).first()
    return status

def get_statuses():
    statuses = Status.query.filter_by(del_flg=False).all()
    return statuses